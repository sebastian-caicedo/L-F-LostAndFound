# Fase 4 — Construcción del frontend

**Proyecto:** L&F — Lost And Found
**Fecha de cierre:** 23/10/2026
**Estado:** Completada

## Objetivo

Construir la interfaz web que usa el encargado de objetos perdidos para atender el flujo completo del MVP desde el mostrador: inicio de sesión → registro de personas y objetos → reclamación → descripción a ciegas → comparación → decisión → entrega → historial y trazabilidad.

## Tareas de la hoja de ruta

- [x] Crear la estructura visual de Astro: layout, menú, navegación y página inicial.
- [x] Crear la pantalla de inicio de sesión.
- [x] Crear el módulo de estudiantes (pantalla **Personas**, que incluye a los docentes por RF19).
- [x] Crear el módulo de objetos: registrar perdido, registrar encontrado, consultar y ver detalle.
- [x] Crear el módulo de reclamaciones.
- [x] Crear la pantalla de revisión y comparación entre objeto y reclamante.
- [x] Crear la pantalla de decisión con aprobación/rechazo y motivo.
- [x] Crear el módulo de entregas.
- [x] Crear el módulo de historial.

## Decisiones de diseño

Se definieron con el equipo antes de construir las pantallas:

| Decisión | Motivo |
|---|---|
| Astro con páginas `.astro`, JavaScript sin frameworks y CSS con variables | Es lo más sencillo de entender y explicar; el equipo no había trabajado con frameworks de frontend |
| Colores azul y blanco, sin modo oscuro ni logo de la universidad | El sistema no está vinculado oficialmente a la universidad. Marca de texto: "L&F – Objetos perdidos y encontrados" |
| Pantalla para computador de escritorio | El sistema se usa en el mostrador de objetos perdidos |
| Sin pantalla de inicio: después de iniciar sesión se va directo al **Mostrador** | Lo primero que hace el encargado es atender a la persona que llega |
| El estudiante nunca ve la pantalla, por eso no hay botón "mostrar" | Solo el encargado usa la aplicación. La regla de verificación a ciegas (RF21) la aplica el backend |
| Errores en rojo en la misma pantalla, sin ventanas emergentes | Las ventanas emergentes interrumpen y se cierran sin leerlas |
| Fotos con la cámara web **o** subiendo un archivo | El mostrador puede tener o no cámara; un archivo permite usar una foto tomada con el celular |
| Al terminar un flujo: confirmación y botón **Atender a otra persona** | El encargado decide cuándo volver al mostrador |
| La alerta de intentos fallidos se muestra al elegir a la persona y otra vez al comparar | Es justo cuando el encargado debe verificar con más cuidado (RF24) |
| Historial con botones de filtro: reportes, reclamaciones, entregas e incidentes | Permite llegar en un clic a cada parte de la trazabilidad |
| Detalles con `?id=N` (por ejemplo `/objetos/detalle?id=5`) | Astro genera páginas estáticas: una sola página sirve para todos los objetos |

## Pantallas

| Pantalla | Qué hace | RF |
|---|---|---|
| Inicio de sesión | Usuario y contraseña, botón para ver la contraseña, error en la misma pantalla. Sesión de 8 horas | RF01 |
| Mostrador | Tres opciones según lo que necesita la persona y contadores de lo pendiente | — |
| Mostrador → Entrega un objeto | Datos → foto opcional → reportes de pérdida que coinciden, con el contacto de quien lo reportó | RF04, RF20, RF28 |
| Mostrador → Perdió algo | Persona → datos del reporte → objetos encontrados que coinciden; desde ahí se puede reclamar | RF02, RF03, RF05, RF19, RF26, RF29 |
| Mostrador → Viene a reclamar | Persona → objeto → descripción a ciegas → comparar y decidir con motivo → entrega con foto | RF06–RF16, RF21–RF24, RF26, RF27 |
| Objetos y su detalle | Pestañas por estado, filtros, edición mientras el registro esté abierto, foto, coincidencias, entrega y reclamaciones del objeto | RF05, RF17, RF18, RF20, RF25, RF26, RF28 |
| Personas y su detalle | Búsqueda, registro, alerta, reportes, reclamaciones y objetos que se ha llevado | RF02, RF17, RF18, RF19, RF24 |
| Pendientes | Reclamaciones por decidir y aprobadas por entregar, con el botón para retomarlas | RF08, RF15 |
| Historial | Reportes, reclamaciones, entregas e incidentes; registrar un incidente en una entrega | RF17, RF18, RF23, RF29 |
| Alertas | Personas con reclamaciones rechazadas de objetos distintos y el motivo de cada rechazo | RF24 |

## Estructura del frontend

```text
frontend/src/
├── layouts/      Base.astro (HTML) y App.astro (encabezado, menú y protección de sesión)
├── pages/        Una página por pantalla
├── components/   Pasos, BuscarPersona, FormPersona y SelectorFoto
├── lib/          api.js (token y errores), ui.js, pasos.js, persona.js, foto.js y objetos.js
└── styles/       global.css (colores y estilos comunes)
```

Todas las pantallas hablan con el backend por medio de `lib/api.js`: ahí están el token de sesión, los mensajes de error en español y el cierre de sesión cuando el token vence. Las fotos son protegidas, así que se descargan con el token (`apiImagen`) en vez de ponerse directo en un `<img>`.

## Cambios al backend durante la fase

| Cambio | Motivo |
|---|---|
| `GET /objetos` acepta `persona_id` | Mostrar los reportes abiertos de la persona y vincularlos a su reclamación (RF27) |
| En los reportes de pérdida, `GET /objetos` incluye quién lo reportó (nombre y código) | Mostrarlo en la lista sin pedir el detalle de cada objeto. No expone las características (RF21) |

## Qué se hizo, entrega por entrega

| Entrega | Contenido | Commit |
|---|---|---|
| 1 | Estructura, estilos, inicio de sesión, encabezado con menú y mostrador con contadores | `58b205e` |
| 2 | Los tres flujos del mostrador con cámara web o archivo | `be8e44a` |
| 3 | Objetos, Personas y Pendientes, con su detalle y trazabilidad | `6ab46d5` |
| 4 | Historial con filtros, registro de incidentes en entregas y Alertas | Este cierre |

## Cómo se verificó

Cada entrega se probó en un navegador automatizado (Playwright con Chromium y una cámara simulada) contra el backend real con los datos de prueba de `seed.py`:

| Prueba | Comprobaciones |
|---|---|
| Entrega 1: inicio de sesión y mostrador | 27 |
| Entrega 2: flujos del mostrador | 62 |
| Entrega 3: Objetos, Personas y Pendientes | 43 |
| Entrega 4: Historial y Alertas | 34 |

Las pruebas revisan el flujo completo y también las reglas: que la lista y el paso de descripción no muestren características ni fotos (RF21), que el motivo sea obligatorio (RF12), que la foto de entrega sea obligatoria (RF22), que no se pueda aprobar un objeto ya entregado (RF26), que los registros cerrados no se editen (RF25), que no aparezcan ventanas emergentes ni errores de JavaScript y que lo que muestra cada pantalla coincida con lo guardado en la base. Las 178 pruebas del backend de la Fase 3 se repitieron tras cada cambio al backend.

Las pruebas automáticas se incorporan al repositorio en la Fase 6.

## Pendiente para las siguientes fases

- **Fase 5:** probar el flujo completo en los computadores del equipo y corregir errores de integración.
- **Fase 6:** pasar las pruebas del backend a `backend/tests/` con pytest.
- **Fase 7:** actualizar el documento del Proyecto de Aula (RF19–RF29 y capturas de las pantallas) y los diagramas UML.
