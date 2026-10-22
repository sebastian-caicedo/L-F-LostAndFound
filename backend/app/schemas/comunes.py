"""
Tipos de datos reutilizables en los esquemas.

Cada tipo combina el tipo de Python, su longitud máxima y la validación que
le corresponde. Al declarar un campo como `Nombre`, Pydantic aplica todo eso
automáticamente antes de que el dato llegue al servicio.
"""

from datetime import date
from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from app.validaciones import (
    fecha_no_futura,
    normalizar_codigo,
    normalizar_correo,
    normalizar_telefono,
    texto_obligatorio,
    texto_opcional,
)

TextoCorto = Annotated[str, StringConstraints(max_length=100), AfterValidator(texto_obligatorio)]
TextoLargo = Annotated[str, StringConstraints(max_length=2000), AfterValidator(texto_obligatorio)]
TextoOpcional = Annotated[
    Annotated[str, StringConstraints(max_length=150)] | None, AfterValidator(texto_opcional)
]
Categoria = Annotated[str, StringConstraints(max_length=50), AfterValidator(texto_obligatorio)]
CodigoEstudiantil = Annotated[str, StringConstraints(max_length=20), AfterValidator(normalizar_codigo)]
Correo = Annotated[str, StringConstraints(max_length=120), AfterValidator(normalizar_correo)]
Telefono = Annotated[str, StringConstraints(max_length=25), AfterValidator(normalizar_telefono)]
FechaPasada = Annotated[date | None, AfterValidator(fecha_no_futura)]
