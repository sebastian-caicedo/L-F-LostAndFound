"""
Verifica que la base de datos funcione y que sus restricciones protejan los datos.

Uso (desde backend/, con el entorno virtual activo y después de python seed.py):

    python verificar_bd.py

Hace dos tipos de pruebas:
1. Que los datos de prueba existan y las relaciones entre tablas funcionen.
2. Que la base RECHACE datos inválidos (cada intento se deshace, así que no
   modifica los datos de prueba).

Es una verificación de la Fase 2. Las pruebas automatizadas completas del
backend se harán con pytest en la Fase 6.
"""

import sys

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import (
    Decision,
    Encargado,
    EstadoObjeto,
    EstadoReclamacion,
    Estudiante,
    Entrega,
    InformacionReclamante,
    Objeto,
    Reclamacion,
    ResultadoDecision,
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


def main() -> None:
    print("1. Datos de prueba y relaciones")
    with SessionLocal() as db:
        conteos = {
            "encargado": (Encargado, 1),
            "estudiante": (Estudiante, 3),
            "objeto": (Objeto, 5),
            "reclamacion": (Reclamacion, 3),
            "informacion_reclamante": (InformacionReclamante, 3),
            "decision": (Decision, 2),
            "entrega": (Entrega, 1),
        }
        for tabla, (modelo, esperado) in conteos.items():
            total = db.scalar(select(func.count()).select_from(modelo))
            resultado(total == esperado, f"Tabla {tabla}: {total} registros (esperados {esperado})")

        aprobada = db.scalar(
            select(Reclamacion).where(Reclamacion.estado == EstadoReclamacion.APROBADA)
        )
        resultado(
            aprobada is not None
            and aprobada.decision.resultado == ResultadoDecision.APROBADA
            and aprobada.entrega is not None
            and aprobada.objeto.estado == EstadoObjeto.ENTREGADO,
            "Reclamación aprobada -> decisión, entrega y objeto ENTREGADO enlazados",
        )
        pendientes = db.scalars(
            select(Reclamacion).where(Reclamacion.estado == EstadoReclamacion.PENDIENTE)
        ).all()
        resultado(
            len(pendientes) == 1 and pendientes[0].informacion is not None,
            "Hay 1 reclamación pendiente con su información del reclamante (RF08)",
        )

    print("2. La base rechaza datos inválidos")

    def primer(db, modelo):
        return db.scalar(select(modelo).limit(1))

    debe_rechazar(
        "Decisión con motivo vacío (RF12)",
        lambda db: Decision(
            reclamacion_id=db.scalar(
                select(Reclamacion.id).where(Reclamacion.estado == EstadoReclamacion.PENDIENTE)
            ),
            encargado_id=primer(db, Encargado).id,
            resultado=ResultadoDecision.RECHAZADA,
            motivo="   ",
        ),
    )
    debe_rechazar(
        "Segunda decisión para una reclamación ya decidida",
        lambda db: Decision(
            reclamacion_id=primer(db, Decision).reclamacion_id,
            encargado_id=primer(db, Encargado).id,
            resultado=ResultadoDecision.APROBADA,
            motivo="Intento duplicado",
        ),
    )
    debe_rechazar(
        "Reclamación con un estudiante que no existe (RNF-03)",
        lambda db: Reclamacion(
            estudiante_id=9999,
            objeto_id=primer(db, Objeto).id,
            encargado_id=primer(db, Encargado).id,
        ),
    )
    debe_rechazar(
        "Segunda reclamación APROBADA para el mismo objeto",
        lambda db: Reclamacion(
            estudiante_id=primer(db, Estudiante).id,
            objeto_id=db.scalar(
                select(Reclamacion.objeto_id).where(
                    Reclamacion.estado == EstadoReclamacion.APROBADA
                )
            ),
            encargado_id=primer(db, Encargado).id,
            estado=EstadoReclamacion.APROBADA,
        ),
    )
    debe_rechazar(
        "Objeto perdido sin estudiante que lo reporte",
        lambda db: Objeto(
            tipo_registro=TipoRegistro.PERDIDO,
            tipo="Llaves",
            descripcion="Llavero",
            caracteristicas="Tres llaves",
            estado=EstadoObjeto.PERDIDO,
            encargado_id=primer(db, Encargado).id,
        ),
    )
    debe_rechazar(
        "Objeto encontrado con estado PERDIDO (estado incoherente)",
        lambda db: Objeto(
            tipo_registro=TipoRegistro.ENCONTRADO,
            tipo="Llaves",
            descripcion="Llavero",
            caracteristicas="Tres llaves",
            estado=EstadoObjeto.PERDIDO,
            encargado_id=primer(db, Encargado).id,
        ),
    )
    debe_rechazar(
        "Estudiante con un código repetido",
        lambda db: Estudiante(
            nombre="Duplicado",
            codigo=primer(db, Estudiante).codigo,
            carrera="N/A",
            contacto="duplicado@example.com",
        ),
    )
    debe_rechazar(
        "Estudiante sin carrera (campo obligatorio, RNF-04)",
        lambda db: Estudiante(nombre="Sin carrera", codigo="T09999999", contacto="x@example.com"),
    )

    print()
    if fallos:
        print(f"Resultado: {fallos} verificación(es) fallaron.")
        sys.exit(1)
    print("Resultado: todas las verificaciones pasaron.")


if __name__ == "__main__":
    main()
