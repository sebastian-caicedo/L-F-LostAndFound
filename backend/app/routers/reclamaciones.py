"""
Endpoints de reclamaciones, comparación, decisión y entrega (RF06–RF16, RF21, RF22, RF24).

El orden de uso en el mostrador es:
    POST /reclamaciones                    -> registrar la reclamación
    POST /reclamaciones/{id}/informacion   -> lo que describe la persona, sin ver el objeto
    GET  /reclamaciones/{id}/comparacion   -> objeto y descripción lado a lado, con foto
    POST /reclamaciones/{id}/decision      -> aprobar o rechazar con motivo
    POST /reclamaciones/{id}/entrega       -> entregar con foto de evidencia
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, status

from app import fotos
from app.deps import DbSession, EncargadoActual, get_encargado_actual
from app.models import EstadoReclamacion
from app.schemas.comunes import TextoOpcional
from app.schemas.entregas import EntregaOut
from app.schemas.reclamaciones import (
    ComparacionOut,
    DecisionCrear,
    InformacionCrear,
    ReclamacionCrear,
    ReclamacionOut,
)
from app.services import reclamaciones_service

router = APIRouter(
    prefix="/reclamaciones",
    tags=["Reclamaciones"],
    dependencies=[Depends(get_encargado_actual)],
)


@router.post("", response_model=ReclamacionOut, status_code=status.HTTP_201_CREATED)
def registrar_reclamacion(datos: ReclamacionCrear, db: DbSession, encargado: EncargadoActual):
    """
    Registra una reclamación presencial (RF06). Queda PENDIENTE.
    Solo se reclaman objetos encontrados y disponibles. La respuesta trae la
    alerta de intentos fallidos de la persona (RF24).
    """
    reclamacion = reclamaciones_service.registrar(db, datos, encargado)
    return reclamaciones_service.con_alerta(db, reclamacion)


@router.post("/{reclamacion_id}/informacion", response_model=ReclamacionOut, status_code=status.HTTP_201_CREATED)
def registrar_informacion(reclamacion_id: int, datos: InformacionCrear, db: DbSession):
    """
    Registra lo que la persona describe del objeto para probar que es suyo (RF07).
    Se registra una sola vez y no se puede modificar después.
    """
    reclamacion = reclamaciones_service.registrar_informacion(db, reclamacion_id, datos)
    return reclamaciones_service.con_alerta(db, reclamacion)


@router.get("", response_model=list[ReclamacionOut])
def listar_reclamaciones(db: DbSession, estado: EstadoReclamacion | None = EstadoReclamacion.PENDIENTE):
    """
    Lista reclamaciones (RF08). Por defecto muestra las PENDIENTES, de la más
    antigua a la más reciente. Cada una trae la alerta de su persona (RF24).
    """
    return reclamaciones_service.listar(db, estado)


@router.get("/{reclamacion_id}", response_model=ReclamacionOut)
def obtener_reclamacion(reclamacion_id: int, db: DbSession):
    """Datos de una reclamación, sin las características ni la foto del objeto."""
    return reclamaciones_service.con_alerta(db, reclamaciones_service.obtener(db, reclamacion_id))


@router.get("/{reclamacion_id}/comparacion", response_model=ComparacionOut)
def comparar(reclamacion_id: int, db: DbSession):
    """
    Muestra el objeto y la descripción del reclamante lado a lado (RF09).
    Responde 409 si todavía no se registró la descripción: la foto y las
    características del objeto no se muestran antes (RF21).
    """
    return reclamaciones_service.comparacion(db, reclamacion_id)


@router.post("/{reclamacion_id}/decision", response_model=ReclamacionOut)
def decidir(reclamacion_id: int, datos: DecisionCrear, db: DbSession, encargado: EncargadoActual):
    """
    Aprueba o rechaza la reclamación (RF10, RF11). El motivo es obligatorio (RF12).
    El encargado responsable y la fecha y hora se registran solos (RF13, RF14).
    """
    reclamacion = reclamaciones_service.decidir(db, reclamacion_id, datos, encargado)
    return reclamaciones_service.con_alerta(db, reclamacion)


@router.post("/{reclamacion_id}/entrega", response_model=EntregaOut, status_code=status.HTTP_201_CREATED)
def registrar_entrega(
    reclamacion_id: int,
    foto: UploadFile,
    db: DbSession,
    encargado: EncargadoActual,
    observaciones: Annotated[TextoOpcional, Form()] = None,
):
    """
    Entrega el objeto de una reclamación aprobada (RF15) y lo marca ENTREGADO (RF16).
    La foto de la persona con el objeto es obligatoria (RF22): JPG, PNG o WEBP, máx. 5 MB.
    """
    contenido = fotos.leer_subida(foto.file)
    return reclamaciones_service.registrar_entrega(db, reclamacion_id, contenido, observaciones, encargado)
