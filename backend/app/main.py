"""
Punto de entrada de la API de L&F.

Crea la aplicación FastAPI, configura CORS, registra los routers de cada
módulo y convierte los errores de negocio en respuestas HTTP. Se ejecuta
desde backend/ con:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app import config
from app.errores import ErrorNegocio
from app.routers import auth, entregas, historial, objetos, personas, reclamaciones

# Si falta la SECRET_KEY, la API no arranca y muestra cómo generarla.
config.validar_configuracion()

app = FastAPI(
    title="L&F - Lost And Found",
    description="API para la gestión de objetos perdidos y encontrados.",
)

# Permite que el frontend (Astro) llame a esta API. El origen se lee del .env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(personas.router)
app.include_router(objetos.router)
app.include_router(reclamaciones.router)
app.include_router(entregas.router)
app.include_router(historial.router)


@app.exception_handler(ErrorNegocio)
def manejar_error_negocio(_request: Request, error: ErrorNegocio) -> JSONResponse:
    """Convierte un error de los servicios en una respuesta con su código y mensaje."""
    return JSONResponse(status_code=error.codigo_http, content={"detail": error.mensaje})


@app.exception_handler(IntegrityError)
def manejar_error_integridad(_request: Request, _error: IntegrityError) -> JSONResponse:
    """
    Última línea de defensa: si la base rechaza un dato por una restricción que
    los servicios no alcanzaron a validar, se responde 409 en vez de un error 500.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "El dato no cumple las reglas de la base de datos o choca con un registro existente."},
    )


@app.get("/health", tags=["Sistema"])
def health():
    """Comprueba que la API esté en funcionamiento. No requiere sesión."""
    return {"status": "ok"}
