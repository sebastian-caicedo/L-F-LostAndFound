"""Esquemas del módulo de objetos (RF03, RF04, RF05, RF20, RF25)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.models import EstadoObjeto, TipoRegistro
from app.schemas.auth import EncargadoOut
from app.schemas.comunes import Categoria, FechaPasada, TextoLargo, TextoOpcional
from app.schemas.personas import PersonaResumen


class ObjetoPerdidoCrear(BaseModel):
    """Datos para registrar un objeto que una persona reporta como perdido (RF03)."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "persona_id": 1,
                "tipo": "Cuaderno",
                "descripcion": "Cuaderno argollado de cálculo",
                "caracteristicas": "Tapa azul, stickers de planetas, nombre en la primera hoja",
                "fecha_reporte": None,
            }
        },
    )

    persona_id: int = Field(description="Id de la persona que reporta la pérdida.")
    tipo: Categoria = Field(description="Categoría: celular, billetera, cuaderno, etc.")
    descripcion: TextoLargo
    caracteristicas: TextoLargo
    # Si no se envía, se usa la fecha de hoy.
    fecha_reporte: FechaPasada = None


class ObjetoEncontradoCrear(BaseModel):
    """Datos para registrar un objeto encontrado (RF04). Queda DISPONIBLE."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "tipo": "Celular",
                "descripcion": "Teléfono inteligente con forro",
                "caracteristicas": "Forro negro con grieta en la esquina",
                "fecha_encontrado": None,
                "lugar_encontrado": "Biblioteca, segundo piso",
            }
        },
    )

    tipo: Categoria
    descripcion: TextoLargo
    caracteristicas: TextoLargo
    # "Cuando corresponda" (HCU04): lugar y fecha son opcionales.
    fecha_encontrado: FechaPasada = None
    lugar_encontrado: TextoOpcional = None


class ObjetoEditar(BaseModel):
    """
    Campos que se pueden corregir de un objeto (RF25). Todos son opcionales:
    solo se cambia lo que se envía. El estado NO se puede editar: cambia solo
    con el flujo (reclamación y entrega).
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"caracteristicas": "Forro negro, grieta en la esquina superior derecha"}},
    )

    tipo: Categoria | None = None
    descripcion: TextoLargo | None = None
    caracteristicas: TextoLargo | None = None
    fecha_reporte: FechaPasada = None
    fecha_encontrado: FechaPasada = None
    lugar_encontrado: TextoOpcional = None

    @model_validator(mode="after")
    def no_vaciar_obligatorios(self):
        """Impide enviar null en campos obligatorios, lo que los borraría."""
        for campo in ("tipo", "descripcion", "caracteristicas"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"El campo {campo} no puede quedar vacío.")
        return self


class ObjetoBase(BaseModel):
    """Campos comunes de un objeto, con el indicador y la ruta de su foto."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_registro: TipoRegistro
    tipo: str
    descripcion: str
    estado: EstadoObjeto
    fecha_reporte: date | None
    fecha_encontrado: date | None
    lugar_encontrado: str | None
    fecha_registro: datetime
    # El nombre del archivo no se expone; solo si hay foto y dónde pedirla.
    foto: str | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def tiene_foto(self) -> bool:
        return self.foto is not None

    @computed_field
    @property
    def foto_url(self) -> str | None:
        """Ruta protegida para ver la foto. Requiere el token de sesión."""
        return f"/objetos/{self.id}/foto" if self.foto else None


class ObjetoResumen(ObjetoBase):
    """
    Objeto en la lista de consulta (RF05).

    No incluye las características: son lo que el reclamante debe describir
    sin haberlas visto, así que solo aparecen en el detalle del objeto.
    """


class ObjetoDetalle(ObjetoBase):
    """Todos los datos de un objeto, con quién lo reportó, registró y editó."""

    caracteristicas: str
    persona: PersonaResumen | None
    encargado: EncargadoOut
    encargado_modificacion: EncargadoOut | None
    fecha_modificacion: datetime | None
