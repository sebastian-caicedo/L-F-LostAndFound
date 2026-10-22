"""
Verifica que la base de datos funcione y que sus restricciones protejan los datos.

Uso (desde backend/, con el entorno virtual activo y después de python seed.py):

    python verificar_bd.py

Hace dos tipos de pruebas:
1. Que los datos de prueba existan y las relaciones entre tablas funcionen.
2. Que la base RECHACE datos inválidos (cada intento se deshace, así que no
   modifica los datos de prueba).

Las pruebas automatizadas completas del backend se harán con pytest en la Fase 6.
"""

import sys

from sqlalchemy import distinct, func, select
from sqlalchemy.exc import IntegrityError

from app import fotos
from app.database import SessionLocal
from app.models import (
    Decision,
    Encargado,
    Entrega,
    EstadoObjeto,
    EstadoReclamacion,
    Incidente,
    InformacionReclamante,
    Objeto,
    Persona,
    Reclamacion,
    ResultadoDecision,
    TipoPersona,
    TipoRegistro,
)

fallos = 0


def resultado(ok: bool, descripcion: str) -> None:
    global fallos
    if not ok:
        fallos += 1
    print(f"  [{'OK' if ok else 'FALLA'}] {descripcion}")


def debe_rechazar(descripcion: str, crear_registro) -> None:
    """Intenta guardar un registro inválido. La prueba pasa si la base lo rechaza."""
    with SessionLocal() as db:
        try:
            db.add(crear_registro(db))
            db.flush()
            resultado(False, f"{descripcion} (la base lo aceptó)")
        except IntegrityError:
            resultado(True, descripcion)
        finally:
            db.rollback()


def primer(db, modelo):
    return db.scalar(select(modelo).limit(1))


def encargado_id(db) -> int:
    return primer(db, Encargado).id


def main() -> None:
    print("1. Datos de prueba y relaciones")
    with SessionLocal() as db:
        conteos = {
            "encargado": (Encargado, 1),
            "persona": (Persona, 5),
            "objeto": (Objeto, 8),
            "reclamacion": (Reclamacion, 7),
            "informacion_reclamante": (InformacionReclamante, 7),
            "decision": (Decision, 6),
            "entrega": (Entrega, 2),
            "incidente": (Incidente, 1),
        }
        for tabla, (modelo, esperado) in conteos.items():
            total = db.scalar(select(func.count()).select_from(modelo))
            resultado(total == esperado, f"Tabla {tabla}: {total} registros (esperados {esperado})")

        docentes = db.scalar(
            select(func.count()).select_from(Persona).where(Persona.tipo == TipoPersona.DOCENTE)
        )
        resultado(docentes == 1, "Hay 1 docente registrado (RF19)")

        entregas = db.scalars(select(Entrega)).all()
        resultado(
            all(
                e.reclamacion.decision.resultado == ResultadoDecision.APROBADA
                and e.reclamacion.objeto.estado == EstadoObjeto.ENTREGADO
                and fotos.ruta_foto(fotos.CARPETA_ENTREGAS, e.foto_evidencia).is_file()
                for e in entregas
            ),
            "Cada entrega tiene decisión aprobada, objeto ENTREGADO y foto de evidencia (RF22)",
        )

        celular = db.scalar(select(Objeto).where(Objeto.tipo == "Celular"))
        resultado(
            celular.foto is not None
            and fotos.ruta_foto(fotos.CARPETA_OBJETOS, celular.foto).is_file(),
            "El celular tiene su foto guardada en la carpeta de fotos (RF20)",
        )

        incidente = primer(db, Incidente)
        resultado(
            incidente.entrega.reclamacion.objeto.estado == EstadoObjeto.ENTREGADO
            and incidente.propietario_real.tipo == TipoPersona.DOCENTE,
            "El incidente apunta a una entrega, el objeto sigue ENTREGADO y tiene dueño real (RF23)",
        )

        # RF24: personas con 3 o más reclamaciones rechazadas de objetos distintos.
        sospechosos = db.execute(
            select(Persona.nombre, func.count(distinct(Reclamacion.objeto_id)))
            .join(Reclamacion, Reclamacion.persona_id == Persona.id)
            .where(Reclamacion.estado == EstadoReclamacion.RECHAZADA)
            .group_by(Persona.id)
            .having(func.count(distinct(Reclamacion.objeto_id)) >= 3)
        ).all()
        resultado(
            len(sospechosos) == 1 and sospechosos[0][0] == "Pedro Intento Díaz",
            f"La consulta de la alerta RF24 encuentra a {sospechosos}",
        )

    print("2. La base rechaza datos inválidos")

    def persona_base(**cambios):
        datos = dict(
            tipo=TipoPersona.ESTUDIANTE, nombre="Prueba", codigo="T09999999",
            carrera="Carrera", correo="nuevo@example.com", telefono="3000000000",
        )
        datos.update(cambios)
        return Persona(**datos)

    debe_rechazar("Estudiante con código de formato inválido",
                  lambda db: persona_base(codigo="12345"))
    debe_rechazar("Estudiante sin código",
                  lambda db: persona_base(codigo=None))
    debe_rechazar("Estudiante sin carrera (RNF-04)",
                  lambda db: persona_base(carrera=None))
    debe_rechazar("Docente con código o carrera",
                  lambda db: persona_base(tipo=TipoPersona.DOCENTE, codigo=None))
    debe_rechazar("Persona con código repetido",
                  lambda db: persona_base(codigo="T00000001"))
    debe_rechazar("Persona con correo repetido",
                  lambda db: persona_base(correo="ana.prueba@example.com"))
    debe_rechazar("Persona sin teléfono",
                  lambda db: persona_base(telefono=None))

    def objeto_base(db, **cambios):
        datos = dict(
            tipo_registro=TipoRegistro.ENCONTRADO, tipo="Llaves", descripcion="Llavero",
            caracteristicas="Tres llaves", estado=EstadoObjeto.DISPONIBLE,
            encargado_id=encargado_id(db),
        )
        datos.update(cambios)
        return Objeto(**datos)

    debe_rechazar("Objeto perdido sin persona que lo reporte",
                  lambda db: objeto_base(db, tipo_registro=TipoRegistro.PERDIDO,
                                         estado=EstadoObjeto.PERDIDO))
    debe_rechazar("Objeto encontrado con estado PERDIDO (estado incoherente)",
                  lambda db: objeto_base(db, estado=EstadoObjeto.PERDIDO))

    debe_rechazar(
        "Reclamación con una persona que no existe (RNF-03)",
        lambda db: Reclamacion(persona_id=9999, objeto_id=primer(db, Objeto).id,
                               encargado_id=encargado_id(db)),
    )
    debe_rechazar(
        "Segunda reclamación APROBADA para el mismo objeto",
        lambda db: Reclamacion(
            persona_id=primer(db, Persona).id,
            objeto_id=db.scalar(select(Reclamacion.objeto_id)
                                .where(Reclamacion.estado == EstadoReclamacion.APROBADA)),
            encargado_id=encargado_id(db),
            estado=EstadoReclamacion.APROBADA,
        ),
    )
    debe_rechazar(
        "Decisión con motivo vacío (RF12)",
        lambda db: Decision(
            reclamacion_id=db.scalar(select(Reclamacion.id)
                                     .where(Reclamacion.estado == EstadoReclamacion.PENDIENTE)),
            encargado_id=encargado_id(db), resultado=ResultadoDecision.RECHAZADA, motivo="   ",
        ),
    )
    debe_rechazar(
        "Segunda decisión para una reclamación ya decidida",
        lambda db: Decision(
            reclamacion_id=primer(db, Decision).reclamacion_id, encargado_id=encargado_id(db),
            resultado=ResultadoDecision.APROBADA, motivo="Intento duplicado",
        ),
    )
    debe_rechazar(
        "Entrega sin foto de evidencia (RF22)",
        lambda db: Entrega(
            reclamacion_id=db.scalar(select(Reclamacion.id)
                                     .where(Reclamacion.estado == EstadoReclamacion.PENDIENTE)),
            encargado_id=encargado_id(db),
        ),
    )
    debe_rechazar(
        "Incidente sin explicar cómo obtuvo el objeto (RF23)",
        lambda db: Incidente(
            entrega_id=db.scalar(select(Entrega.id).where(~Entrega.incidente.has())),
            encargado_id=encargado_id(db), como_lo_obtuvo=" ", medida_mejora="Una medida",
        ),
    )
    debe_rechazar(
        "Segundo incidente para la misma entrega",
        lambda db: Incidente(
            entrega_id=primer(db, Incidente).entrega_id, encargado_id=encargado_id(db),
            como_lo_obtuvo="Duplicado", medida_mejora="Duplicado",
        ),
    )

    print()
    if fallos:
        print(f"Resultado: {fallos} verificación(es) fallaron.")
        sys.exit(1)
    print("Resultado: todas las verificaciones pasaron.")


if __name__ == "__main__":
    main()
