"""Endpoints de entregas: foto de evidencia e incidentes de fraude (RF22, RF23)."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.deps import DbSession, EncargadoActual, get_encargado_actual
from app.schemas.entregas import EntregaOut, IncidenteCrear, IncidenteOut
from app.services import historial_service

router = APIRouter(
    prefix="/entregas",
    tags=["Entregas e incidentes"],
    dependencies=[Depends(get_encargado_actual)],
)


@router.get("/{entrega_id}", response_model=EntregaOut)
def obtener_entrega(entrega_id: int, db: DbSession):
    """Datos de una entrega: quién se llevó qué objeto, cuándo y quién lo entregó."""
    return historial_service.obtener_entrega(db, entrega_id)


@router.get(
    "/{entrega_id}/foto",
    response_class=FileResponse,
    responses={200: {"content": {"image/*": {}}, "description": "La foto de evidencia."}},
)
def ver_foto_entrega(entrega_id: int, db: DbSession):
    """Foto de la persona con el objeto, tomada al entregar (RF22)."""
    return FileResponse(historial_service.ruta_foto_entrega(db, entrega_id))


@router.post("/{entrega_id}/incidente", response_model=IncidenteOut, status_code=status.HTTP_201_CREATED)
def registrar_incidente(entrega_id: int, datos: IncidenteCrear, db: DbSession, encargado: EncargadoActual):
    """
    Registra que esta entrega resultó fraudulenta (RF23): cómo ocurrió, qué
    medida se propone y, si se conoce, quién es el dueño real. El objeto
    sigue ENTREGADO.
    """
    return historial_service.registrar_incidente(db, entrega_id, datos, encargado)
