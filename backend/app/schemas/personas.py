"""Esquemas del módulo de personas: estudiantes y docentes (RF02, RF19)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import TipoPersona
from app.schemas.comunes import CodigoEstudiantil, Correo, Telefono, TextoCorto


class EstudianteCrear(BaseModel):
    """Datos para registrar un estudiante. Todos son obligatorios."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "nombre": "Ana Prueba Gómez",
                "codigo": "t12345",
                "carrera": "Ingeniería de Sistemas",
                "correo": "ana.prueba@example.edu.co",
                "telefono": "300 000 0001",
            }
        },
    )

    nombre: TextoCorto
    # Se acepta t12345, 12345 o T00012345; siempre se guarda como T00012345.
    codigo: CodigoEstudiantil
    carrera: TextoCorto
    correo: Correo
    telefono: Telefono


class DocenteCrear(BaseModel):
    """Datos para registrar un docente. No tiene código ni carrera."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "nombre": "Carlos Docente Pérez",
                "correo": "carlos.docente@example.edu.co",
                "telefono": "3000000009",
            }
        },
    )

    nombre: TextoCorto
    correo: Correo
    telefono: Telefono


class PersonaResumen(BaseModel):
    """Datos mínimos de una persona, para mostrarla dentro de otros registros."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoPersona
    nombre: str
    codigo: str | None


class PersonaOut(PersonaResumen):
    """Todos los datos de una persona."""

    carrera: str | None
    correo: str
    telefono: str
    fecha_registro: datetime
