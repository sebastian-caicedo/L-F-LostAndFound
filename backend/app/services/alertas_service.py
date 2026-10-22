"""
Alerta de reclamaciones fallidas (RF24).

Una persona genera alerta cuando tiene 3 o más reclamaciones RECHAZADAS de
objetos distintos (el número se configura con UMBRAL_ALERTA_RECHAZOS).

No hay una tabla de alertas: se calcula con las reclamaciones que ya existen.
Así la alerta siempre está al día y no hay que sincronizar nada.

Se cuentan objetos DISTINTOS porque reclamar varias veces el mismo objeto
puede ser un dueño insistente; intentar con muchos objetos diferentes es lo
que hace sospechar. La alerta solo informa: la decisión sigue siendo del
encargado (la decisión automática está fuera del alcance).
"""

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app import config
from app.models import EstadoReclamacion, Persona, Reclamacion
from app.schemas.alertas import AlertaOut


def _consulta_rechazos():
    """Cuenta, por persona, los objetos distintos con reclamación rechazada."""
    return (
        select(
            Reclamacion.persona_id,
            func.count(distinct(Reclamacion.objeto_id)).label("rechazos"),
        )
        .where(Reclamacion.estado == EstadoReclamacion.RECHAZADA)
        .group_by(Reclamacion.persona_id)
    )


def construir_alerta(rechazos: int) -> AlertaOut:
    activa = rechazos >= config.UMBRAL_ALERTA_RECHAZOS
    mensaje = (
        f"Atención: esta persona tiene {rechazos} reclamaciones rechazadas de objetos "
        "distintos. Verifica con especial cuidado."
        if activa
        else None
    )
    return AlertaOut(rechazos_objetos_distintos=rechazos, activa=activa, mensaje=mensaje)


def rechazos_de(db: Session, persona_id: int) -> int:
    fila = db.execute(_consulta_rechazos().where(Reclamacion.persona_id == persona_id)).first()
    return fila[1] if fila else 0


def alerta_de(db: Session, persona_id: int) -> AlertaOut:
    return construir_alerta(rechazos_de(db, persona_id))


def rechazos_por_persona(db: Session, ids: set[int]) -> dict[int, int]:
    """Rechazos de varias personas en una sola consulta (para listas)."""
    if not ids:
        return {}
    filas = db.execute(_consulta_rechazos().where(Reclamacion.persona_id.in_(ids))).all()
    return {persona_id: total for persona_id, total in filas}


def personas_con_alerta(db: Session) -> list[tuple[Persona, int]]:
    """Personas que hoy tienen la alerta activa, de más a menos rechazos."""
    subconsulta = _consulta_rechazos().having(
        func.count(distinct(Reclamacion.objeto_id)) >= config.UMBRAL_ALERTA_RECHAZOS
    ).subquery()
    filas = db.execute(
        select(Persona, subconsulta.c.rechazos)
        .join(subconsulta, subconsulta.c.persona_id == Persona.id)
        .order_by(subconsulta.c.rechazos.desc(), Persona.nombre)
    ).all()
    return [(persona, total) for persona, total in filas]
