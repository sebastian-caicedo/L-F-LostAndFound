"""
Configuración del backend, leída del archivo .env.

Todo valor que cambia entre computadores o que es secreto (claves, rutas,
orígenes permitidos) se lee aquí y no se escribe directamente en el código.
El resto del backend importa estos valores desde este módulo.

Las variables disponibles están documentadas en .env.example.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# La ruta de la base de datos (DATABASE_URL) se lee en database.py.

# Clave con la que se firman los tokens de sesión (RF01). Debe ser larga,
# aleatoria y privada: quien la conozca podría fabricar tokens válidos.
# Si falta, la API no arranca (ver validar_configuracion).
SECRET_KEY: str = os.getenv("SECRET_KEY", "")

# Algoritmo de firma del token. HS256 usa una sola clave secreta (SECRET_KEY).
ALGORITMO_TOKEN: str = "HS256"

# Duración de la sesión del encargado. Por defecto 8 horas: una jornada de trabajo.
HORAS_EXPIRACION_TOKEN: int = int(os.getenv("TOKEN_EXPIRE_HOURS", "8"))

# Dirección del frontend (Astro) que tiene permiso para llamar a la API (CORS).
FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:4321")

# Carpeta donde se guardan las fotos de objetos y de entregas (RF20, RF22).
# Por defecto backend/uploads. No se sube al repositorio (.gitignore).
UPLOADS_DIR: Path = Path(os.getenv("UPLOADS_DIR", Path(__file__).resolve().parent.parent / "uploads"))

# Tamaño máximo de cada foto, en megabytes.
FOTO_MAX_MB: int = int(os.getenv("FOTO_MAX_MB", "5"))


def validar_configuracion() -> None:
    """
    Detiene el arranque de la API si falta una variable indispensable.
    Se llama desde main.py. Los scripts seed.py y verificar_bd.py no la usan,
    porque no necesitan la SECRET_KEY.
    """
    if not SECRET_KEY or SECRET_KEY.startswith("cambiar-por"):
        raise RuntimeError(
            "Falta configurar SECRET_KEY en el archivo .env. Genera una con:\n"
            '  python -c "import secrets; print(secrets.token_hex(32))"'
        )
