"""
Reglas de negocio de reclamaciones, revisión, decisión y entrega
(RF06–RF16, RF21, RF22, RF24, RF26, RF27).

Flujo presencial:
1. La persona llega al mostrador y el encargado registra la reclamación (RF06).
2. La persona describe el objeto SIN verlo; el encargado lo registra (RF07).
3. Solo entonces el sistema muestra la comparación con la foto (RF09, RF21).
4. El encargado aprueba o rechaza con un motivo (RF10–RF14).
5. Si aprobó, entrega el objeto con una foto de evidencia (RF15, RF16, RF22).
   Si la reclamación está vinculada al reporte de pérdida de la persona, ese
   reporte se cierra como RECUPERADO en la misma transacción (RF27).

Si alguien reclama un objeto que YA se entregó a otra persona, la reclamación
se puede registrar para comparar: el sistema muestra quién se lo llevó y qué
describió (RF26). No se puede aprobar, porque el objeto ya no está; si se
comprueba que era de quien reclama ahora, se registra un incidente (RF23).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import fotos
from app.errores import AccionNoPermitida, Conflicto, DatoInvalido, NoEncontrado
from app.models import (
    Decision,
    Encargado,
    Entrega,
    EstadoObjeto,
    EstadoReclamacion,
    InformacionReclamante,
    Objeto,
    Persona,
    Reclamacion,
    ResultadoDecision,
    TipoRegistro,
)
from app.schemas.comparacion import ComparacionOut
from app.schemas.reclamaciones import (
    DecisionCrear,
    InformacionCrear,
    ReclamacionCrear,
    ReclamacionOut,
)
from app.services import alertas_service, historial_service, objetos_service


def obtener(db: Session, reclamacion_id: int) -> Reclamacion:
    reclamacion = db.get(Reclamacion, reclamacion_id)
    if reclamacion is None:
        raise NoEncontrado(f"No existe una reclamación con id {reclamacion_id}.")
    return reclamacion


def _tiene_aprobada(db: Session, objeto_id: int) -> bool:
    return (
        db.scalar(
            select(Reclamacion.id).where(
                Reclamacion.objeto_id == objeto_id,
                Reclamacion.estado == EstadoReclamacion.APROBADA,
            )
        )
        is not None
    )


def _aprobada_sin_entregar(db: Session, objeto: Objeto) -> bool:
    """El objeto tiene una reclamación aprobada y todavía está en la oficina."""
    return objeto.estado == EstadoObjeto.DISPONIBLE and _tiene_aprobada(db, objeto.id)


def con_alerta(db: Session, reclamacion: Reclamacion) -> ReclamacionOut:
    """Convierte la reclamación en respuesta y le agrega la alerta de la persona (RF24)."""
    salida = ReclamacionOut.model_validate(reclamacion)
    salida.alerta = alertas_service.alerta_de(db, reclamacion.persona_id)
    return salida


# ---------------------------------------------------------------------------
# Paso 5: reclamaciones (RF06, RF07, RF08)
# ---------------------------------------------------------------------------


def registrar(db: Session, datos: ReclamacionCrear, encargado: Encargado) -> Reclamacion:
    """
    Registra una reclamación presencial (RF06, HCU06). Nace PENDIENTE.

    Reglas:
    - La persona y el objeto deben existir.
    - Solo se reclaman objetos ENCONTRADOS (no reportes de pérdida).
    - No se reclama un objeto con una reclamación aprobada que aún no se entrega.
    - Sí se puede reclamar un objeto ya ENTREGADO: sirve para comparar con quien
      se lo llevó y detectar un posible fraude (RF26). No se podrá aprobar.
    - Una persona no puede tener dos reclamaciones pendientes del mismo objeto.
    - Si se indica reporte_id (RF27): debe ser un reporte de pérdida ABIERTO de
      esta misma persona. Al entregar, ese reporte pasa a RECUPERADO.
    """
    if db.get(Persona, datos.persona_id) is None:
        raise DatoInvalido(f"No existe una persona con id {datos.persona_id}. Regístrala primero.")
    objeto = db.get(Objeto, datos.objeto_id)
    if objeto is None:
        raise DatoInvalido(f"No existe un objeto con id {datos.objeto_id}.")
    if objeto.tipo_registro != TipoRegistro.ENCONTRADO:
        raise AccionNoPermitida("Solo se pueden reclamar objetos encontrados, no reportes de pérdida.")
    if _aprobada_sin_entregar(db, objeto):
        raise AccionNoPermitida(
            "El objeto ya tiene una reclamación aprobada y está pendiente de entrega. "
            "Entrégalo primero; después se puede registrar esta reclamación para comparar."
        )
    duplicada = db.scalar(
        select(Reclamacion.id).where(
            Reclamacion.persona_id == datos.persona_id,
            Reclamacion.objeto_id == datos.objeto_id,
            Reclamacion.estado == EstadoReclamacion.PENDIENTE,
        )
    )
    if duplicada is not None:
        raise Conflicto(f"Esta persona ya tiene una reclamación pendiente de este objeto (id {duplicada}).")

    if datos.reporte_id is not None:
        _validar_reporte(db, datos.reporte_id, datos.persona_id)

    reclamacion = Reclamacion(
        persona_id=datos.persona_id,
        objeto_id=datos.objeto_id,
        reporte_id=datos.reporte_id,
        encargado_id=encargado.id,
    )
    db.add(reclamacion)
    db.commit()
    db.refresh(reclamacion)
    return reclamacion


def _validar_reporte(db: Session, reporte_id: int, persona_id: int) -> None:
    """El reporte vinculado debe ser un reporte de pérdida abierto de la misma persona (RF27)."""
    objetos_service.vencer_reportes(db)
    reporte = db.get(Objeto, reporte_id)
    if reporte is None or reporte.tipo_registro != TipoRegistro.PERDIDO:
        raise DatoInvalido(f"No existe un reporte de pérdida con id {reporte_id}.")
    if reporte.persona_id != persona_id:
        raise DatoInvalido("Ese reporte de pérdida pertenece a otra persona.")
    if reporte.estado == EstadoObjeto.VENCIDO:
        raise AccionNoPermitida(
            "Ese reporte de pérdida ya venció. Registra la reclamación sin vincularlo, "
            "o registra un reporte nuevo si la persona sigue buscando el objeto."
        )
    if reporte.estado != EstadoObjeto.PERDIDO:
        raise AccionNoPermitida("Ese reporte de pérdida ya está cerrado: la persona recuperó su objeto.")


def registrar_informacion(db: Session, reclamacion_id: int, datos: InformacionCrear) -> Reclamacion:
    """
    Registra lo que la persona describe del objeto (RF07, HCU07).

    Se registra UNA sola vez y no se puede modificar: si se pudiera cambiar
    después de ver la foto en la comparación, la verificación a ciegas no
    serviría (RF21).
    """
    reclamacion = obtener(db, reclamacion_id)
    if reclamacion.estado != EstadoReclamacion.PENDIENTE:
        raise AccionNoPermitida("La reclamación ya fue decidida.")
    if reclamacion.informacion is not None:
        raise Conflicto(
            "La descripción del reclamante ya fue registrada y no se puede modificar, "
            "para que no se ajuste después de ver la foto del objeto."
        )
    db.add(InformacionReclamante(reclamacion_id=reclamacion.id, **datos.model_dump()))
    db.commit()
    db.refresh(reclamacion)
    return reclamacion


def listar(db: Session, estado: EstadoReclamacion | None = EstadoReclamacion.PENDIENTE) -> list[ReclamacionOut]:
    """
    Lista reclamaciones (RF08). Por defecto, las PENDIENTES, de la más antigua
    a la más reciente: así se atiende primero a quien lleva más tiempo esperando.
    Cada una trae la alerta de intentos fallidos de su persona (RF24).
    """
    consulta = select(Reclamacion).order_by(Reclamacion.fecha_creacion, Reclamacion.id)
    if estado is not None:
        consulta = consulta.where(Reclamacion.estado == estado)
    reclamaciones = list(db.scalars(consulta))

    rechazos = alertas_service.rechazos_por_persona(db, {r.persona_id for r in reclamaciones})
    salida = []
    for reclamacion in reclamaciones:
        item = ReclamacionOut.model_validate(reclamacion)
        item.alerta = alertas_service.construir_alerta(rechazos.get(reclamacion.persona_id, 0))
        salida.append(item)
    return salida


# ---------------------------------------------------------------------------
# Paso 6: comparación y decisión (RF09–RF14, RF21)
# ---------------------------------------------------------------------------


def comparacion(db: Session, reclamacion_id: int) -> ComparacionOut:
    """
    Muestra el objeto y la descripción del reclamante lado a lado (RF09, HCU08).

    Solo está disponible después de registrar la descripción del reclamante:
    antes de eso no se muestran ni la foto ni las características (RF21).

    Si el objeto ya se entregó a otra persona, incluye esa entrega: a quién,
    cuándo, qué describió y con qué motivo se aprobó (RF26).
    """
    reclamacion = obtener(db, reclamacion_id)
    if reclamacion.informacion is None:
        raise AccionNoPermitida(
            "Primero registra la descripción del reclamante. La foto y las características "
            "del objeto solo se muestran después, para que la persona no pueda copiarlas."
        )
    previa = historial_service.entrega_previa(
        db, reclamacion.objeto_id, excluir_reclamacion_id=reclamacion.id
    )
    aviso = None
    if previa is not None:
        aviso = (
            f"Este objeto ya se entregó a {previa.persona.nombre} el "
            f"{previa.fecha_hora:%d/%m/%Y a las %H:%M}. Compara la descripción de quien "
            "reclama ahora con la del objeto y con la que dio esa persona. Si concluyes que "
            "el objeto es de quien reclama ahora, registra un incidente en esa entrega "
            "indicándolo como dueño real."
        )
    return ComparacionOut(
        reclamacion_id=reclamacion.id,
        estado=reclamacion.estado,
        fecha_creacion=reclamacion.fecha_creacion,
        persona=reclamacion.persona,
        alerta=alertas_service.alerta_de(db, reclamacion.persona_id),
        descripcion_reclamante=reclamacion.informacion,
        objeto=reclamacion.objeto,
        reporte=reclamacion.reporte,
        decision=reclamacion.decision,
        entrega_previa=previa,
        aviso=aviso,
    )


def decidir(db: Session, reclamacion_id: int, datos: DecisionCrear, encargado: Encargado) -> Reclamacion:
    """
    Registra la decisión manual del encargado (RF10–RF14, HCU09).

    Reglas:
    - Solo se decide sobre reclamaciones PENDIENTES (una sola vez).
    - Debe existir la descripción del reclamante: no se decide sin comparar.
    - El motivo es obligatorio (lo valida el esquema y la base de datos).
    - El encargado (RF13) y la fecha y hora (RF14) los asigna el sistema.
    - Para aprobar, el objeto debe seguir disponible y sin otra reclamación aprobada.
    - Aprobar NO rechaza automáticamente otras reclamaciones del mismo objeto:
      cada una necesita su propia decisión con motivo.
    """
    reclamacion = obtener(db, reclamacion_id)
    if reclamacion.estado != EstadoReclamacion.PENDIENTE:
        raise AccionNoPermitida(f"La reclamación ya fue decidida: está {reclamacion.estado.value}.")
    if reclamacion.informacion is None:
        raise AccionNoPermitida("Registra la descripción del reclamante y revisa la comparación antes de decidir.")
    if datos.resultado == ResultadoDecision.APROBADA:
        if reclamacion.objeto.estado != EstadoObjeto.DISPONIBLE:
            raise AccionNoPermitida(
                "No se puede aprobar: el objeto ya se entregó a otra persona. Si concluyes que es "
                "de quien reclama ahora, registra un incidente en esa entrega con esta persona "
                "como dueño real, y luego cierra esta reclamación como RECHAZADA explicando el motivo."
            )
        if _tiene_aprobada(db, reclamacion.objeto_id):
            raise AccionNoPermitida("El objeto ya tiene otra reclamación aprobada.")

    db.add(
        Decision(
            reclamacion_id=reclamacion.id,
            encargado_id=encargado.id,  # RF13: del token, no del formulario.
            resultado=datos.resultado,
            motivo=datos.motivo,
        )
    )
    reclamacion.estado = EstadoReclamacion(datos.resultado.value)
    db.commit()
    db.refresh(reclamacion)
    return reclamacion


# ---------------------------------------------------------------------------
# Paso 7: entrega (RF15, RF16, RF22)
# ---------------------------------------------------------------------------


def registrar_entrega(
    db: Session,
    reclamacion_id: int,
    foto: bytes,
    observaciones: str | None,
    encargado: Encargado,
) -> Entrega:
    """
    Registra la entrega del objeto (RF15) y lo marca ENTREGADO (RF16).

    - Solo con reclamación APROBADA y sin entrega previa.
    - La foto de la persona con el objeto es obligatoria (RF22).
    - Si la reclamación tiene un reporte de pérdida vinculado, ese reporte pasa
      a RECUPERADO (RF27), aunque haya vencido mientras tanto.
    - La entrega y los cambios de estado se guardan juntos (una transacción):
      si algo falla, no queda nada y se borra la foto guardada.
    """
    reclamacion = obtener(db, reclamacion_id)
    if reclamacion.estado != EstadoReclamacion.APROBADA:
        raise AccionNoPermitida("Solo se puede entregar un objeto cuya reclamación fue aprobada.")
    if reclamacion.entrega is not None:
        raise Conflicto("Esta reclamación ya tiene una entrega registrada.")
    if reclamacion.objeto.estado != EstadoObjeto.DISPONIBLE:
        raise AccionNoPermitida("El objeto ya no está disponible para entregar.")

    nombre_foto = fotos.guardar_foto(foto, fotos.CARPETA_ENTREGAS)
    try:
        entrega = Entrega(
            reclamacion_id=reclamacion.id,
            encargado_id=encargado.id,
            foto_evidencia=nombre_foto,
            observaciones=observaciones,
        )
        db.add(entrega)
        reclamacion.objeto.estado = EstadoObjeto.ENTREGADO
        reporte = reclamacion.reporte
        if reporte is not None and reporte.estado in (EstadoObjeto.PERDIDO, EstadoObjeto.VENCIDO):
            reporte.estado = EstadoObjeto.RECUPERADO
        db.commit()
    except Exception:
        db.rollback()
        fotos.borrar_foto(fotos.CARPETA_ENTREGAS, nombre_foto)
        raise
    db.refresh(entrega)
    return entrega
