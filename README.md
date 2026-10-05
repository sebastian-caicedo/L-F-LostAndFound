# L&F — Lost And Found

Sistema web para la **gestión de objetos perdidos y encontrados en una institución universitaria**. El encargado registra objetos y estudiantes, gestiona reclamaciones, compara la información del reclamante con las características del objeto y decide si aprueba o rechaza, con trazabilidad completa de decisiones y entregas.

**Estado:** MVP en desarrollo · **Inicio:** 24/08/2026 · **Metodología:** Scrum con tablero Kanban

## Problema que resuelve

Sin un mecanismo centralizado, nadie sabe con certeza qué objetos fueron encontrados, dónde están ni cómo comprobar que quien los reclama es el dueño. L&F centraliza el registro y deja evidencia de cada decisión: quién la tomó, cuándo y por qué.

## Usuario

El **encargado de objetos perdidos** es el único usuario de la aplicación. El estudiante no la usa directamente: el encargado registra sus datos cuando reporta una pérdida o reclama un objeto. La decisión sobre cada reclamación es siempre manual; el sistema solo facilita la comparación.

## Flujo principal (MVP)

```text
Iniciar sesión → Registrar estudiante → Registrar objeto (perdido / encontrado)
→ Registrar reclamación y características del reclamante → Revisar y comparar
→ Aprobar o rechazar (motivo obligatorio) → Registrar entrega → Historial
```

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
| Gestión del proyecto | Jira / Trello (tablero Kanban) |

```text
Encargado → Frontend (Astro) → API HTTP → Backend (FastAPI) → SQLite
```

## Instalación y ejecución

**Requisitos:** Git, Python [VERIFICAR versión], Node.js y npm.

```bash
git clone https://github.com/sebastian-caicedo/L-F-LostAndFound.git
cd L-F-LostAndFound

cp .env.example .env        # completar valores; no subir credenciales reales

# Backend (FastAPI)  [VERIFICAR carpeta y comandos]
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (Astro)   [VERIFICAR carpeta]
cd frontend
npm install
npm run dev
```

## Pruebas

```bash
[VERIFICAR comando, ej: pytest]
```

Cubren: autenticación y permisos, validación de datos, reclamaciones aprobadas y rechazadas, motivo obligatorio, entregas, cambio de estado del objeto y trazabilidad.

## Documentación

En [`docs/`](docs/): documento del Proyecto de Aula (historias de usuario, elicitación y decisiones de alcance), hoja de ruta y diagramas UML (casos de uso, clases, secuencia, actividades, componentes y despliegue).

## Equipo

**Sebastián Caicedo** · **Javier Carta**

Ingeniería de Software, séptimo semestre. Docente: Aisner José Marrugo Juliao.
