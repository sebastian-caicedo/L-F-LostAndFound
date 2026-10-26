"""
Configuración de la conexión a la base de datos SQLite.

Este módulo crea tres piezas que usa el resto del backend:

- engine: la conexión con el archivo SQLite.
- SessionLocal: fábrica de sesiones. Una sesión agrupa las operaciones
  (consultas, inserciones) que se confirman juntas con commit().
- Base: clase de la que heredan todos los modelos (tablas) en models.py.

La ruta de la base se lee de la variable DATABASE_URL del archivo .env,
para no dejarla escrita en el código (ver .env.example).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Carga las variables del archivo .env (si existe) en el entorno.
load_dotenv()

# Si no hay .env, se usa un archivo lf.db en la carpeta desde donde se ejecuta.
# Se lee aquí directamente (y no desde config.py) para que seed.py y
# verificar_bd.py funcionen sin necesitar la SECRET_KEY.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lf.db")

engine = create_engine(
    DATABASE_URL,
    # SQLite por defecto solo permite usar una conexión en el hilo que la creó.
    # FastAPI atiende peticiones en varios hilos, por eso se desactiva esa
    # verificación. Cada petición usará su propia sesión.
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def activar_llaves_foraneas(conexion_dbapi, _registro):
    """
    SQLite NO valida las llaves foráneas a menos que se active en cada conexión.
    Sin esto, se podría guardar una reclamación con un estudiante que no existe,
    lo que viola el RNF-03 (integridad).
    """
    cursor = conexion_dbapi.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


@event.listens_for(engine, "connect")
def registrar_sin_tildes(conexion_dbapi, _registro):
    """
    Registra en SQLite la función sin_tildes() para buscar sin importar tildes
    ni mayúsculas. SQLite no trae esta función: se le "presta" la de Python
    (app/texto.py) y así se puede usar dentro de las consultas.
    """
    from app.texto import sin_tildes

    conexion_dbapi.create_function("sin_tildes", 1, sin_tildes, deterministic=True)


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase base de todos los modelos de la base de datos."""


def crear_tablas() -> None:
    """Crea en la base todas las tablas definidas en models.py que aún no existan."""
    # Se importa aquí para que los modelos queden registrados en Base antes de crear.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
