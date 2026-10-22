"""
Dependencias comunes de los endpoints.

FastAPI ejecuta estas funciones antes de cada endpoint que las pida y le
entrega el resultado. Así no se repite en cada endpoint el código para abrir
la base de datos o para validar el token.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Encargado
from app.security import leer_token

# Indica a FastAPI que el token se envía en el encabezado
# "Authorization: Bearer <token>" y que se obtiene en /auth/login.
# Gracias a esto, el botón "Authorize" de /docs permite iniciar sesión.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Abre una sesión de base de datos por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_encargado_actual(
    token: Annotated[str, Depends(esquema_oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> Encargado:
    """
    Devuelve el encargado dueño del token. Si el token falta, es inválido,
    venció o el encargado está inactivo, responde 401 (RNF-01, RNF-02).

    Todo endpoint protegido declara esta dependencia. El encargado que devuelve
    es el que se guarda como responsable de cada acción (RF13).
    """
    no_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o vencida. Inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    encargado_id = leer_token(token)
    if encargado_id is None:
        raise no_autorizado
    encargado = db.get(Encargado, encargado_id)
    if encargado is None or not encargado.activo:
        raise no_autorizado
    return encargado


# Atajos para declarar las dependencias en los endpoints de forma corta:
#   def mi_endpoint(db: DbSession, encargado: EncargadoActual): ...
DbSession = Annotated[Session, Depends(get_db)]
EncargadoActual = Annotated[Encargado, Depends(get_encargado_actual)]
