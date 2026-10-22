"""
Manejo de las fotos de objetos (RF20) y de entregas (RF22).

Las fotos se guardan como archivos en la carpeta UPLOADS_DIR (por defecto
backend/uploads) y en la base solo se guarda el nombre del archivo. Así la
base de datos se mantiene liviana.

Las fotos NO se publican como archivos estáticos: solo se pueden ver a través
de endpoints que exigen sesión iniciada. Eso protege la verificación a ciegas:
nadie sin sesión puede ver cómo es un objeto encontrado.
"""

import uuid
from pathlib import Path
from typing import BinaryIO

from app import config
from app.errores import DatoInvalido

# Subcarpetas permitidas dentro de UPLOADS_DIR.
CARPETA_OBJETOS = "objetos"
CARPETA_ENTREGAS = "entregas"

# Los primeros bytes de un archivo indican su formato real. Se revisan en lugar
# de confiar en la extensión o en el tipo que declara el navegador, que se
# pueden falsificar.
_FIRMAS = {
    "jpg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}


def _detectar_formato(contenido: bytes) -> str | None:
    for extension, firmas in _FIRMAS.items():
        if any(contenido.startswith(f) for f in firmas):
            return extension
    # WEBP: empieza por "RIFF" y en la posición 8 dice "WEBP".
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return "webp"
    return None


def leer_subida(archivo: BinaryIO) -> bytes:
    """
    Lee un archivo subido sin pasar del tamaño máximo. Se lee un byte más del
    límite: si llega a leerse, la foto es demasiado grande y se rechaza sin
    cargar el resto en memoria.
    """
    limite = config.FOTO_MAX_MB * 1024 * 1024
    contenido = archivo.read(limite + 1)
    if len(contenido) > limite:
        raise DatoInvalido(f"La foto supera el tamaño máximo de {config.FOTO_MAX_MB} MB.")
    return contenido


def guardar_foto(contenido: bytes, carpeta: str) -> str:
    """
    Valida la imagen, la guarda con un nombre aleatorio y devuelve ese nombre.

    El nombre aleatorio (uuid) evita que dos fotos se sobrescriban y que se
    pueda adivinar el nombre de una foto.
    """
    if not contenido:
        raise DatoInvalido("La foto está vacía.")
    if len(contenido) > config.FOTO_MAX_MB * 1024 * 1024:
        raise DatoInvalido(f"La foto supera el tamaño máximo de {config.FOTO_MAX_MB} MB.")
    extension = _detectar_formato(contenido)
    if extension is None:
        raise DatoInvalido("El archivo no es una imagen válida. Formatos permitidos: JPG, PNG o WEBP.")

    destino = config.UPLOADS_DIR / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    nombre = f"{uuid.uuid4().hex}.{extension}"
    (destino / nombre).write_bytes(contenido)
    return nombre


def ruta_foto(carpeta: str, nombre: str) -> Path:
    """Ruta completa de una foto guardada."""
    return config.UPLOADS_DIR / carpeta / nombre


def borrar_foto(carpeta: str, nombre: str | None) -> None:
    """Borra una foto reemplazada. Si no existe, no hace nada."""
    if nombre:
        ruta_foto(carpeta, nombre).unlink(missing_ok=True)
