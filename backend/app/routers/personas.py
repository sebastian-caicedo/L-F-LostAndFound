"""
Endpoints del módulo de personas: estudiantes y docentes (RF02, RF19).

Todos requieren sesión iniciada. No hay endpoints para editar ni eliminar
personas: eliminar rompería la trazabilidad de reclamaciones y entregas, y
editar no se consideró necesario para el MVP.
"""

from fastapi import APIRouter, Depends, status

from app.deps import DbSession, get_encargado_actual
from app.models import TipoPersona
from app.schemas.alertas import PersonaConAlerta
from app.schemas.personas import DocenteCrear, EstudianteCrear, PersonaOut
from app.services import alertas_service, personas_service

router = APIRouter(
    prefix="/personas",
    tags=["Personas"],
    dependencies=[Depends(get_encargado_actual)],
)


@router.post("/estudiantes", response_model=PersonaOut, status_code=status.HTTP_201_CREATED)
def registrar_estudiante(datos: EstudianteCrear, db: DbSession):
    """
    Registra un estudiante (RF02).

    El código se puede escribir como t12345, 12345 o T00012345: siempre se
    guarda como T00012345. Responde 409 si el código o el correo ya existen.
    """
    return personas_service.registrar_estudiante(db, datos)


@router.post("/docentes", response_model=PersonaOut, status_code=status.HTTP_201_CREATED)
def registrar_docente(datos: DocenteCrear, db: DbSession):
    """Registra un docente (RF19). Responde 409 si el correo ya existe."""
    return personas_service.registrar_docente(db, datos)


@router.get("", response_model=list[PersonaOut])
def listar_personas(db: DbSession, tipo: TipoPersona | None = None, buscar: str | None = None):
    """
    Lista estudiantes y docentes. Filtros opcionales:
    - tipo: ESTUDIANTE o DOCENTE.
    - buscar: texto contenido en el nombre, el código o el correo (sin importar mayúsculas ni tildes).
    """
    return personas_service.listar(db, tipo, buscar)


@router.get("/alertas", response_model=list[PersonaConAlerta])
def personas_con_alerta(db: DbSession):
    """
    Personas con 3 o más reclamaciones rechazadas de objetos distintos (RF24),
    de más a menos rechazos. Solo informa: la decisión sigue siendo del encargado.
    """
    return [
        PersonaConAlerta(persona=persona, alerta=alertas_service.construir_alerta(total))
        for persona, total in alertas_service.personas_con_alerta(db)
    ]


@router.get("/codigo/{codigo}", response_model=PersonaOut)
def buscar_por_codigo(codigo: str, db: DbSession):
    """Busca un estudiante por su código (acepta t70496 o T00070496)."""
    return personas_service.obtener_por_codigo(db, codigo)


@router.get("/{persona_id}", response_model=PersonaOut)
def obtener_persona(persona_id: int, db: DbSession):
    """Devuelve los datos de una persona."""
    return personas_service.obtener(db, persona_id)
