"""
Normalización de texto para las búsquedas.

El encargado puede escribir "Audifonos" (sin tilde) aunque el objeto se haya
registrado como "Audífonos", o "maria" para encontrar a "María". Para que la
búsqueda los encuentre, se comparan los dos textos sin tildes y en minúsculas.

Cómo funciona: unicodedata.normalize("NFD") separa cada letra de su tilde
("í" pasa a ser "i" + "´"). Luego se descartan las marcas (categoría "Mn") y
queda solo la letra. La ñ también pasa a n ("año" coincide con "ano").

Solo se usa para comparar: los datos se guardan tal como se escribieron.
"""

import unicodedata


def sin_tildes(texto: str | None) -> str:
    """Devuelve el texto en minúsculas y sin tildes. "Audífonos" -> "audifonos"."""
    if texto is None:
        return ""
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
