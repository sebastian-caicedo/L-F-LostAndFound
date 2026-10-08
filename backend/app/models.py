"""
Modelos de la base de datos de L&F (Fase 2 de la hoja de ruta).

Cada clase es una tabla de SQLite. El diseño parte del diagrama de clases
corregido (docs/diagramas) y se documenta en docs/modelo-datos.md.

Las reglas se reparten en dos niveles:
- Aquí (base de datos): integridad. Campos obligatorios, llaves foráneas,
  valores únicos y restricciones CHECK. Se cumplen aunque el backend falle.
- En los servicios del backend (Fase 3): reglas del flujo. Por ejemplo, que
  solo se entregue un objeto cuya reclamación fue aprobada (RF15).
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def ahora() -> datetime:
    """Fecha y hora actual del servidor. Se asigna automáticamente (RF14)."""
    return datetime.now()


def columna_enum(enum_clase: type[enum.Enum], nombre: str) -> Enum:
    """
    Guarda un Enum de Python como texto en SQLite y agrega un CHECK para que
    la base rechace cualquier valor que no esté en la lista.
    """
    return Enum(
        enum_clase,
        name=nombre,
        native_enum=False,
        create_constraint=True,
        values_callable=lambda e: [m.value for m in e],
        length=20,
    )


# ---------------------------------------------------------------------------
# Valores permitidos (estados)
# ---------------------------------------------------------------------------


class TipoRegistro(str, enum.Enum):
    """Indica si el objeto fue reportado como perdido o fue encontrado (RF03, RF04)."""

    PERDIDO = "PERDIDO"
    ENCONTRADO = "ENCONTRADO"


class EstadoObjeto(str, enum.Enum):
    """
    Estado del objeto.
    - PERDIDO: un estudiante reportó que lo perdió.
    - DISPONIBLE: fue encontrado y puede ser reclamado.
    - ENTREGADO: se devolvió a su dueño (RF16). No admite más reclamaciones.
    """

    PERDIDO = "PERDIDO"
    DISPONIBLE = "DISPONIBLE"
    ENTREGADO = "ENTREGADO"


class EstadoReclamacion(str, enum.Enum):
    """Estado de una reclamación. Toda reclamación nace PENDIENTE (HCU06)."""

    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


class ResultadoDecision(str, enum.Enum):
    """Resultado de la decisión manual del encargado (RF10, RF11)."""

    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------


class Encargado(Base):
    """
    Único usuario del sistema (RF01). Queda registrado como responsable de
    los objetos que registra, las reclamaciones, las decisiones y las entregas.
    """

    __tablename__ = "encargado"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    usuario: Mapped[str] = mapped_column(String(50), unique=True)
    # Nunca se guarda la contraseña: solo su hash (bcrypt).
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Estudiante(Base):
    """Datos del estudiante que reporta una pérdida o reclama un objeto (RF02)."""

    __tablename__ = "estudiante"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    # El código estudiantil identifica al estudiante en la universidad; no se repite.
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    carrera: Mapped[str] = mapped_column(String(100))
    contacto: Mapped[str] = mapped_column(String(100))

    objetos_reportados: Mapped[list["Objeto"]] = relationship(back_populates="estudiante")
    reclamaciones: Mapped[list["Reclamacion"]] = relationship(back_populates="estudiante")


class Objeto(Base):
    """
    Objeto perdido o encontrado (RF03, RF04, RF05).

    En el diagrama de clases, ObjetoPerdido y ObjetoEncontrado heredan de Objeto.
    Aquí se guardan en una sola tabla, diferenciados por tipo_registro, para
    poder consultarlos juntos (RF05). Los campos propios de cada tipo quedan
    vacíos cuando no aplican.
    """

    __tablename__ = "objeto"
    __table_args__ = (
        # Un objeto perdido siempre lo reporta un estudiante (HCU03).
        CheckConstraint(
            "tipo_registro = 'ENCONTRADO' OR estudiante_id IS NOT NULL",
            name="ck_objeto_perdido_tiene_estudiante",
        ),
        # El estado debe corresponder al tipo de registro.
        CheckConstraint(
            "(tipo_registro = 'PERDIDO' AND estado = 'PERDIDO') OR "
            "(tipo_registro = 'ENCONTRADO' AND estado IN ('DISPONIBLE', 'ENTREGADO'))",
            name="ck_objeto_estado_segun_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_registro: Mapped[TipoRegistro] = mapped_column(columna_enum(TipoRegistro, "tipo_registro"))
    # Categoría del objeto: celular, billetera, cuaderno, etc.
    tipo: Mapped[str] = mapped_column(String(50))
    descripcion: Mapped[str] = mapped_column(Text)
    # Rasgos que permiten reconocerlo (color, marca, marcas, contenido).
    caracteristicas: Mapped[str] = mapped_column(Text)
    estado: Mapped[EstadoObjeto] = mapped_column(columna_enum(EstadoObjeto, "estado_objeto"))

    # Solo para objetos perdidos.
    fecha_reporte: Mapped[date | None] = mapped_column(Date)
    estudiante_id: Mapped[int | None] = mapped_column(ForeignKey("estudiante.id"))

    # Solo para objetos encontrados ("cuando corresponda", HCU04).
    fecha_encontrado: Mapped[date | None] = mapped_column(Date)
    lugar_encontrado: Mapped[str | None] = mapped_column(String(150))

    # Trazabilidad del registro.
    encargado_id: Mapped[int] = mapped_column(ForeignKey("encargado.id"))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    estudiante: Mapped["Estudiante | None"] = relationship(back_populates="objetos_reportados")
    encargado: Mapped["Encargado"] = relationship()
    reclamaciones: Mapped[list["Reclamacion"]] = relationship(back_populates="objeto")


class Reclamacion(Base):
    """
    Reclamación presencial de un objeto encontrado por parte de un estudiante (RF06).
    Nace PENDIENTE y pasa a APROBADA o RECHAZADA con la decisión del encargado.
    """

    __tablename__ = "reclamacion"
    __table_args__ = (
        # Un objeto solo puede tener UNA reclamación aprobada: no se le puede
        # entregar a dos personas. Es un índice único parcial de SQLite.
        Index(
            "ux_reclamacion_una_aprobada_por_objeto",
            "objeto_id",
            unique=True,
            sqlite_where=CheckConstraint("estado = 'APROBADA'").sqltext,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiante.id"))
    objeto_id: Mapped[int] = mapped_column(ForeignKey("objeto.id"))
    # Encargado que registró la reclamación.
    encargado_id: Mapped[int] = mapped_column(ForeignKey("encargado.id"))
    estado: Mapped[EstadoReclamacion] = mapped_column(
        columna_enum(EstadoReclamacion, "estado_reclamacion"),
        default=EstadoReclamacion.PENDIENTE,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    estudiante: Mapped["Estudiante"] = relationship(back_populates="reclamaciones")
    objeto: Mapped["Objeto"] = relationship(back_populates="reclamaciones")
    encargado: Mapped["Encargado"] = relationship()
    informacion: Mapped["InformacionReclamante | None"] = relationship(back_populates="reclamacion")
    decision: Mapped["Decision | None"] = relationship(back_populates="reclamacion")
    entrega: Mapped["Entrega | None"] = relationship(back_populates="reclamacion")


class InformacionReclamante(Base):
    """
    Lo que el estudiante describe para demostrar que el objeto es suyo (RF07).
    Se muestra junto a las características del objeto para compararlas (RF09).
    """

    __tablename__ = "informacion_reclamante"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True: cada reclamación tiene una sola información del reclamante.
    reclamacion_id: Mapped[int] = mapped_column(ForeignKey("reclamacion.id"), unique=True)
    caracteristicas: Mapped[str] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(Text)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    reclamacion: Mapped["Reclamacion"] = relationship(back_populates="informacion")


class Decision(Base):
    """
    Decisión manual del encargado sobre una reclamación (RF10–RF14).
    Es un registro histórico: guarda quién decidió, qué, por qué y cuándo (RNF-05).
    """

    __tablename__ = "decision"
    __table_args__ = (
        # El motivo es obligatorio y no puede ser solo espacios (RF12).
        CheckConstraint("length(trim(motivo)) > 0", name="ck_decision_motivo_no_vacio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True: una reclamación se decide una sola vez.
    reclamacion_id: Mapped[int] = mapped_column(ForeignKey("reclamacion.id"), unique=True)
    # Encargado responsable, asignado automáticamente desde la sesión (RF13).
    encargado_id: Mapped[int] = mapped_column(ForeignKey("encargado.id"))
    resultado: Mapped[ResultadoDecision] = mapped_column(
        columna_enum(ResultadoDecision, "resultado_decision")
    )
    motivo: Mapped[str] = mapped_column(Text)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=ahora)  # RF14

    reclamacion: Mapped["Reclamacion"] = relationship(back_populates="decision")
    encargado: Mapped["Encargado"] = relationship()


class Entrega(Base):
    """
    Entrega del objeto a su dueño, solo para reclamaciones aprobadas (RF15).
    Al registrarla, el objeto pasa a ENTREGADO (RF16).
    """

    __tablename__ = "entrega"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True: una reclamación aprobada genera como máximo una entrega.
    reclamacion_id: Mapped[int] = mapped_column(ForeignKey("reclamacion.id"), unique=True)
    # Encargado que entregó el objeto, asignado automáticamente desde la sesión.
    encargado_id: Mapped[int] = mapped_column(ForeignKey("encargado.id"))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=ahora)
    observaciones: Mapped[str | None] = mapped_column(Text)

    reclamacion: Mapped["Reclamacion"] = relationship(back_populates="entrega")
    encargado: Mapped["Encargado"] = relationship()
