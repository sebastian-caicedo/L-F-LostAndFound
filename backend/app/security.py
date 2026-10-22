"""
Funciones de seguridad: contraseñas y tokens de sesión (RF01).

- Contraseñas: se guardan como hash bcrypt. El hash no se puede revertir;
  para validar una contraseña se calcula de nuevo y se compara.
- Tokens: al iniciar sesión, el encargado recibe un token JWT firmado con la
  SECRET_KEY. El token lleva el id del encargado y la fecha de vencimiento.
  Si alguien lo modifica, la firma deja de coincidir y se rechaza.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app import config


def hashear_password(password: str) -> str:
    """Convierte una contraseña en un hash bcrypt para guardarlo en la base."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    """Indica si la contraseña escrita corresponde al hash guardado."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def crear_token(encargado_id: int) -> str:
    """
    Crea el token de sesión del encargado.

    Contenido del token:
    - sub: id del encargado. Así el backend sabe quién hace cada acción (RF13).
    - exp: fecha y hora en que vence (8 horas por defecto).
    """
    vence = datetime.now(timezone.utc) + timedelta(hours=config.HORAS_EXPIRACION_TOKEN)
    contenido = {"sub": str(encargado_id), "exp": vence}
    return jwt.encode(contenido, config.SECRET_KEY, algorithm=config.ALGORITMO_TOKEN)


def leer_token(token: str) -> int | None:
    """
    Valida el token y devuelve el id del encargado.
    Devuelve None si el token es inválido, fue modificado o ya venció.
    """
    try:
        contenido = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITMO_TOKEN])
        return int(contenido["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
