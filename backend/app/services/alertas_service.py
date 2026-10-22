"""
Alerta de reclamaciones fallidas (RF24).

Una persona genera alerta cuando tiene 3 o más reclamaciones RECHAZADAS de
objetos distintos (el número se configura con UMBRAL_ALERTA_RECHAZOS).

No hay una tabla de alertas: se calcula con las reclamaciones que ya existen.
Así la alerta siempre está al día y no hay que sincronizar nada.

Se cuentan objetos DISTINTOS porque reclamar varias veces el mismo objeto
puede ser un dueño insistente; intentar con muchos objetos diferentes es lo
que hace sospechar.

No cuenta el rechazo de un objeto del que después se comprobó que la persona
era el dueño real (un incidente la registra como propietario_real): ese
rechazo no fue un intento falso, sino una víctima del fraude. La alerta solo informa: la decisión sigue siendo del
encargado (la decisión automática está fuera del alcance).
"""

from sqlalchemy import and_, distinct, exists, func, select
from sqlalchemy.orm import Session, aliased

from app import config
from app.models import Entrega, EstadoReclamacion, Incidente, Persona, Reclamacion
from app.schemas.alertas import AlertaOut


def _reconocido_como_dueno():
    """
    Condición: existe un incidente sobre una entrega de este mismo objeto que
    reconoce a esta persona como dueña real.
    """
    reclamacion_entregada = aliased(Reclamacion)
    return exists().where(
        and_(
            Incidente.entrega_id == Entrega.id,
            Entrega.reclamacion_id == reclamacion_entregada.id,
            reclamacion_entregada.objeto_id == Reclamacion.objeto_id,
            Incidente.propietario_real_id == Reclamacion.persona_id,
        )
    )


def _consulta_rechazos():
    """Cuenta, por persona, los objetos distintos con reclamación rechazada."""
    return (
        select(
            Reclamacion.persona_id,
            func.count(distinct(Reclamacion.objeto_id)).label("rechazos"),
        )
        .where(Reclamacion.estado == EstadoReclamacion.RECHAZADA, ~_reconocido_como_dueno())
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
