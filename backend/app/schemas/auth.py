"""Esquemas del módulo de autenticación (RF01)."""

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Respuesta del inicio de sesión."""

    access_token: str
    # "bearer" es el tipo estándar: el token se envía en el encabezado
    # Authorization: Bearer <token>
    token_type: str = "bearer"


class EncargadoOut(BaseModel):
    """Datos públicos del encargado. Nunca incluye el hash de la contraseña."""

    # Permite construir el esquema directamente desde el modelo de SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    usuario: str
