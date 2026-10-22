"""
Punto de entrada de la API de L&F.

Crea la aplicación FastAPI, configura CORS y registra los routers de cada
módulo. Se ejecuta desde backend/ con:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.routers import auth

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


@app.get("/health", tags=["Sistema"])
def health():
    """Comprueba que la API esté en funcionamiento. No requiere sesión."""
    return {"status": "ok"}
