"""
Crea la base de datos de L&F desde cero y la llena con datos de PRUEBA.

Uso (desde la carpeta backend/, con el entorno virtual activo):

    python seed.py

ATENCIÓN: borra todas las tablas, las vuelve a crear y borra las fotos de la
carpeta de fotos. Úsalo solo en desarrollo.

Todos los datos son inventados. No corresponden a personas reales ni a la
base de datos de la universidad. Los correos usan el dominio example.com,
reservado para ejemplos, y las fotos son imágenes de un solo color generadas
aquí mismo: nunca se usan fotos de personas reales.

La contraseña del encargado de prueba se toma de la variable
SEED_ENCARGADO_PASSWORD del archivo .env, para no dejarla escrita en el código.
"""

import os
import struct
import sys
import zlib
from datetime import date, datetime

from app import config, fotos
from app.database import Base, SessionLocal, crear_tablas, engine
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
from app.security import hashear_password


def imagen_de_prueba(rojo: int, verde: int, azul: int, ancho: int = 64, alto: int = 64) -> bytes:
    """Genera una imagen PNG de un solo color. Sirve como foto de prueba."""

    def bloque(tipo: bytes, datos: bytes) -> bytes:
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))

    fila = b"\x00" + bytes([rojo, verde, azul]) * ancho
    return (
        b"\x89PNG\r\n\x1a\n"
        + bloque(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
        + bloque(b"IDAT", zlib.compress(fila * alto))
        + bloque(b"IEND", b"")
    )


def limpiar_fotos() -> None:
    """Borra las fotos de pruebas anteriores, para que no queden archivos huérfanos."""
    for carpeta in (fotos.CARPETA_OBJETOS, fotos.CARPETA_ENTREGAS):
        ruta = config.UPLOADS_DIR / carpeta
        if ruta.is_dir():
            for archivo in ruta.iterdir():
                if archivo.is_file():
                    archivo.unlink()


def main() -> None:
    password = os.getenv("SEED_ENCARGADO_PASSWORD")
    if not password:
        sys.exit(
            "Falta SEED_ENCARGADO_PASSWORD en el archivo .env. "
            "Cópiala desde .env.example y asígnale una contraseña de prueba."
        )

    # Reinicia la base y la carpeta de fotos.
    Base.metadata.drop_all(bind=engine)
    crear_tablas()
    limpiar_fotos()

    with SessionLocal() as db:
        # --- Encargado (RF01) ---
        encargado = Encargado(
            nombre="Encargado de Prueba",
            usuario="encargado",
            password_hash=hashear_password(password),
        )
        db.add(encargado)

        # --- Personas: estudiantes (RF02) y un docente (RF19) ---
        def estudiante(nombre, codigo, carrera, correo, telefono):
            return Persona(
                tipo=TipoPersona.ESTUDIANTE, nombre=nombre, codigo=codigo,
                carrera=carrera, correo=correo, telefono=telefono,
            )

        ana = estudiante("Ana Prueba Gómez", "T00000001", "Ingeniería de Sistemas",
                         "ana.prueba@example.com", "3000000001")
        luis = estudiante("Luis Ejemplo Torres", "T00000002", "Ingeniería Industrial",
                          "luis.ejemplo@example.com", "3000000002")
        maria = estudiante("María Demo Ruiz", "T00000003", "Psicología",
                           "maria.demo@example.com", "3000000003")
        # Persona con varias reclamaciones rechazadas: activa la alerta del RF24.
        pedro = estudiante("Pedro Intento Díaz", "T00000004", "Contaduría Pública",
                           "pedro.intento@example.com", "3000000004")
        carlos = Persona(
            tipo=TipoPersona.DOCENTE, nombre="Carlos Docente Pérez",
            correo="carlos.docente@example.com", telefono="3000000009",
        )
        db.add_all([ana, luis, maria, pedro, carlos])
        db.flush()  # Asigna los id para poder usarlos abajo.

        # --- Objetos perdidos (RF03) ---
        def perdido(tipo, descripcion, caracteristicas, fecha, persona):
            return Objeto(
                tipo_registro=TipoRegistro.PERDIDO, estado=EstadoObjeto.PERDIDO,
                tipo=tipo, descripcion=descripcion, caracteristicas=caracteristicas,
                fecha_reporte=fecha, persona=persona, encargado=encargado,
            )

        cuaderno = perdido("Cuaderno", "Cuaderno argollado de cálculo",
                           "Tapa azul, stickers de planetas, nombre escrito en la primera hoja",
                           date(2026, 10, 1), ana)
        termo = perdido("Termo", "Termo metálico para café",
                        "Gris con una abolladura en la base y un sticker de montaña",
                        date(2026, 10, 3), carlos)

        # --- Objetos encontrados (RF04) ---
        def encontrado(tipo, descripcion, caracteristicas, fecha, lugar, estado=EstadoObjeto.DISPONIBLE):
            return Objeto(
                tipo_registro=TipoRegistro.ENCONTRADO, estado=estado,
                tipo=tipo, descripcion=descripcion, caracteristicas=caracteristicas,
                fecha_encontrado=fecha, lugar_encontrado=lugar, encargado=encargado,
            )

        celular = encontrado("Celular", "Teléfono inteligente con forro",
                             "Forro negro con grieta en la esquina, fondo de pantalla de un gato",
                             date(2026, 10, 2), "Biblioteca, segundo piso")
        # Foto de prueba del celular (RF20).
        celular.foto = fotos.guardar_foto(imagen_de_prueba(40, 40, 40), fotos.CARPETA_OBJETOS)

        billetera = encontrado("Billetera", "Billetera de cuero",
                               "Café oscuro, cierre dañado, carné de gimnasio adentro",
                               date(2026, 9, 28), "Cafetería central", EstadoObjeto.ENTREGADO)
        audifonos = encontrado("Audífonos", "Audífonos inalámbricos en estuche",
                               "Estuche blanco con iniciales grabadas",
                               date(2026, 10, 5), "Salón A-204")
        sombrilla = encontrado("Sombrilla", "Sombrilla plegable",
                               "Roja con mango de madera y una cinta verde amarrada",
                               date(2026, 10, 6), "Entrada principal", EstadoObjeto.ENTREGADO)
        calculadora = encontrado("Calculadora", "Calculadora científica",
                                 "Tapa con el nombre raspado y una pila de repuesto en el compartimiento",
                                 date(2026, 10, 7), "Laboratorio de física")

        # El docente reporta después que perdió una sombrilla: sus coincidencias
        # muestran la sombrilla que ya se entregó a otra persona (RF26).
        sombrilla_perdida = perdido("Sombrilla", "Sombrilla roja",
                                    "Roja, mango de madera y una cinta verde amarrada en la punta",
                                    date(2026, 10, 8), carlos)

        db.add_all([cuaderno, termo, celular, billetera, audifonos, sombrilla, calculadora,
                    sombrilla_perdida])
        db.flush()

        # --- Reclamaciones ---
        def reclamacion(persona, objeto, descripcion, estado=EstadoReclamacion.PENDIENTE,
                        fecha=None, observaciones=None):
            rec = Reclamacion(persona=persona, objeto=objeto, encargado=encargado, estado=estado)
            if fecha:
                rec.fecha_creacion = fecha
            db.add(rec)
            db.add(InformacionReclamante(
                reclamacion=rec, caracteristicas=descripcion, observaciones=observaciones,
            ))
            return rec

        def decidir(rec, resultado, motivo, fecha):
            db.add(Decision(
                reclamacion=rec, encargado=encargado, resultado=resultado,
                motivo=motivo, fecha_hora=fecha,
            ))

        # Caso 1: reclamación pendiente de revisión (RF06, RF07, RF08).
        reclamacion(maria, celular,
                    "Forro negro, la esquina superior está rota y el fondo es un gato gris",
                    observaciones="Dice que lo dejó en la biblioteca el jueves")

        # Caso 2: reclamación aprobada y entregada (RF10, RF12–RF16, RF22).
        rec_billetera = reclamacion(luis, billetera,
                                    "Billetera café con el cierre dañado y un carné de gimnasio",
                                    EstadoReclamacion.APROBADA, datetime(2026, 9, 29, 9, 15))
        decidir(rec_billetera, ResultadoDecision.APROBADA,
                "Describió el cierre dañado y el carné de gimnasio, que no eran visibles",
                datetime(2026, 9, 29, 9, 30))
        db.add(Entrega(
            reclamacion=rec_billetera, encargado=encargado,
            fecha_hora=datetime(2026, 9, 29, 9, 35),
            foto_evidencia=fotos.guardar_foto(imagen_de_prueba(120, 80, 40), fotos.CARPETA_ENTREGAS),
            observaciones="Se verificó el carné estudiantil al entregar",
        ))

        # Caso 3: reclamación rechazada (RF11, RF12–RF14).
        rec_audifonos = reclamacion(ana, audifonos, "Audífonos negros sin estuche",
                                    EstadoReclamacion.RECHAZADA, datetime(2026, 10, 6, 14, 0))
        decidir(rec_audifonos, ResultadoDecision.RECHAZADA,
                "El color y el estuche no coinciden con el objeto registrado",
                datetime(2026, 10, 6, 14, 10))

        # Caso 4: entrega que después resultó fraudulenta (RF23).
        rec_sombrilla = reclamacion(maria, sombrilla, "Sombrilla roja con mango de madera",
                                    EstadoReclamacion.APROBADA, datetime(2026, 10, 7, 8, 0))
        decidir(rec_sombrilla, ResultadoDecision.APROBADA,
                "Describió el color y el mango correctamente", datetime(2026, 10, 7, 8, 10))
        entrega_sombrilla = Entrega(
            reclamacion=rec_sombrilla, encargado=encargado,
            fecha_hora=datetime(2026, 10, 7, 8, 15),
            foto_evidencia=fotos.guardar_foto(imagen_de_prueba(200, 30, 30), fotos.CARPETA_ENTREGAS),
        )
        db.add(entrega_sombrilla)
        db.add(Incidente(
            entrega=entrega_sombrilla, encargado=encargado, propietario_real=carlos,
            como_lo_obtuvo="Describió solo el color y el mango, que se ven a simple vista desde "
                           "el mostrador. No mencionó la cinta verde amarrada.",
            medida_mejora="Guardar los objetos fuera de la vista del reclamante y exigir al menos "
                          "un rasgo que no sea visible a simple vista.",
            fecha_hora=datetime(2026, 10, 8, 10, 0),
        ))

        # Caso 5: persona con 3 reclamaciones rechazadas de objetos distintos (RF24).
        for objeto, descripcion, dia in (
            (audifonos, "Audífonos con cable, de color rojo", 8),
            (celular, "Celular sin forro, pantalla rota", 9),
            (calculadora, "Calculadora gráfica nueva, sin marcas", 10),
        ):
            rec = reclamacion(pedro, objeto, descripcion, EstadoReclamacion.RECHAZADA,
                              datetime(2026, 10, dia, 11, 0))
            decidir(rec, ResultadoDecision.RECHAZADA,
                    "La descripción no coincide con las características registradas",
                    datetime(2026, 10, dia, 11, 5))

        db.commit()

    print("Base de datos creada y poblada con datos de prueba.")
    print("  1 encargado (usuario: encargado), 4 estudiantes, 1 docente, 8 objetos,")
    print("  7 reclamaciones (1 pendiente, 2 aprobadas, 4 rechazadas), 2 entregas, 1 incidente.")


if __name__ == "__main__":
    main()
