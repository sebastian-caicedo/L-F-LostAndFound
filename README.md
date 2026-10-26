# L&F — Lost And Found

Sistema web para la **gestión de objetos perdidos y encontrados en una institución universitaria**. El encargado registra estudiantes, docentes y objetos (con foto), gestiona reclamaciones, compara la información del reclamante con las características del objeto y decide si aprueba o rechaza. Cada decisión y cada entrega quedan registradas con trazabilidad completa.

**Estado:** MVP en desarrollo (Fase 5 — integración) · **Inicio:** 24/08/2026 · **Metodología:** Scrum con tablero Kanban

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
- Una persona con **3 o más reclamaciones rechazadas** de objetos distintos genera una alerta para el encargado. La alerta no bloquea: la decisión sigue siendo del encargado. No cuenta el rechazo de un objeto del que después se comprobó, mediante un incidente, que la persona era el dueño real.
- Un **reporte de pérdida** queda abierto 15 días desde que se registra (`DIAS_VIGENCIA_REPORTE`). Si en ese tiempo no se recupera el objeto, pasa a `VENCIDO`: sale de los reportes abiertos y de las coincidencias, pero **no se borra**, porque queda como evidencia. Si la persona sigue buscando, se registra un reporte nuevo.
- Las **búsquedas** y las **coincidencias** no distinguen tildes ni mayúsculas: `audifonos` encuentra `Audífonos` y `maria` encuentra a `María`. Los datos se guardan tal como se escribieron.
- Una reclamación se puede **vincular al reporte de pérdida** abierto de la misma persona. Al entregar el objeto, ese reporte se cierra como `RECUPERADO`.
- Se puede registrar la reclamación de un objeto **ya entregado**. No se puede aprobar, pero la comparación muestra a quién se entregó, cuándo, qué describió esa persona y con qué motivo se aprobó, para evaluar un posible fraude. Lo mismo muestran las coincidencias de un reporte de pérdida.

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
| RF24 | Alertar al encargado cuando una persona tiene 3 o más reclamaciones rechazadas de objetos distintos (sin contar objetos de los que se comprobó que era el dueño real) | Baja |
| RF25 | Editar los datos de un objeto no entregado, registrando quién y cuándo lo editó | Media |
| RF26 | Mostrar, al comparar una reclamación o al buscar coincidencias de un reporte de pérdida, si el objeto ya se entregó: a quién, cuándo, qué describió esa persona y con qué motivo se aprobó | Media |
| RF27 | Vincular una reclamación con el reporte de pérdida de la misma persona y cerrar ese reporte como recuperado al entregar el objeto | Media |
| RF28 | Mostrar coincidencias en las dos direcciones: para un objeto encontrado, los reportes de pérdida abiertos de la misma categoría | Media |
| RF29 | Vencer los reportes de pérdida que no se resuelven en 15 días (configurable), sin borrarlos | Media |

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
│   │   ├── texto.py         # Búsquedas sin importar tildes ni mayúsculas
│   │   ├── schemas/         # Datos que entran y salen de la API (Pydantic)
│   │   ├── services/        # Reglas de negocio
│   │   └── routers/         # Endpoints HTTP, uno por módulo
│   ├── peticiones/          # Peticiones de prueba (extensión REST Client)
│   ├── uploads/             # Fotos de objetos y entregas (no se sube al repositorio)
│   ├── seed.py              # Crea la base y carga datos de prueba
│   ├── verificar_bd.py      # Verifica relaciones y restricciones de la base
│   └── requirements.txt     # Dependencias de Python
├── frontend/                # Interfaz web en Astro (HTML, CSS y JavaScript, sin frameworks)
│   ├── public/              # Archivos estáticos (ícono)
│   ├── src/
│   │   ├── pages/           # Una página por pantalla (login, mostrador, objetos...)
│   │   │                    # Los detalles usan ?id=N: /objetos/detalle?id=5, /personas/detalle?id=2
│   │   ├── layouts/         # Base.astro (estructura HTML) y App.astro (encabezado y menú)
│   │   ├── components/      # Piezas reutilizables: pasos, buscar y registrar persona, selector de foto
│   │   ├── lib/             # JavaScript compartido
│   │   │   ├── api.js       # Llamadas a la API, token de sesión y mensajes de error
│   │   │   ├── ui.js        # Fechas, estados, mensajes y protección del texto
│   │   │   ├── pasos.js     # Flujos por pasos del mostrador
│   │   │   ├── persona.js   # Buscar o registrar personas y su alerta
│   │   │   ├── foto.js      # Cámara web o archivo
│   │   │   └── objetos.js   # Datos, fotos y entrega previa de un objeto
│   │   └── styles/global.css # Colores (azul y blanco) y estilos comunes
│   ├── astro.config.mjs     # Lee PUBLIC_API_URL del .env de la raíz
│   └── package.json
├── docs/                    # Documentación del proyecto
│   ├── diagramas/           # Diagramas UML
│   ├── avances/             # Resumen de cada fase: qué se hizo y cómo se verificó
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

El backend usa un **entorno virtual** (`venv`): una carpeta con su propia copia de Python y de las librerías del proyecto, para no mezclarlas con las de otros proyectos del computador. La carpeta `venv/` no se sube al repositorio; cada integrante la crea en su equipo.

**Primera vez** (crear el entorno e instalar las dependencias), desde la raíz del proyecto:

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

**Cada vez que abras una terminal nueva** hay que activar el entorno otra vez antes de usar el backend:

```bash
cd backend
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
uvicorn app.main:app --reload
```

- Sabrás que está activo porque la línea de la terminal empieza con `(venv)`.
- Para salir del entorno: `deactivate`.
- Si aparece `ModuleNotFoundError` (por ejemplo, `No module named 'dotenv'`), el entorno no está activo o faltan dependencias: actívalo y ejecuta `pip install -r requirements.txt`.
- Si PowerShell no deja activarlo ("la ejecución de scripts está deshabilitada"), ejecuta una sola vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo, o usa la terminal **cmd** en vez de PowerShell.
- Si borraste la carpeta `venv`, repite los pasos de **Primera vez**.

La API queda disponible en `http://localhost:8000`. Para verificar que funciona, abre `http://localhost:8000/health`; debe responder `{"status": "ok"}`. La documentación interactiva de la API está en `http://localhost:8000/docs`: con el botón **Authorize** se inicia sesión y se pueden probar los endpoints protegidos.

### 3. Base de datos (SQLite)

Con el entorno virtual activo, desde `backend/`:

```bash
python seed.py          # Crea las tablas y carga datos de prueba (borra los datos anteriores)
python verificar_bd.py  # Comprueba relaciones y que se rechacen datos inválidos
```

Se crean el archivo `backend/lf.db` y la carpeta `backend/uploads/` con fotos de prueba; ninguno de los dos se sube al repositorio. El usuario de prueba es `encargado`, con la contraseña definida en `SEED_ENCARGADO_PASSWORD`. El diseño del modelo está en [`docs/modelo-datos.md`](docs/modelo-datos.md).

### 4. Frontend (Astro)

Con el backend encendido (paso 2), en otra terminal y desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

La interfaz queda disponible en `http://localhost:4321`. Ingresa con el usuario `encargado` y la contraseña de `SEED_ENCARGADO_PASSWORD`.

- El frontend lee `PUBLIC_API_URL` del mismo `.env` de la raíz que usa el backend. Solo las variables que empiezan con `PUBLIC_` llegan al navegador.
- Abre la aplicación con `localhost` y no con `127.0.0.1`: el backend solo acepta peticiones del origen configurado en `FRONTEND_ORIGIN` (CORS).
- La sesión dura 8 horas o hasta que el encargado haga clic en **Cerrar sesión**.
- Las fotos se pueden tomar con la **cámara web** o **subir desde un archivo** (JPG, PNG o WEBP, máximo 5 MB). El navegador pide permiso para usar la cámara la primera vez; solo funciona en `localhost` o con HTTPS.

#### Pantallas

| Pantalla | Qué hace | RF | Estado |
|---|---|---|---|
| Inicio de sesión | Usuario y contraseña; error en la misma pantalla | RF01 | Lista |
| Mostrador | Tres opciones según lo que necesita la persona y contadores de lo pendiente | — | Lista |
| Mostrador → Entrega un objeto | Datos del objeto encontrado → foto (opcional) → reportes de pérdida que coinciden, con el contacto de quien lo reportó | RF04, RF20, RF28 | Lista |
| Mostrador → Perdió algo | Persona (y sus reportes abiertos) → datos del reporte → objetos encontrados que coinciden; desde ahí se puede reclamar | RF02, RF03, RF05, RF19, RF26, RF29 | Lista |
| Mostrador → Viene a reclamar | Persona (con su alerta) → objeto (sin ver características) y reporte vinculado → descripción a ciegas → comparar y decidir con motivo (con la entrega previa e incidente si ya se entregó) → entrega con foto obligatoria. Se retoma con `?reclamacion=ID` | RF06–RF16, RF21–RF24, RF26, RF27 | Lista |
| Objetos | Pestañas (disponibles, entregados, reportes abiertos, recuperados y vencidos) y filtros por categoría y texto. Sin características en la lista | RF05, RF21, RF29 | Lista |
| Objetos → Detalle | Todos los datos con quién lo registró y modificó, foto (cámara o archivo), edición mientras esté abierto, coincidencias, entrega y reclamaciones del objeto | RF05, RF17, RF18, RF20, RF25, RF26, RF28 | Lista |
| Personas | Pestañas (todas, estudiantes, docentes), búsqueda, marca de alerta y registro de personas. No se editan ni se borran | RF02, RF19, RF24 | Lista |
| Personas → Detalle | Datos, alerta, reportes de pérdida, reclamaciones con su decisión y objetos que se ha llevado | RF17, RF18, RF24 | Lista |
| Pendientes | Reclamaciones por decidir (la más antigua primero) y aprobadas por entregar, con el botón para retomarlas en el mostrador | RF08, RF15 | Lista |
| Historial | Filtros de reportes (abiertos, recuperados, vencidos), reclamaciones (pendientes, aprobadas, rechazadas), entregas e incidentes. Filtro por persona u objeto. Registrar un incidente en una entrega | RF17, RF18, RF23, RF29 | Lista |
| Alertas | Personas con reclamaciones rechazadas de objetos distintos, con el motivo de cada rechazo | RF24 | Lista |

## API

Todos los endpoints, excepto `/health` y `/auth/login`, requieren el token de sesión en el encabezado `Authorization: Bearer <token>`. La sesión dura 8 horas (`TOKEN_EXPIRE_HOURS`).

| Método | Ruta | Descripción | RF |
|---|---|---|---|
| GET | `/health` | Estado de la API | — |
| POST | `/auth/login` | Inicia sesión y devuelve el token | RF01 |
| GET | `/auth/me` | Datos del encargado con la sesión abierta | RF01 |
| POST | `/personas/estudiantes` | Registra un estudiante | RF02 |
| POST | `/personas/docentes` | Registra un docente | RF19 |
| GET | `/personas` | Lista personas; filtros `tipo` y `buscar` (nombre, código o correo, sin importar tildes ni mayúsculas) | RF02, RF19 |
| GET | `/personas/codigo/{codigo}` | Busca un estudiante por código | RF02 |
| GET | `/personas/{id}` | Datos de una persona | RF02, RF19 |
| POST | `/objetos/perdidos` | Registra un objeto perdido | RF03 |
| POST | `/objetos/encontrados` | Registra un objeto encontrado | RF04 |
| GET | `/objetos` | Consulta objetos; filtros `tipo_registro`, `estado` (`PERDIDO` = reportes abiertos, `RECUPERADO`, `VENCIDO`, `DISPONIBLE`, `ENTREGADO`), `tipo`, `buscar` y `persona_id` (reportes de una persona). Los filtros de texto no distinguen tildes ni mayúsculas (`audifonos` encuentra `Audífonos`). En los reportes incluye quién lo reportó (nombre y código) | RF05, RF27, RF29 |
| GET | `/objetos/{id}` | Detalle de un objeto | RF05 |
| PATCH | `/objetos/{id}` | Corrige datos de un objeto no entregado | RF25 |
| PUT | `/objetos/{id}/foto` | Sube o reemplaza la foto de un objeto (JPG, PNG o WEBP, máx. 5 MB) | RF20 |
| GET | `/objetos/{id}/foto` | Muestra la foto de un objeto | RF20 |
| GET | `/objetos/{id}/coincidencias` | De un reporte de pérdida: objetos encontrados de la misma categoría, con su entrega si ya se entregaron. De un objeto encontrado: reportes de pérdida abiertos de la misma categoría, con la persona que lo reportó | RF05, RF26, RF28 |
| GET | `/personas/alertas` | Personas con 3 o más reclamaciones rechazadas de objetos distintos | RF24 |
| POST | `/reclamaciones` | Registra una reclamación presencial (queda `PENDIENTE`); también de objetos ya entregados, para comparar. `reporte_id` opcional para vincular el reporte de pérdida de la persona | RF06, RF26, RF27 |
| POST | `/reclamaciones/{id}/informacion` | Registra la descripción del reclamante (una sola vez) | RF07 |
| GET | `/reclamaciones` | Lista reclamaciones (por defecto, las pendientes) con su alerta | RF08, RF24 |
| GET | `/reclamaciones/{id}` | Datos de una reclamación | RF08 |
| GET | `/reclamaciones/{id}/comparacion` | Objeto y descripción lado a lado, con foto; solo después de la descripción. Si el objeto ya se entregó, muestra esa entrega | RF09, RF21, RF26 |
| POST | `/reclamaciones/{id}/decision` | Aprueba o rechaza con motivo; encargado y fecha automáticos | RF10–RF14 |
| POST | `/reclamaciones/{id}/entrega` | Entrega con foto obligatoria; el objeto pasa a `ENTREGADO` y el reporte vinculado a `RECUPERADO` | RF15, RF16, RF22, RF27 |
| GET | `/entregas/{id}` | Datos de una entrega | RF18 |
| GET | `/entregas/{id}/foto` | Foto de la persona con el objeto | RF22 |
| POST | `/entregas/{id}/incidente` | Registra que la entrega fue fraudulenta | RF23 |
| GET | `/historial/reclamaciones` | Historial con descripción, decisión y entrega; filtros `estado`, `persona_id`, `objeto_id` | RF17 |
| GET | `/historial/entregas` | Historial de entregas; filtros `persona_id`, `objeto_id` | RF18 |
| GET | `/historial/incidentes` | Incidentes de fraude y medidas propuestas | RF23 |

Las fotos no son públicas: solo se ven con sesión iniciada. La lista de objetos no muestra las características, que solo aparecen en el detalle.

**Orden de uso en el mostrador:** registrar la reclamación → registrar lo que describe la persona sin ver el objeto → ver la comparación (aquí aparecen la foto y las características) → decidir con motivo → si se aprobó, entregar con foto.

**Si alguien reporta una pérdida:** se registra el reporte (`POST /objetos/perdidos`) y se revisan sus coincidencias. Si aparece un objeto encontrado que puede ser suyo, la persona lo reclama vinculando su reporte (`reporte_id`); al entregarlo, el reporte queda `RECUPERADO`. Al registrar un objeto encontrado, sus coincidencias muestran los reportes abiertos que podrían corresponder, con el teléfono de quien lo reportó. Si pasan 15 días sin recuperarlo, el reporte vence.

**Si alguien reclama un objeto que ya se entregó:** se registra la reclamación y su descripción como siempre. La comparación muestra a quién se entregó y qué describió esa persona. Si el encargado concluye que el objeto es de quien reclama ahora, registra un incidente en esa entrega (`POST /entregas/{id}/incidente`) con esta persona como dueño real, y cierra la reclamación como `RECHAZADA` explicando el motivo. Ese rechazo no cuenta para la alerta de la persona.

En `backend/peticiones/` hay peticiones de prueba listas para la extensión REST Client de VS Code.

## Datos de prueba

La base de datos **no es la de la universidad**. Todos los datos que usa el sistema son de prueba, creados por el equipo con `backend/seed.py`. No se almacenan datos reales de personas: los correos usan el dominio reservado `example.com` y las fotos de prueba son imágenes de un solo color.

## Pruebas

- **Pruebas complementarias** ([`fase5-complementarias.yml`](.github/workflows/fase5-complementarias.yml)): en cada cambio que llega a `main` y en cada Pull Request, GitHub Actions instala las dependencias, revisa que el código Python no tenga errores de sintaxis y compila el frontend.
- **Pruebas de integración** ([`fase5-integracion.yml`](.github/workflows/fase5-integracion.yml)): instala el proyecto desde cero, comprueba que se rechaza la clave de ejemplo, crea y verifica la base de datos, prueba el inicio de sesión y los contadores del mostrador, y abre la pantalla de inicio de sesión. Se lanza a mano en **Actions → Fase 5 - Pruebas automaticas → Run workflow**; los registros quedan como artefacto `evidencias-fase5`.
- **Verificación manual:** [`docs/integracion/verificacion-fase5.md`](docs/integracion/verificacion-fase5.md), en el computador de cada integrante.
- **Pruebas del backend con pytest:** pendientes (Fase 6). Cubrirán autenticación y permisos, validación de datos, reclamaciones aprobadas y rechazadas, motivo obligatorio, entregas, cambio de estado del objeto y trazabilidad.

## Hoja de ruta

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Repositorio y entorno de desarrollo | Completada |
| 2 | Diseño de la base de datos | Completada |
| 3 | Backend | Completada |
| 4 | Frontend | Completada |
| 5 | Integración | En curso |
| 6 | Calidad y pruebas | Pendiente |
| 7 | Documentación y entrega | Pendiente |

El detalle de cada fase está en la hoja de ruta dentro de [`docs/`](docs/). El resumen de lo hecho en cada fase está en [`docs/avances/`](docs/avances/).

## Documentación

En [`docs/`](docs/) se encuentran:

- El documento final del Proyecto de Aula en [`docs/Proyecto_de_Aula_LF_Final.docx`](docs/Proyecto_de_Aula_LF_Final.docx): problema, requerimientos RF01–RF29, historias de usuario, arquitectura, modelo de datos, pruebas, resultados y conclusiones.
- La hoja de ruta del proyecto en [`docs/Hoja_de_Ruta_LF_Lost_and_Found.docx`](docs/Hoja_de_Ruta_LF_Lost_and_Found.docx).
- El modelo de datos en [`docs/modelo-datos.md`](docs/modelo-datos.md): diagrama entidad-relación, estados y reglas de integridad.
- Los diagramas UML en [`docs/diagramas/`](docs/diagramas/): casos de uso, clases, secuencia, actividades, componentes y despliegue.
- El diagrama de clases actualizado con el ajuste de alcance RF19–RF29 en [`docs/diagramas/diagrama-clases.md`](docs/diagramas/diagrama-clases.md).
- Los avances de cada fase en [`docs/avances/`](docs/avances/): qué se hizo, decisiones tomadas, trazabilidad de requerimientos y verificación ([Fase 3](docs/avances/fase3.md), [Fase 4](docs/avances/fase4.md)).
- La lista de verificación de la integración (Fase 5) en [`docs/integracion/verificacion-fase5.md`](docs/integracion/verificacion-fase5.md), para hacerla en el computador de cada integrante.

## Equipo

**Sebastián Caicedo** · **Javier Carta**

Ingeniería de Software, séptimo semestre. Docente: Aisner José Marrugo Juliao.
