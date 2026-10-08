"""
Crea la base de datos de L&F desde cero y la llena con datos de PRUEBA.

Uso (desde la carpeta backend/, con el entorno virtual activo):

    python seed.py

ATENCIÓN: borra todas las tablas y las vuelve a crear. Úsalo solo en desarrollo.

Todos los datos son inventados. No corresponden a personas reales ni a la
base de datos de la universidad. Los correos usan el dominio example.com,
reservado para ejemplos.

La contraseña del encargado de prueba se toma de la variable
SEED_ENCARGADO_PASSWORD del archivo .env, para no dejarla escrita en el código.
"""

import os
import sys
from datetime import date, datetime

import bcrypt

from app.database import Base, SessionLocal, crear_tablas, engine
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


def hashear(password: str) -> str:
    """Convierte una contraseña en un hash bcrypt. La contraseña nunca se guarda."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def main() -> None:
    password = os.getenv("SEED_ENCARGADO_PASSWORD")
    if not password:
        sys.exit(
            "Falta SEED_ENCARGADO_PASSWORD en el archivo .env. "
            "Cópiala desde .env.example y asígnale una contraseña de prueba."
        )

    # Reinicia la base: elimina las tablas existentes y las crea de nuevo.
    Base.metadata.drop_all(bind=engine)
    crear_tablas()

    with SessionLocal() as db:
        # --- Encargado (RF01) ---
        encargado = Encargado(
            nombre="Encargado de Prueba",
            usuario="encargado",
            password_hash=hashear(password),
        )
        db.add(encargado)

        # --- Estudiantes (RF02) ---
        ana = Estudiante(
            nombre="Ana Prueba Gómez",
            codigo="T00000001",
            carrera="Ingeniería de Sistemas",
            contacto="ana.prueba@example.com",
        )
        luis = Estudiante(
            nombre="Luis Ejemplo Torres",
            codigo="T00000002",
            carrera="Ingeniería Industrial",
            contacto="luis.ejemplo@example.com",
        )
        maria = Estudiante(
            nombre="María Demo Ruiz",
            codigo="T00000003",
            carrera="Psicología",
            contacto="maria.demo@example.com",
        )
        db.add_all([ana, luis, maria])
        db.flush()  # Asigna los id para poder usarlos abajo.

        # --- Objetos (RF03, RF04) ---
        # Un objeto reportado como perdido por Ana.
        cuaderno_perdido = Objeto(
            tipo_registro=TipoRegistro.PERDIDO,
            tipo="Cuaderno",
            descripcion="Cuaderno argollado de cálculo",
            caracteristicas="Tapa azul, stickers de planetas, nombre escrito en la primera hoja",
            estado=EstadoObjeto.PERDIDO,
            fecha_reporte=date(2026, 10, 1),
            estudiante=ana,
            encargado=encargado,
        )
        # Objetos encontrados.
        celular = Objeto(
            tipo_registro=TipoRegistro.ENCONTRADO,
            tipo="Celular",
            descripcion="Teléfono inteligente con forro",
            caracteristicas="Forro negro con grieta en la esquina, fondo de pantalla de un gato",
            estado=EstadoObjeto.DISPONIBLE,
            fecha_encontrado=date(2026, 10, 2),
            lugar_encontrado="Biblioteca, segundo piso",
            encargado=encargado,
        )
        billetera = Objeto(
            tipo_registro=TipoRegistro.ENCONTRADO,
            tipo="Billetera",
            descripcion="Billetera de cuero",
            caracteristicas="Café oscuro, cierre dañado, carné de gimnasio adentro",
            estado=EstadoObjeto.ENTREGADO,
            fecha_encontrado=date(2026, 9, 28),
            lugar_encontrado="Cafetería central",
            encargado=encargado,
        )
        audifonos = Objeto(
            tipo_registro=TipoRegistro.ENCONTRADO,
            tipo="Audífonos",
            descripcion="Audífonos inalámbricos en estuche",
            caracteristicas="Estuche blanco con iniciales grabadas",
            estado=EstadoObjeto.DISPONIBLE,
            fecha_encontrado=date(2026, 10, 5),
            lugar_encontrado="Salón A-204",
            encargado=encargado,
        )
        sombrilla = Objeto(
            tipo_registro=TipoRegistro.ENCONTRADO,
            tipo="Sombrilla",
            descripcion="Sombrilla plegable",
            caracteristicas="Roja con mango de madera",
            estado=EstadoObjeto.DISPONIBLE,
            fecha_encontrado=date(2026, 10, 6),
            lugar_encontrado="Entrada principal",
            encargado=encargado,
        )
        db.add_all([cuaderno_perdido, celular, billetera, audifonos, sombrilla])
        db.flush()

        # --- Caso 1: reclamación pendiente de revisión (RF06, RF07, RF08) ---
        rec_pendiente = Reclamacion(estudiante=maria, objeto=celular, encargado=encargado)
        db.add(rec_pendiente)
        db.add(
            InformacionReclamante(
                reclamacion=rec_pendiente,
                caracteristicas="Forro negro, la esquina superior está rota y el fondo es un gato gris",
                observaciones="Dice que lo dejó en la biblioteca el jueves",
            )
        )

        # --- Caso 2: reclamación aprobada y entregada (RF10, RF12–RF16) ---
        rec_aprobada = Reclamacion(
            estudiante=luis,
            objeto=billetera,
            encargado=encargado,
            estado=EstadoReclamacion.APROBADA,
            fecha_creacion=datetime(2026, 9, 29, 9, 15),
        )
        db.add(rec_aprobada)
        db.add(
            InformacionReclamante(
                reclamacion=rec_aprobada,
                caracteristicas="Billetera café con el cierre dañado y un carné de gimnasio",
            )
        )
        db.add(
            Decision(
                reclamacion=rec_aprobada,
                encargado=encargado,
                resultado=ResultadoDecision.APROBADA,
                motivo="Describió el cierre dañado y el carné de gimnasio, que no eran visibles",
                fecha_hora=datetime(2026, 9, 29, 9, 30),
            )
        )
        db.add(
            Entrega(
                reclamacion=rec_aprobada,
                encargado=encargado,
                fecha_hora=datetime(2026, 9, 29, 9, 35),
                observaciones="Se verificó el carné estudiantil al entregar",
            )
        )

        # --- Caso 3: reclamación rechazada (RF11, RF12–RF14) ---
        rec_rechazada = Reclamacion(
            estudiante=ana,
            objeto=audifonos,
            encargado=encargado,
            estado=EstadoReclamacion.RECHAZADA,
            fecha_creacion=datetime(2026, 10, 6, 14, 0),
        )
        db.add(rec_rechazada)
        db.add(
            InformacionReclamante(
                reclamacion=rec_rechazada,
                caracteristicas="Audífonos negros sin estuche",
            )
        )
        db.add(
            Decision(
                reclamacion=rec_rechazada,
                encargado=encargado,
                resultado=ResultadoDecision.RECHAZADA,
                motivo="El color y el estuche no coinciden con el objeto registrado",
                fecha_hora=datetime(2026, 10, 6, 14, 10),
            )
        )

        db.commit()

    print("Base de datos creada y poblada con datos de prueba.")
    print("  1 encargado (usuario: encargado), 3 estudiantes, 5 objetos, 3 reclamaciones.")


if __name__ == "__main__":
    main()
