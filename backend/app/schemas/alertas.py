"""Esquemas de la alerta de reclamaciones fallidas (RF24)."""

from pydantic import BaseModel

from app.schemas.personas import PersonaOut


class AlertaOut(BaseModel):
    """Resumen de intentos fallidos de una persona."""

    rechazos_objetos_distintos: int
    # True cuando llega al umbral (3 por defecto).
    activa: bool
    mensaje: str | None


class PersonaConAlerta(BaseModel):
    """Persona que tiene la alerta activa, para la lista de alertas."""

    persona: PersonaOut
    alerta: AlertaOut
