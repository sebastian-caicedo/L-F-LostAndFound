"""Reglas de negocio de la autenticación del encargado (RF01)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Encargado
from app.security import crear_token, verificar_password


def autenticar(db: Session, usuario: str, password: str) -> str | None:
    """
    Valida las credenciales y devuelve un token de sesión.

    Devuelve None si el usuario no existe, si la contraseña es incorrecta o si
    el encargado está inactivo. En los tres casos la respuesta es la misma, para
    no revelar si un usuario existe o no.
    """
    encargado = db.scalar(select(Encargado).where(Encargado.usuario == usuario))
    if encargado is None or not encargado.activo:
        return None
    if not verificar_password(password, encargado.password_hash):
        return None
    return crear_token(encargado.id)
