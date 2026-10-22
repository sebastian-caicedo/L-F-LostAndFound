"""
Historial, fotos de entrega e incidentes (RF17, RF18, RF22, RF23).

El historial no tiene tablas propias: se arma con las reclamaciones,
decisiones y entregas, que nunca se borran ni se modifican después de decididas.
"""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import fotos
from app.errores import Conflicto, DatoInvalido, NoEncontrado
from app.models import (
    Encargado,
    Entrega,
    EstadoReclamacion,
    Incidente,
    Persona,
    Reclamacion,
)
from app.schemas.entregas import IncidenteCrear
from app.schemas.reclamaciones import ReclamacionHistorial
from app.services import alertas_service


def historial_reclamaciones(
    db: Session,
    estado: EstadoReclamacion | None = None,
    persona_id: int | None = None,
    objeto_id: int | None = None,
) -> list[ReclamacionHistorial]:
    """
    Historial de reclamaciones con su descripción, decisión y entrega (RF17).
    De la más reciente a la más antigua. Filtros opcionales y combinables.
    """
    consulta = select(Reclamacion).order_by(Reclamacion.fecha_creacion.desc(), Reclamacion.id.desc())
    if estado is not None:
        consulta = consulta.where(Reclamacion.estado == estado)
    if persona_id is not None:
        consulta = consulta.where(Reclamacion.persona_id == persona_id)
    if objeto_id is not None:
        consulta = consulta.where(Reclamacion.objeto_id == objeto_id)
    reclamaciones = list(db.scalars(consulta))

    rechazos = alertas_service.rechazos_por_persona(db, {r.persona_id for r in reclamaciones})
    salida = []
    for reclamacion in reclamaciones:
        item = ReclamacionHistorial.model_validate(reclamacion)
        item.alerta = alertas_service.construir_alerta(rechazos.get(reclamacion.persona_id, 0))
        salida.append(item)
    return salida


def historial_entregas(
    db: Session, persona_id: int | None = None, objeto_id: int | None = None
) -> list[Entrega]:
    """
    Historial de entregas (RF18), de la más reciente a la más antigua.
    Con objeto_id se responde "¿quién se llevó este objeto?"; con persona_id,
    "¿qué objetos se ha llevado esta persona?".
    """
    consulta = (
        select(Entrega)
        .join(Reclamacion, Entrega.reclamacion_id == Reclamacion.id)
        .order_by(Entrega.fecha_hora.desc(), Entrega.id.desc())
    )
    if persona_id is not None:
        consulta = consulta.where(Reclamacion.persona_id == persona_id)
    if objeto_id is not None:
        consulta = consulta.where(Reclamacion.objeto_id == objeto_id)
    return list(db.scalars(consulta))


def obtener_entrega(db: Session, entrega_id: int) -> Entrega:
    entrega = db.get(Entrega, entrega_id)
    if entrega is None:
        raise NoEncontrado(f"No existe una entrega con id {entrega_id}.")
    return entrega


def ruta_foto_entrega(db: Session, entrega_id: int) -> Path:
    """Ruta de la foto de evidencia de una entrega (RF22)."""
    entrega = obtener_entrega(db, entrega_id)
    ruta = fotos.ruta_foto(fotos.CARPETA_ENTREGAS, entrega.foto_evidencia)
    if not ruta.is_file():
        raise NoEncontrado("No se encontró el archivo de la foto en el servidor.")
    return ruta


def registrar_incidente(
    db: Session, entrega_id: int, datos: IncidenteCrear, encargado: Encargado
) -> Incidente:
    """
    Registra que una entrega resultó fraudulenta (RF23).

    - Una entrega tiene como máximo un incidente.
    - El dueño real, si se indica, debe existir y no puede ser quien se llevó el objeto.
    - El objeto sigue ENTREGADO: el incidente es el registro de lo que pasó.
    """
    entrega = obtener_entrega(db, entrega_id)
    if entrega.incidente is not None:
        raise Conflicto("Esta entrega ya tiene un incidente registrado.")
    if datos.propietario_real_id is not None:
        if db.get(Persona, datos.propietario_real_id) is None:
            raise DatoInvalido(f"No existe una persona con id {datos.propietario_real_id}.")
        if datos.propietario_real_id == entrega.reclamacion.persona_id:
            raise DatoInvalido("El dueño real no puede ser la misma persona que se llevó el objeto.")

    incidente = Incidente(entrega_id=entrega.id, encargado_id=encargado.id, **datos.model_dump())
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente


def listar_incidentes(db: Session) -> list[Incidente]:
    """Incidentes de fraude, del más reciente al más antiguo (RF23)."""
    return list(db.scalars(select(Incidente).order_by(Incidente.fecha_hora.desc(), Incidente.id.desc())))
