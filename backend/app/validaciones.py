"""
Validaciones y normalización de datos que escribe el encargado (RNF-04).

"Normalizar" es llevar un dato a una forma única antes de guardarlo. Por
ejemplo, el encargado puede escribir t70496 o T00070496 y en la base siempre
queda T00070496. Así las búsquedas y la regla de "código único" funcionan
aunque el dato se escriba de formas distintas.

Cada función devuelve el valor normalizado o lanza ValueError con un mensaje
en español. Los esquemas de Pydantic las usan para responder 422 si algo falla.
"""

import re
from datetime import date

_SOLO_DIGITOS = re.compile(r"[0-9]+")
_CORREO = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_SEPARADORES_TELEFONO = re.compile(r"[\s\-().]")


def texto_obligatorio(valor: str) -> str:
    """Quita espacios al inicio y al final, y rechaza textos vacíos."""
    limpio = valor.strip()
    if not limpio:
        raise ValueError("Este campo es obligatorio y no puede estar vacío.")
    return limpio


def texto_opcional(valor: str | None) -> str | None:
    """Quita espacios; si queda vacío, lo guarda como sin dato (None)."""
    if valor is None:
        return None
    limpio = valor.strip()
    return limpio or None


def normalizar_codigo(valor: str) -> str:
    """
    Convierte un código estudiantil al formato de la universidad: T + 8 dígitos.

    Acepta la T en minúscula o sin T, y completa los ceros a la izquierda:
        t70496    -> T00070496
        70496     -> T00070496
        T00070496 -> T00070496
    Rechaza letras distintas a la T inicial, más de 8 dígitos o un código en cero.
    """
    limpio = valor.strip().upper().replace(" ", "")
    if limpio.startswith("T"):
        limpio = limpio[1:]
    if not _SOLO_DIGITOS.fullmatch(limpio) or len(limpio) > 8 or int(limpio) == 0:
        raise ValueError(
            "El código estudiantil debe ser una T seguida de hasta 8 dígitos, "
            "por ejemplo T00012345."
        )
    return "T" + limpio.zfill(8)


def normalizar_correo(valor: str) -> str:
    """Valida el formato del correo y lo guarda en minúsculas."""
    limpio = valor.strip().lower()
    if not _CORREO.fullmatch(limpio):
        raise ValueError("El correo no tiene un formato válido, por ejemplo nombre@dominio.edu.co.")
    return limpio


def normalizar_telefono(valor: str) -> str:
    """
    Quita espacios, guiones, puntos y paréntesis, y valida que queden entre 7 y
    15 dígitos (con un + opcional al inicio para el indicativo del país).
        300 123 4567  -> 3001234567
        +57 300-1234567 -> +573001234567
    """
    limpio = _SEPARADORES_TELEFONO.sub("", valor.strip())
    digitos = limpio[1:] if limpio.startswith("+") else limpio
    if not _SOLO_DIGITOS.fullmatch(digitos) or not 7 <= len(digitos) <= 15:
        raise ValueError("El teléfono debe tener entre 7 y 15 dígitos, por ejemplo 3001234567.")
    return limpio


def fecha_no_futura(valor: date | None) -> date | None:
    """Rechaza fechas posteriores a hoy (no se puede perder o encontrar algo mañana)."""
    if valor is not None and valor > date.today():
        raise ValueError("La fecha no puede ser posterior a hoy.")
    return valor
