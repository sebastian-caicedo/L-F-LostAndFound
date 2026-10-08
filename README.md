# L&F — Lost And Found

Sistema web para la **gestión de objetos perdidos y encontrados en una institución universitaria**. El encargado registra estudiantes y objetos, gestiona reclamaciones, compara la información del reclamante con las características del objeto y decide si aprueba o rechaza. Cada decisión y cada entrega quedan registradas con trazabilidad completa.

**Estado:** MVP en desarrollo (Fase 1 — base del proyecto) · **Inicio:** 24/08/2026 · **Metodología:** Scrum con tablero Kanban

## Problema que resuelve

Sin un mecanismo centralizado, nadie sabe con certeza qué objetos fueron encontrados, dónde están ni cómo comprobar que quien los reclama es el dueño. L&F centraliza el registro y deja evidencia de cada decisión: quién la tomó, cuándo y por qué.

## Usuario

El **encargado de objetos perdidos** es el único usuario de la aplicación. El estudiante no la usa directamente: el encargado registra sus datos cuando reporta una pérdida o reclama un objeto.

La decisión sobre cada reclamación es siempre del encargado. El sistema solo facilita la comparación entre el objeto y la información del reclamante.

## Flujo principal (MVP)

```text
Iniciar sesión → Registrar estudiante → Registrar objeto (perdido / encontrado)
→ Registrar reclamación y características del reclamante → Revisar y comparar
→ Aprobar o rechazar (motivo obligatorio) → Registrar entrega → Historial
```

### Reglas de negocio

- Aprobar o rechazar una reclamación exige un **motivo obligatorio**. El sistema registra automáticamente el **encargado responsable** y la **fecha y hora** de la decisión.
- La **entrega** solo se registra para reclamaciones **aprobadas** y actualiza el estado del objeto.
- Toda reclamación se asocia a un estudiante y a un objeto existentes.

## Requerimientos funcionales

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF01 | Autenticar al encargado con sus credenciales | Alta |
| RF02 | Registrar los datos del estudiante relacionado con un proceso | Alta |
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

## Requerimientos no funcionales

| ID | Atributo | Criterio |
|---|---|---|
| RNF-01 | Seguridad | Toda funcionalidad protegida rechaza a usuarios no autenticados |
| RNF-02 | Autorización | Las funciones del encargado rechazan a cualquier otro rol |
| RNF-03 | Integridad | Toda reclamación se asocia a un estudiante y a un objeto existentes |
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
│   │   └── main.py          # Punto de entrada de la API (endpoint /health y CORS)
│   └── requirements.txt     # Dependencias de Python
├── frontend/                # Interfaz web en Astro
│   ├── public/              # Archivos estáticos (favicon)
│   ├── src/pages/           # Páginas de la aplicación
│   ├── astro.config.mjs
│   └── package.json
├── docs/                    # Documentación del proyecto
│   ├── diagramas/           # Diagramas UML
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

Completa los valores del archivo `.env`. Ese archivo **no se sube al repositorio**: el repositorio solo contiene `.env.example`, sin credenciales reales.

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

La API queda disponible en `http://localhost:8000`. Para verificar que funciona, abre `http://localhost:8000/health`; debe responder `{"status": "ok"}`. La documentación interactiva de la API está en `http://localhost:8000/docs`.

### 3. Frontend (Astro)

En otra terminal, desde la raíz del proyecto:

```bash
cd frontend
npm install
npm run dev
```

La interfaz queda disponible en `http://localhost:4321`.

## Datos de prueba

La base de datos **no es la de la universidad**. Todos los datos que usa el sistema son de prueba, creados por el equipo. No se almacenan datos reales de personas.

## Pruebas

Pendiente (Fase 6 de la hoja de ruta). Las pruebas cubrirán autenticación y permisos, validación de datos, reclamaciones aprobadas y rechazadas, motivo obligatorio, entregas, cambio de estado del objeto y trazabilidad.

## Hoja de ruta

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Repositorio y entorno de desarrollo | En curso |
| 2 | Diseño de la base de datos | Pendiente |
| 3 | Backend | Pendiente |
| 4 | Frontend | Pendiente |
| 5 | Integración | Pendiente |
| 6 | Calidad y pruebas | Pendiente |
| 7 | Documentación y entrega | Pendiente |

El detalle de cada fase está en la hoja de ruta dentro de [`docs/`](docs/).

## Documentación

En [`docs/`](docs/) se encuentran:

- El documento del Proyecto de Aula: historias de usuario, elicitación y decisiones de alcance.
- La hoja de ruta del proyecto.
- Los diagramas UML en [`docs/diagramas/`](docs/diagramas/): casos de uso, clases, secuencia, actividades, componentes y despliegue.

## Equipo

**Sebastián Caicedo** · **Javier Carta**

Ingeniería de Software, séptimo semestre. Docente: Aisner José Marrugo Juliao.
