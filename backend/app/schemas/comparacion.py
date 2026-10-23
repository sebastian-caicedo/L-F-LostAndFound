"""
Esquemas de la comparación y de las coincidencias (RF05, RF09, RF21, RF26, RF27, RF28).

Aquí se arma lo que el encargado ve para decidir: lo registrado del objeto,
lo que describe la persona y, si el objeto ya se entregó a otra persona,
los datos de esa entrega para evaluar un posible fraude.
"""

from datetime import datetime

from pydantic import BaseModel, computed_field

from app.models import EstadoReclamacion
from app.schemas.alertas import AlertaOut
from app.schemas.auth import EncargadoOut
from app.schemas.entregas import IncidenteMini
from app.schemas.personas import PersonaOut, PersonaResumen
from app.schemas.reclamaciones import DecisionOut, InformacionOut, ObjetoComparacion


class EntregaPrevia(BaseModel):
    """
    El objeto ya se entregó a otra persona (RF26). Muestra a quién, cuándo,
    qué describió esa persona para llevárselo y con qué motivo se aprobó, para
    compararlo con quien reclama ahora.
    """

    entrega_id: int
    fecha_hora: datetime
    entregado_por: EncargadoOut
    persona: PersonaResumen
    descripcion_dada: InformacionOut | None
    motivo_aprobacion: str
    incidente: IncidenteMini | None

    @computed_field
    @property
    def foto_url(self) -> str:
        """Foto de la persona con el objeto, tomada al entregarlo (RF22)."""
        return f"/entregas/{self.entrega_id}/foto"


class ComparacionOut(BaseModel):
    """
    Objeto y reclamante lado a lado (RF09, HCU08): lo registrado del objeto
    frente a lo que describió la persona, con la alerta de intentos fallidos.
    Si el objeto ya se entregó a otra persona, incluye esa entrega (RF26).
    """

    reclamacion_id: int
    estado: EstadoReclamacion
    fecha_creacion: datetime
    persona: PersonaOut
    alerta: AlertaOut
    descripcion_reclamante: InformacionOut
    objeto: ObjetoComparacion
    # Reporte de pérdida que la persona hizo antes, si está vinculado (RF27).
    # Es una descripción más, dada sin haber visto el objeto.
    reporte: ObjetoComparacion | None = None
    decision: DecisionOut | None
    entrega_previa: EntregaPrevia | None = None
    aviso: str | None = None


class Coincidencia(BaseModel):
    """
    Posible coincidencia entre un objeto perdido y uno encontrado (RF05, RF26, RF28).

    - Desde un reporte de pérdida: objeto encontrado candidato; si ya se
      entregó, incluye a quién y con qué descripción (entrega_previa).
    - Desde un objeto encontrado: reporte de pérdida abierto candidato, con la
      persona que lo reportó para poder contactarla (reportado_por).
    """

    objeto: ObjetoComparacion
    entrega_previa: EntregaPrevia | None = None
    reportado_por: PersonaOut | None = None
