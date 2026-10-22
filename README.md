# L&F — Lost And Found

Sistema web para la **gestión de objetos perdidos y encontrados en una institución universitaria**. El encargado registra estudiantes, docentes y objetos (con foto), gestiona reclamaciones, compara la información del reclamante con las características del objeto y decide si aprueba o rechaza. Cada decisión y cada entrega quedan registradas con trazabilidad completa.

**Estado:** MVP en desarrollo (Fase 3 — backend) · **Inicio:** 24/08/2026 · **Metodología:** Scrum con tablero Kanban

## Problema que resuelve

Sin un mecanismo centralizado, nadie sabe con certeza qué objetos fueron encontrados, dónde están ni cómo comprobar que quien los reclama es el dueño. L&F centraliza el registro y deja evidencia de cada decisión: quién la tomó, cuándo y por qué.

## Usuario

El **encargado de objetos perdidos** es el único usuario de la aplicación. Estudiantes y docentes no la usan directamente: el encargado registra sus datos cuando reportan una pérdida o reclaman un objeto en persona.

La decisión sobre cada reclamación es siempre del encargado. El sistema solo facilita la comparación entre el objeto y la información del reclamante.

## Flujo principal (MVP)

```text
Iniciar sesión → Registrar persona (estudiante o docente) → Registrar objeto (perdido / encontrado)
→ Registrar reclamación y características del reclamante → Revisar y comparar
→ Aprobar o rechazar (motivo obligatorio) → Registrar entrega con foto → Historial
```

### Reglas de negocio

- Aprobar o rechazar una reclamación exige un **motivo obligatorio**. El sistema registra automáticamente el **encargado responsable** y la **fecha y hora** de la decisión.
- La **entrega** solo se registra para reclamaciones **aprobadas** y actualiza el estado del objeto.
- Toda reclamación se asocia a una persona (estudiante o docente) y a un objeto existentes.
- El código estudiantil se guarda siempre con el formato de la universidad, `T` + 8 dígitos. El encargado puede escribir `t70496` y se guarda `T00070496`.
- La foto de un objeto encontrado no se muestra en una reclamación hasta registrar la descripción del reclamante.
- Si una entrega resulta fraudulenta, el objeto sigue `ENTREGADO` y se registra un incidente con cómo ocurrió y qué medida se propone.
- Una persona con **3 o más reclamaciones rechazadas** de objetos distintos genera una alerta para el encargado. La alerta no bloquea: la decisión sigue siendo del encargado.

## Requerimientos funcionales

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF01 | Autenticar al encargado con sus credenciales | Alta |
| RF02 | Registrar los datos del estudiante relacionado con un proceso (nombre, código, carrera, correo y teléfono) | Alta |
| RF03 | Registrar objetos perdidos y sus características | Alta |
| RF04 | Registrar objetos encontrados y sus características | Alta |
| RF05 | Consultar los objetos registrados | Alta |
| RF06 | Registrar reclamaciones asociando estudiante y objeto encontrado | Alta |
| RF07 | Registrar la información proporcionada por el reclamante | Alta |
| RF08 | Consultar reclamaciones pendientes de revisión | Alta |
| RF09 | Mostrar objeto y reclamante lado a lado para compararlos | Alta |
| RF10 | Aprobar una reclamación | Alta |
| RF11 | Rechazar una reclamación | Alta |
| RF12 | Exigir un motivo al aprobar o rechazar | Alta |
| RF13 | Registrar automáticamente el encargado responsable de la decisión | Media |
| RF14 | Registrar automáticamente fecha y hora de la decisión | Alta |
| RF15 | Registrar la entrega de un objeto con reclamación aprobada | Alta |
| RF16 | Actualizar el estado del objeto tras la entrega | Media |
| RF17 | Consultar el historial de reclamaciones y decisiones | Media |
| RF18 | Consultar el historial de entregas | Media |

### Ajuste de alcance (octubre de 2026)

Durante la Fase 3 el equipo amplió el alcance con estos requerimientos. Deben reflejarse también en el documento del Proyecto de Aula y en los diagramas UML.

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF19 | Registrar docentes como personas que reportan o reclaman objetos (nombre, correo institucional y teléfono) | Media |
| RF20 | Registrar y consultar la foto de un objeto | Media |
| RF21 | Ocultar la foto del objeto en una reclamación hasta registrar la descripción del reclamante | Media |
| RF22 | Registrar en la entrega una foto de la persona junto al objeto | Alta |
| RF23 | Registrar incidentes de entregas fraudulentas: cómo ocurrió, medida de mejora y dueño real | Media |
| RF24 | Alertar al encargado cuando una persona tiene 3 o más reclamaciones rechazadas de objetos distintos | Baja |
| RF25 | Editar los datos de un objeto no entregado, registrando quién y cuándo lo editó | Media |

## Requerimientos no funcionales

| ID | Atributo | Criterio |
|---|---|---|
| RNF-01 | Seguridad | Toda funcionalidad protegida rechaza a usuarios no autenticados |
| RNF-02 | Autorización | Las funciones del encargado rechazan a cualquier otro rol |
| RNF-03 | Integridad | Toda reclamación se asocia a una persona y a un objeto existentes |
| RNF-04 | Validación | Los campos obligatorios se validan antes de guardar |
| RNF-05 | Trazabilidad | Toda decisión guarda encargado, fecha, estado y motivo |
| RNF-06 | Usabilidad | Registrar un objeto perdido toma como máximo 3 minutos en pruebas |
| RNF-07 | Mantenibilidad | Código modular y pruebas automatizadas en funciones críticas |

## Fuera del alcance

IA para reconocer objetos o personas, decisión automática de reclamaciones, chat, pagos, geolocalización avanzada, reputación de usuarios, redes sociales, app móvil nativa, integraciones institucionales complejas y rol de supervisor.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Frontend | Astro |
| Backend | FastAPI (Python) |
| Base de datos | SQLite |
| Control de versiones | Git / GitHub |
| Gestión del proyecto | Tablero Kanban (Scrum) |

```text
Encargado → Frontend (Astro, :4321) → API HTTP → Backend (FastAPI, :8000) → SQLite
```

## Estructura del repositorio

```text
L-F-LostAndFound/
├── backend/                 # API en FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Punto de entrada de la API: CORS y registro de routers
│   │   ├── config.py        # Configuración leída del .env (SECRET_KEY, CORS, sesión)
│   │   ├── database.py      # Conexión a SQLite (lee DATABASE_URL del .env)
│   │   ├── models.py        # Tablas de la base de datos (SQLAlchemy)
│   │   ├── security.py      # Hash de contraseñas y tokens de sesión
│   │   ├── deps.py          # Dependencias comunes: sesión de BD y encargado autenticado
│   │   ├── errores.py       # Errores de negocio (404, 409, 422) con mensajes en español
│   │   ├── validaciones.py  # Normalización de código, correo, teléfono y fechas
│   │   ├── fotos.py         # Guardado y validación de fotos
│   │   ├── schemas/         # Datos que entran y salen de la API (Pydantic)
│   │   ├── services/        # Reglas de negocio
│   │   └── routers/         # Endpoints HTTP, uno por módulo
│   ├── peticiones/          # Peticiones de prueba (extensión REST Client)
│   ├── uploads/             # Fotos de objetos y entregas (no se sube al repositorio)
│   ├── seed.py              # Crea la base y carga datos de prueba
│   ├── verificar_bd.py      # Verifica relaciones y restricciones de la base
│   └── requirements.txt     # Dependencias de Python
├── frontend/                # Interfaz web en Astro
│   ├── public/              # Archivos estáticos (favicon)
│   ├── src/pages/           # Páginas de la aplicación
│   ├── astro.config.mjs
│   └── package.json
├── docs/                    # Documentación del proyecto
│   ├── diagramas/           # Diagramas UML
│   ├── modelo-datos.md      # Diseño de la base de datos
│   └── ...                  # Proyecto de Aula y hoja de ruta
├── .env.example             # Plantilla de variables de entorno (sin valores reales)
└── README.md
```

## Instalación y ejecución

### Requisitos

- Git
- Python 3.14.4
- Node.js 22.12 o superior y npm

### 1. Clonar el repositorio y configurar variables de entorno

```bash
git clone https://github.com/sebastian-caicedo/L-F-LostAndFound.git
cd L-F-LostAndFound
cp .env.example .env        # En Windows (cmd): copy .env.example .env
```

Completa los valores del archivo `.env`:

- `SECRET_KEY`: clave para firmar los tokens de sesión. Genérala con `python -c "import secrets; print(secrets.token_hex(32))"`. Sin ella, la API no arranca.
- `SEED_ENCARGADO_PASSWORD`: contraseña del encargado de prueba.

Ese archivo **no se sube al repositorio**: el repositorio solo contiene `.env.example`, sin credenciales reales.

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Activar el entorno virtual:
#   Windows:     venv\Scripts\activate
#   Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`. Para verificar que funciona, abre `http://localhost:8000/health`; debe responder `{"status": "ok"}`. La documentación interactiva de la API está en `http://localhost:8000/docs`: con el botón **Authorize** se inicia sesión y se pueden probar los endpoints protegidos.

### 3. Base de datos (SQLite)

Con el entorno virtual activo, desde `backend/`:

```bash
python seed.py          # Crea las tablas y carga datos de prueba (borra los datos anteriores)
python verificar_bd.py  # Comprueba relaciones y que se rechacen datos inválidos
```

Se crean el archivo `backend/lf.db` y la carpeta `backend/uploads/` con fotos de prueba; ninguno de los dos se sube al repositorio. El usuario de prueba es `encargado`, con la contraseña definida en `SEED_ENCARGADO_PASSWORD`. El diseño del modelo está en [`docs/modelo-datos.md`](docs/modelo-datos.md).

### 4. Frontend (Astro)

En otra terminal, desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

La interfaz queda disponible en `http://localhost:4321`.

## API

Todos los endpoints, excepto `/health` y `/auth/login`, requieren el token de sesión en el encabezado `Authorization: Bearer <token>`. La sesión dura 8 horas (`TOKEN_EXPIRE_HOURS`).

| Método | Ruta | Descripción | RF |
|---|---|---|---|
| GET | `/health` | Estado de la API | — |
| POST | `/auth/login` | Inicia sesión y devuelve el token | RF01 |
| GET | `/auth/me` | Datos del encargado con la sesión abierta | RF01 |
| POST | `/personas/estudiantes` | Registra un estudiante | RF02 |
| POST | `/personas/docentes` | Registra un docente | RF19 |
| GET | `/personas` | Lista personas; filtros `tipo` y `buscar` (nombre, código o correo) | RF02, RF19 |
| GET | `/personas/codigo/{codigo}` | Busca un estudiante por código | RF02 |
| GET | `/personas/{id}` | Datos de una persona | RF02, RF19 |
| POST | `/objetos/perdidos` | Registra un objeto perdido | RF03 |
| POST | `/objetos/encontrados` | Registra un objeto encontrado | RF04 |
| GET | `/objetos` | Consulta objetos; filtros `tipo_registro`, `estado`, `tipo` y `buscar` | RF05 |
| GET | `/objetos/{id}` | Detalle de un objeto | RF05 |
| PATCH | `/objetos/{id}` | Corrige datos de un objeto no entregado | RF25 |
| PUT | `/objetos/{id}/foto` | Sube o reemplaza la foto de un objeto (JPG, PNG o WEBP, máx. 5 MB) | RF20 |
| GET | `/objetos/{id}/foto` | Muestra la foto de un objeto | RF20 |

Las fotos no son públicas: solo se ven con sesión iniciada. La lista de objetos no muestra las características, que solo aparecen en el detalle.

En `backend/peticiones/` hay peticiones de prueba listas para la extensión REST Client de VS Code.

## Datos de prueba

La base de datos **no es la de la universidad**. Todos los datos que usa el sistema son de prueba, creados por el equipo con `backend/seed.py`. No se almacenan datos reales de personas: los correos usan el dominio reservado `example.com` y las fotos de prueba son imágenes de un solo color.

## Pruebas

Pendiente (Fase 6 de la hoja de ruta). Las pruebas cubrirán autenticación y permisos, validación de datos, reclamaciones aprobadas y rechazadas, motivo obligatorio, entregas, cambio de estado del objeto y trazabilidad.

## Hoja de ruta

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Repositorio y entorno de desarrollo | Completada |
| 2 | Diseño de la base de datos | Completada |
| 3 | Backend | En curso |
| 4 | Frontend | Pendiente |
| 5 | Integración | Pendiente |
| 6 | Calidad y pruebas | Pendiente |
| 7 | Documentación y entrega | Pendiente |

El detalle de cada fase está en la hoja de ruta dentro de [`docs/`](docs/).

## Documentación

En [`docs/`](docs/) se encuentran:

- El documento del Proyecto de Aula: historias de usuario, elicitación y decisiones de alcance.
- La hoja de ruta del proyecto.
- El modelo de datos en [`docs/modelo-datos.md`](docs/modelo-datos.md): diagrama entidad-relación, estados y reglas de integridad.
- Los diagramas UML en [`docs/diagramas/`](docs/diagramas/): casos de uso, clases, secuencia, actividades, componentes y despliegue.
- El diagrama de clases actualizado con el ajuste de alcance RF19–RF25 en [`docs/diagramas/diagrama-clases.md`](docs/diagramas/diagrama-clases.md).

## Equipo

**Sebastián Caicedo** · **Javier Carta**

Ingeniería de Software, séptimo semestre. Docente: Aisner José Marrugo Juliao.
