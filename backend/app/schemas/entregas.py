"""Esquemas de entregas e incidentes (RF15, RF18, RF22, RF23)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.auth import EncargadoOut
from app.schemas.comunes import TextoLargo
from app.schemas.objetos import ObjetoMini
from app.schemas.personas import PersonaResumen


class ReclamacionDeEntrega(BaseModel):
    """Quién reclamó qué, dentro de una entrega."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    persona: PersonaResumen
    objeto: ObjetoMini


class IncidenteMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime


class EntregaOut(BaseModel):
    """
    Entrega registrada (RF15, RF18). Responde a la pregunta del dueño real que
    llega después: quién se llevó el objeto, cuándo, quién lo entregó y con
    qué foto de evidencia.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    observaciones: str | None
    encargado: EncargadoOut
    reclamacion: ReclamacionDeEntrega
    incidente: IncidenteMini | None
    foto_evidencia: str = Field(exclude=True)

    @computed_field
    @property
    def foto_url(self) -> str:
        """Ruta protegida de la foto de la persona con el objeto (RF22)."""
        return f"/entregas/{self.id}/foto"


class IncidenteCrear(BaseModel):
    """Datos para registrar una entrega fraudulenta descubierta después (RF23)."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "como_lo_obtuvo": "Describió solo rasgos visibles desde el mostrador.",
                "medida_mejora": "Exigir al menos un rasgo que no se vea a simple vista.",
                "propietario_real_id": 5,
            }
        },
    )

    como_lo_obtuvo: TextoLargo = Field(description="Cómo logró llevarse el objeto: qué dijo y qué falló.")
    medida_mejora: TextoLargo = Field(description="Qué cambiar en el proceso para que no se repita.")
    propietario_real_id: int | None = Field(default=None, description="Dueño real, si ya se conoce.")


class EntregaDeIncidente(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    encargado: EncargadoOut
    reclamacion: ReclamacionDeEntrega


class IncidenteOut(BaseModel):
    """Incidente de fraude con la entrega, quien se llevó el objeto y el dueño real (RF23)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    como_lo_obtuvo: str
    medida_mejora: str
    encargado: EncargadoOut
    propietario_real: PersonaResumen | None
    entrega: EntregaDeIncidente
