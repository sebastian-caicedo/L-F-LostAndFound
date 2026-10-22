"""Endpoints de autenticación del encargado (RF01)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import DbSession, EncargadoActual
from app.schemas.auth import EncargadoOut, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def iniciar_sesion(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """
    Inicia sesión con usuario y contraseña (RF01).

    Devuelve un token válido por 8 horas. Se recibe como formulario
    (username, password) porque es el formato estándar de OAuth2 que usa
    el botón "Authorize" de /docs.
    """
    token = auth_service.autenticar(db, formulario.username, formulario.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=token)


@router.get("/me", response_model=EncargadoOut)
def encargado_actual(encargado: EncargadoActual) -> EncargadoOut:
    """
    Devuelve los datos del encargado que tiene la sesión abierta.
    Sirve para comprobar que el token funciona y, en el frontend, para
    mostrar el nombre del encargado.
    """
    return EncargadoOut.model_validate(encargado)
