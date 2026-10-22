"""
Esquemas de reclamaciones, revisión y decisión (RF06–RF14, RF21, RF24).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models import EstadoReclamacion, ResultadoDecision
from app.schemas.alertas import AlertaOut
from app.schemas.auth import EncargadoOut
from app.schemas.comunes import TextoLargo
from app.schemas.objetos import ObjetoBase, ObjetoMini
from app.schemas.personas import PersonaResumen

# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


class ReclamacionCrear(BaseModel):
    """Datos para registrar una reclamación presencial (RF06)."""

    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {"persona_id": 3, "objeto_id": 5}})

    persona_id: int = Field(description="Id de la persona que reclama (estudiante o docente).")
    objeto_id: int = Field(description="Id del objeto encontrado que reclama.")


class InformacionCrear(BaseModel):
    """
    Lo que la persona describe del objeto para demostrar que es suyo (RF07).
    Se escribe ANTES de ver la foto o las características del objeto.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "caracteristicas": "Audífonos blancos en un estuche con mis iniciales grabadas",
                "observaciones": "Dice que los dejó en el salón A-204 el lunes",
            }
        },
    )

    caracteristicas: TextoLargo
    observaciones: TextoLargo | None = None


class DecisionCrear(BaseModel):
    """
    Decisión del encargado (RF10, RF11). Solo se envían el resultado y el motivo:
    el encargado responsable y la fecha y hora los asigna el sistema (RF13, RF14).
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "resultado": "APROBADA",
                "motivo": "Describió las iniciales grabadas en el estuche, que no son visibles",
            }
        },
    )

    resultado: ResultadoDecision
    # Obligatorio y no puede ser solo espacios (RF12).
    motivo: TextoLargo


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------


class InformacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    caracteristicas: str
    observaciones: str | None
    fecha_registro: datetime


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resultado: ResultadoDecision
    motivo: str
    fecha_hora: datetime
    encargado: EncargadoOut


class EntregaMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    encargado: EncargadoOut


class ReclamacionOut(BaseModel):
    """Reclamación con la persona, el objeto y la alerta de intentos fallidos."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: EstadoReclamacion
    fecha_creacion: datetime
    persona: PersonaResumen
    objeto: ObjetoMini
    encargado: EncargadoOut
    decision: DecisionOut | None
    # Se usa para calcular tiene_informacion; en el historial sí se muestra.
    informacion: InformacionOut | None = Field(default=None, exclude=True)
    # Se completa en el servicio (RF24).
    alerta: AlertaOut | None = None

    @computed_field
    @property
    def tiene_informacion(self) -> bool:
        """Si ya se registró la descripción del reclamante (RF07)."""
        return self.informacion is not None


class ReclamacionHistorial(ReclamacionOut):
    """Reclamación completa para el historial (RF17)."""

    informacion: InformacionOut | None = None
    entrega: EntregaMini | None


class ObjetoComparacion(ObjetoBase):
    """
    Objeto en la pantalla de comparación: incluye las características y la foto.
    Solo se entrega cuando el reclamante ya dio su descripción (RF21).
    """

    caracteristicas: str
