"""Reglas de negocio del módulo de objetos (RF03, RF04, RF05, RF20, RF25, RF26, RF28, RF29)."""

from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import config, fotos
from app.errores import AccionNoPermitida, DatoInvalido, NoEncontrado
from app.models import Encargado, EstadoObjeto, Objeto, Persona, TipoRegistro, ahora
from app.schemas.comparacion import Coincidencia
from app.schemas.objetos import ObjetoEditar, ObjetoEncontradoCrear, ObjetoPerdidoCrear
from app.schemas.reclamaciones import ObjetoComparacion
from app.services import historial_service

# Campos que solo aplican a un tipo de registro.
_SOLO_PERDIDO = {"fecha_reporte"}
_SOLO_ENCONTRADO = {"fecha_encontrado", "lugar_encontrado"}


def vencer_reportes(db: Session) -> int:
    """
    Marca como VENCIDO todo reporte de pérdida abierto que lleve más de
    DIAS_VIGENCIA_REPORTE días registrado (RF29). Devuelve cuántos venció.

    Es un vencimiento "perezoso": no hay un proceso programado que corra cada
    día. El sistema actualiza los reportes vencidos justo antes de consultar
    objetos o de vincular un reporte, así el estado siempre está al día cuando
    alguien lo mira. Los reportes vencidos no se borran: quedan como evidencia.
    """
    limite = ahora() - timedelta(days=config.DIAS_VIGENCIA_REPORTE)
    resultado = db.execute(
        update(Objeto)
        .where(
            Objeto.tipo_registro == TipoRegistro.PERDIDO,
            Objeto.estado == EstadoObjeto.PERDIDO,
            Objeto.fecha_registro < limite,
        )
        .values(estado=EstadoObjeto.VENCIDO)
    )
    if resultado.rowcount:
        db.commit()
    return resultado.rowcount


def registrar_perdido(db: Session, datos: ObjetoPerdidoCrear, encargado: Encargado) -> Objeto:
    """
    Registra un objeto reportado como perdido (RF03, HCU03).
    La persona debe existir. El estado lo asigna el sistema: PERDIDO.
    """
    if db.get(Persona, datos.persona_id) is None:
        raise DatoInvalido(f"No existe una persona con id {datos.persona_id}. Regístrala primero.")

    objeto = Objeto(
        tipo_registro=TipoRegistro.PERDIDO,
        estado=EstadoObjeto.PERDIDO,
        persona_id=datos.persona_id,
        tipo=datos.tipo,
        descripcion=datos.descripcion,
        caracteristicas=datos.caracteristicas,
        fecha_reporte=datos.fecha_reporte or date.today(),
        encargado_id=encargado.id,
    )
    db.add(objeto)
    db.commit()
    db.refresh(objeto)
    return objeto


def registrar_encontrado(db: Session, datos: ObjetoEncontradoCrear, encargado: Encargado) -> Objeto:
    """
    Registra un objeto encontrado (RF04, HCU04).
    El estado lo asigna el sistema: DISPONIBLE, listo para ser reclamado.
    """
    objeto = Objeto(
        tipo_registro=TipoRegistro.ENCONTRADO,
        estado=EstadoObjeto.DISPONIBLE,
        **datos.model_dump(),
        encargado_id=encargado.id,
    )
    db.add(objeto)
    db.commit()
    db.refresh(objeto)
    return objeto


def listar(
    db: Session,
    tipo_registro: TipoRegistro | None = None,
    estado: EstadoObjeto | None = None,
    tipo: str | None = None,
    buscar: str | None = None,
) -> list[Objeto]:
    """
    Consulta los objetos registrados, del más reciente al más antiguo (RF05, HCU05).
    Antes de consultar, vence los reportes que pasaron su vigencia (RF29).
    Filtros opcionales y combinables:
    - tipo_registro: PERDIDO o ENCONTRADO.
    - estado: PERDIDO (reportes abiertos), RECUPERADO, VENCIDO, DISPONIBLE o ENTREGADO.
    - tipo: categoría (coincidencia parcial, sin importar mayúsculas).
    - buscar: texto contenido en la descripción.
    """
    vencer_reportes(db)
    consulta = select(Objeto).order_by(Objeto.fecha_registro.desc(), Objeto.id.desc())
    if tipo_registro is not None:
        consulta = consulta.where(Objeto.tipo_registro == tipo_registro)
    if estado is not None:
        consulta = consulta.where(Objeto.estado == estado)
    if tipo and tipo.strip():
        consulta = consulta.where(Objeto.tipo.ilike(f"%{tipo.strip()}%"))
    if buscar and buscar.strip():
        consulta = consulta.where(Objeto.descripcion.ilike(f"%{buscar.strip()}%"))
    return list(db.scalars(consulta))


def obtener(db: Session, objeto_id: int) -> Objeto:
    vencer_reportes(db)
    objeto = db.get(Objeto, objeto_id)
    if objeto is None:
        raise NoEncontrado(f"No existe un objeto con id {objeto_id}.")
    return objeto


_NO_EDITABLES = {
    EstadoObjeto.ENTREGADO: "El objeto ya fue entregado y no se puede modificar.",
    EstadoObjeto.RECUPERADO: "El reporte ya se cerró porque la persona recuperó su objeto; no se puede modificar.",
    EstadoObjeto.VENCIDO: "El reporte venció y no se puede modificar. Si la persona sigue buscando el objeto, registra un reporte nuevo.",
}


def _verificar_editable(objeto: Objeto) -> None:
    """
    Los registros cerrados (entregado, recuperado o vencido) quedan como
    evidencia y ya no se modifican.
    """
    if objeto.estado in _NO_EDITABLES:
        raise AccionNoPermitida(_NO_EDITABLES[objeto.estado])


def _registrar_modificacion(objeto: Objeto, encargado: Encargado) -> None:
    """Guarda quién hizo el último cambio y cuándo (RF25)."""
    objeto.encargado_modificacion_id = encargado.id
    objeto.fecha_modificacion = ahora()


def editar(db: Session, objeto_id: int, datos: ObjetoEditar, encargado: Encargado) -> Objeto:
    """
    Corrige los datos de un objeto (RF25).
    - Solo cambia los campos enviados.
    - No se puede editar un objeto ENTREGADO.
    - No se pueden enviar campos del otro tipo de registro (por ejemplo,
      lugar_encontrado en un objeto perdido).
    """
    objeto = obtener(db, objeto_id)
    _verificar_editable(objeto)

    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise DatoInvalido("No se envió ningún campo para modificar.")

    no_aplican = _SOLO_ENCONTRADO if objeto.tipo_registro == TipoRegistro.PERDIDO else _SOLO_PERDIDO
    invalidos = sorted(no_aplican & cambios.keys())
    if invalidos:
        tipo = objeto.tipo_registro.value.lower()
        if len(invalidos) == 1:
            raise DatoInvalido(f"El campo {invalidos[0]} no aplica a un objeto {tipo}.")
        raise DatoInvalido(f"Los campos {', '.join(invalidos)} no aplican a un objeto {tipo}.")

    for campo, valor in cambios.items():
        setattr(objeto, campo, valor)
    _registrar_modificacion(objeto, encargado)
    db.commit()
    db.refresh(objeto)
    return objeto


def guardar_foto(db: Session, objeto_id: int, contenido: bytes, encargado: Encargado) -> Objeto:
    """
    Guarda o reemplaza la foto de un objeto (RF20). Si ya tenía una, la anterior
    se borra. Cuenta como modificación del objeto (RF25).
    """
    objeto = obtener(db, objeto_id)
    _verificar_editable(objeto)

    nueva = fotos.guardar_foto(contenido, fotos.CARPETA_OBJETOS)
    anterior = objeto.foto
    objeto.foto = nueva
    _registrar_modificacion(objeto, encargado)
    db.commit()
    fotos.borrar_foto(fotos.CARPETA_OBJETOS, anterior)
    db.refresh(objeto)
    return objeto


def ruta_foto(db: Session, objeto_id: int) -> Path:
    """Ruta del archivo de la foto de un objeto, para enviarlo al frontend."""
    objeto = obtener(db, objeto_id)
    if objeto.foto is None:
        raise NoEncontrado("Este objeto no tiene foto.")
    ruta = fotos.ruta_foto(fotos.CARPETA_OBJETOS, objeto.foto)
    if not ruta.is_file():
        raise NoEncontrado("No se encontró el archivo de la foto en el servidor.")
    return ruta


def _misma_categoria(a: str, b: str) -> bool:
    """
    Compara categorías sin importar mayúsculas: "Calculadora" coincide con
    "calculadora científica" porque una contiene a la otra.
    """
    a, b = a.strip().lower(), b.strip().lower()
    return a in b or b in a


def coincidencias(db: Session, objeto_id: int) -> list[Coincidencia]:
    """
    Posibles coincidencias entre objetos perdidos y encontrados (RF05, HCU05, RF26, RF28).
    Funciona en las dos direcciones y compara por categoría, sin importar
    mayúsculas. La comparación la hace el encargado: el sistema no decide si
    es el mismo objeto.

    - Desde un REPORTE DE PÉRDIDA: muestra los objetos encontrados de la misma
      categoría, primero los disponibles y luego los entregados, cada uno con su
      entrega (a quién, cuándo y qué describió esa persona).
    - Desde un OBJETO ENCONTRADO: muestra los reportes de pérdida ABIERTOS de la
      misma categoría, con la persona que lo reportó para poder contactarla.
      Los reportes vencidos o recuperados no aparecen.

    Como el reporte de pérdida ya tiene la descripción de la persona, mostrar
    aquí las características y la foto no rompe la verificación a ciegas (RF21).
    """
    origen = obtener(db, objeto_id)  # también vence los reportes viejos

    if origen.tipo_registro == TipoRegistro.PERDIDO:
        encontrados = db.scalars(
            select(Objeto)
            .where(Objeto.tipo_registro == TipoRegistro.ENCONTRADO)
            .order_by(Objeto.fecha_registro.desc(), Objeto.id.desc())
        )
        candidatos = [o for o in encontrados if _misma_categoria(o.tipo, origen.tipo)]
        # Primero los disponibles (se pueden reclamar), luego los entregados.
        candidatos.sort(key=lambda o: o.estado != EstadoObjeto.DISPONIBLE)
        return [
            Coincidencia(
                objeto=ObjetoComparacion.model_validate(o),
                entrega_previa=historial_service.entrega_previa(db, o.id),
            )
            for o in candidatos
        ]

    reportes = db.scalars(
        select(Objeto)
        .where(Objeto.tipo_registro == TipoRegistro.PERDIDO, Objeto.estado == EstadoObjeto.PERDIDO)
        .order_by(Objeto.fecha_registro.desc(), Objeto.id.desc())
    )
    return [
        Coincidencia(objeto=ObjetoComparacion.model_validate(r), reportado_por=r.persona)
        for r in reportes
        if _misma_categoria(r.tipo, origen.tipo)
    ]
