"""Reglas de negocio del módulo de personas: estudiantes y docentes (RF02, RF19)."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.errores import Conflicto, DatoInvalido, NoEncontrado
from app.models import Persona, TipoPersona
from app.schemas.personas import DocenteCrear, EstudianteCrear
from app.validaciones import normalizar_codigo


def _verificar_correo_libre(db: Session, correo: str) -> None:
    if db.scalar(select(Persona.id).where(Persona.correo == correo)) is not None:
        raise Conflicto(f"Ya hay una persona registrada con el correo {correo}.")


def registrar_estudiante(db: Session, datos: EstudianteCrear) -> Persona:
    """
    Registra un estudiante (RF02). El código ya llega normalizado (T + 8 dígitos)
    desde el esquema. Se rechaza si el código o el correo ya existen.
    """
    if db.scalar(select(Persona.id).where(Persona.codigo == datos.codigo)) is not None:
        raise Conflicto(f"Ya hay un estudiante registrado con el código {datos.codigo}.")
    _verificar_correo_libre(db, datos.correo)

    persona = Persona(tipo=TipoPersona.ESTUDIANTE, **datos.model_dump())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


def registrar_docente(db: Session, datos: DocenteCrear) -> Persona:
    """Registra un docente (RF19). Se identifica por su correo institucional, que no se repite."""
    _verificar_correo_libre(db, datos.correo)

    persona = Persona(tipo=TipoPersona.DOCENTE, **datos.model_dump())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


def listar(db: Session, tipo: TipoPersona | None = None, buscar: str | None = None) -> list[Persona]:
    """
    Lista las personas, ordenadas por nombre.
    - tipo: solo estudiantes o solo docentes.
    - buscar: texto que se busca en el nombre, el código o el correo.
    """
    consulta = select(Persona).order_by(Persona.nombre)
    if tipo is not None:
        consulta = consulta.where(Persona.tipo == tipo)
    if buscar and buscar.strip():
        patron = f"%{buscar.strip()}%"
        consulta = consulta.where(
            or_(
                Persona.nombre.ilike(patron),
                Persona.codigo.ilike(patron),
                Persona.correo.ilike(patron),
            )
        )
    return list(db.scalars(consulta))


def obtener(db: Session, persona_id: int) -> Persona:
    persona = db.get(Persona, persona_id)
    if persona is None:
        raise NoEncontrado(f"No existe una persona con id {persona_id}.")
    return persona


def obtener_por_codigo(db: Session, codigo: str) -> Persona:
    """
    Busca un estudiante por su código. Acepta el código escrito de cualquier
    forma válida (t70496, T00070496) porque lo normaliza antes de buscar.
    """
    try:
        codigo = normalizar_codigo(codigo)
    except ValueError as error:
        raise DatoInvalido(str(error)) from error
    persona = db.scalar(select(Persona).where(Persona.codigo == codigo))
    if persona is None:
        raise NoEncontrado(f"No hay un estudiante registrado con el código {codigo}.")
    return persona
