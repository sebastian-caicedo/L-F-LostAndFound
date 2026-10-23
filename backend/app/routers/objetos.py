"""
Endpoints del módulo de objetos (RF03, RF04, RF05, RF20, RF25).

Todos requieren sesión iniciada. No hay endpoint para eliminar objetos:
eliminarlos rompería el historial de reclamaciones y entregas.
"""

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse

from app import fotos
from app.deps import DbSession, EncargadoActual, get_encargado_actual
from app.models import EstadoObjeto, TipoRegistro
from app.schemas.comparacion import Coincidencia
from app.schemas.objetos import (
    ObjetoDetalle,
    ObjetoEditar,
    ObjetoEncontradoCrear,
    ObjetoPerdidoCrear,
    ObjetoResumen,
)
from app.services import objetos_service

router = APIRouter(
    prefix="/objetos",
    tags=["Objetos"],
    dependencies=[Depends(get_encargado_actual)],
)


@router.post("/perdidos", response_model=ObjetoDetalle, status_code=status.HTTP_201_CREATED)
def registrar_perdido(datos: ObjetoPerdidoCrear, db: DbSession, encargado: EncargadoActual):
    """
    Registra un objeto que una persona reporta como perdido (RF03).
    Queda en estado PERDIDO. Si no se envía fecha_reporte, se usa la de hoy.
    """
    return objetos_service.registrar_perdido(db, datos, encargado)


@router.post("/encontrados", response_model=ObjetoDetalle, status_code=status.HTTP_201_CREATED)
def registrar_encontrado(datos: ObjetoEncontradoCrear, db: DbSession, encargado: EncargadoActual):
    """
    Registra un objeto encontrado (RF04). Queda en estado DISPONIBLE.
    La foto se agrega después con PUT /objetos/{id}/foto.
    """
    return objetos_service.registrar_encontrado(db, datos, encargado)


@router.get("", response_model=list[ObjetoResumen])
def listar_objetos(
    db: DbSession,
    tipo_registro: TipoRegistro | None = None,
    estado: EstadoObjeto | None = None,
    tipo: str | None = None,
    buscar: str | None = None,
    persona_id: int | None = None,
):
    """
    Consulta los objetos registrados (RF05). Filtros opcionales y combinables:
    - tipo_registro: PERDIDO o ENCONTRADO.
    - estado: PERDIDO (reportes abiertos), RECUPERADO, VENCIDO, DISPONIBLE o ENTREGADO.
    - tipo: categoría (celular, billetera...).
    - buscar: texto contenido en la descripción.
    - persona_id: reportes de pérdida de una persona.

    La lista no muestra las características: solo aparecen en el detalle.
    Los reportes de pérdida vencen a los 15 días de registrados (RF29): pasan a
    VENCIDO, no se borran.
    """
    return objetos_service.listar(db, tipo_registro, estado, tipo, buscar, persona_id)


@router.get("/{objeto_id}", response_model=ObjetoDetalle)
def obtener_objeto(objeto_id: int, db: DbSession):
    """Detalle completo de un objeto (RF05)."""
    return objetos_service.obtener(db, objeto_id)


@router.get("/{objeto_id}/coincidencias", response_model=list[Coincidencia])
def coincidencias(objeto_id: int, db: DbSession):
    """
    Posibles coincidencias entre perdidos y encontrados, en las dos direcciones
    (RF05, RF26, RF28):
    - De un reporte de pérdida: objetos encontrados de la misma categoría; si
      alguno ya se entregó, muestra a quién y qué describió esa persona.
    - De un objeto encontrado: reportes de pérdida abiertos de la misma
      categoría, con la persona que lo reportó para contactarla.
    """
    return objetos_service.coincidencias(db, objeto_id)


@router.patch("/{objeto_id}", response_model=ObjetoDetalle)
def editar_objeto(objeto_id: int, datos: ObjetoEditar, db: DbSession, encargado: EncargadoActual):
    """
    Corrige los datos de un objeto (RF25). Solo cambia los campos enviados y
    registra quién y cuándo lo editó. No se puede editar un objeto ENTREGADO,
    RECUPERADO o VENCIDO, ni cambiar su estado.
    """
    return objetos_service.editar(db, objeto_id, datos, encargado)


@router.put("/{objeto_id}/foto", response_model=ObjetoDetalle)
def subir_foto(objeto_id: int, foto: UploadFile, db: DbSession, encargado: EncargadoActual):
    """
    Agrega o reemplaza la foto de un objeto (RF20).
    Formatos: JPG, PNG o WEBP. Tamaño máximo: 5 MB (FOTO_MAX_MB).
    """
    contenido = fotos.leer_subida(foto.file)
    return objetos_service.guardar_foto(db, objeto_id, contenido, encargado)


@router.get(
    "/{objeto_id}/foto",
    response_class=FileResponse,
    responses={200: {"content": {"image/*": {}}, "description": "La foto del objeto."}},
)
def ver_foto(objeto_id: int, db: DbSession):
    """
    Devuelve la foto de un objeto (RF20). Requiere sesión: las fotos no son
    públicas, para que nadie pueda ver cómo es un objeto antes de describirlo.
    """
    return FileResponse(objetos_service.ruta_foto(db, objeto_id))
