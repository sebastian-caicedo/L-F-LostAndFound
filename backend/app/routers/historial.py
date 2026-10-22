"""Endpoints de historial: reclamaciones, entregas e incidentes (RF17, RF18, RF23)."""

from fastapi import APIRouter, Depends

from app.deps import DbSession, get_encargado_actual
from app.models import EstadoReclamacion
from app.schemas.entregas import EntregaOut, IncidenteOut
from app.schemas.reclamaciones import ReclamacionHistorial
from app.services import historial_service

router = APIRouter(
    prefix="/historial",
    tags=["Historial"],
    dependencies=[Depends(get_encargado_actual)],
)


@router.get("/reclamaciones", response_model=list[ReclamacionHistorial])
def historial_reclamaciones(
    db: DbSession,
    estado: EstadoReclamacion | None = None,
    persona_id: int | None = None,
    objeto_id: int | None = None,
):
    """
    Historial de reclamaciones con la descripción del reclamante, la decisión
    (quién, qué, por qué y cuándo) y la entrega (RF17). Filtros opcionales.
    """
    return historial_service.historial_reclamaciones(db, estado, persona_id, objeto_id)


@router.get("/entregas", response_model=list[EntregaOut])
def historial_entregas(db: DbSession, persona_id: int | None = None, objeto_id: int | None = None):
    """
    Historial de entregas (RF18). Con objeto_id responde "¿quién se llevó
    este objeto?"; con persona_id, "¿qué objetos se ha llevado esta persona?".
    """
    return historial_service.historial_entregas(db, persona_id, objeto_id)


@router.get("/incidentes", response_model=list[IncidenteOut])
def historial_incidentes(db: DbSession):
    """
    Incidentes de fraude registrados (RF23): cómo ocurrieron y qué medidas se
    propusieron. Sirve para revisar y mejorar la seguridad del proceso.
    """
    return historial_service.listar_incidentes(db)
