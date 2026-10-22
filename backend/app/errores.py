"""
Errores de negocio del sistema.

Los servicios lanzan estos errores cuando una regla no se cumple. No saben
nada de HTTP: main.py se encarga de convertirlos en la respuesta adecuada
(404, 409 o 422) con un mensaje en español para el encargado.
"""


class ErrorNegocio(Exception):
    """Error base. El mensaje es el que verá el encargado."""

    codigo_http = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorNegocio):
    """El registro pedido no existe (404)."""

    codigo_http = 404


class Conflicto(ErrorNegocio):
    """El dato choca con uno existente, por ejemplo un código repetido (409)."""

    codigo_http = 409


class DatoInvalido(ErrorNegocio):
    """El dato no cumple una regla del sistema (422)."""

    codigo_http = 422


class AccionNoPermitida(ErrorNegocio):
    """La acción no se puede hacer en el estado actual del registro (409)."""

    codigo_http = 409
