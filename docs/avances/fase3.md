# Fase 3 — Construcción del backend

**Proyecto:** L&F — Lost And Found
**Fecha de cierre:** 22/10/2026
**Estado:** Completada

## Objetivo

Construir la API en FastAPI que implementa todo el flujo del MVP sobre la base de datos de la Fase 2: inicio de sesión del encargado → registro de personas y objetos → reclamación → verificación → decisión → entrega → historial y trazabilidad.

## Tareas de la hoja de ruta

- [x] Organizar la arquitectura del backend: modelos, esquemas, servicios, rutas y configuración de base de datos.
- [x] Implementar la autenticación del encargado.
- [x] Implementar el registro y consulta de estudiantes (y docentes).
- [x] Implementar el registro, consulta y actualización de objetos perdidos y encontrados.
- [x] Implementar el registro y consulta de reclamaciones y la información del reclamante.
- [x] Implementar la revisión y decisión de reclamaciones: aprobar o rechazar, motivo obligatorio, encargado y fecha/hora.
- [x] Implementar el registro de entregas y la actualización del estado del objeto.
- [x] Implementar el historial de reclamaciones, decisiones y entregas.

## Arquitectura

El backend se organiza en capas. Cada una tiene una sola responsabilidad (RNF-07):

```text
Petición HTTP → routers/ → services/ → models.py → SQLite
                   │           │
               schemas/     errores.py
```

| Capa | Carpeta / archivo | Responsabilidad |
|---|---|---|
| Endpoints | `app/routers/` | Reciben la petición, piden la sesión y llaman al servicio. No tienen reglas de negocio |
| Esquemas | `app/schemas/` | Definen y validan los datos que entran y salen (Pydantic). Rechazan campos que no se permiten, como el estado o el encargado |
| Servicios | `app/services/` | Reglas de negocio del flujo. No saben nada de HTTP |
| Modelos | `app/models.py` | Tablas y restricciones de integridad |
| Errores | `app/errores.py` | Errores de negocio con mensajes en español; `main.py` los convierte en 404, 409 o 422 |
| Apoyo | `config.py`, `security.py`, `deps.py`, `validaciones.py`, `fotos.py` | Configuración del `.env`, contraseñas y tokens, sesión y encargado autenticado, normalización de datos, manejo de fotos |

## Qué se hizo, paso a paso

| Paso | Contenido | Commit |
|---|---|---|
| 1 y 2 | Arquitectura por capas, configuración desde `.env`, CORS configurable e inicio de sesión con token de 8 horas | `fb7d945` |
| 3 y 4 | Módulo de personas (estudiantes y docentes) y de objetos (registro, consulta con filtros, edición y fotos). Ajuste del modelo de datos y diagrama de clases actualizado | `1525464` |
| 5 a 8 | Reclamaciones, descripción del reclamante, comparación, decisión, entrega con foto, historial, incidentes y alerta de intentos fallidos | `772fedc` |
| RF26 | Detección de posibles fraudes: entrega previa en la comparación, coincidencias de reportes de pérdida y ajuste de la alerta | `65aa868`, `58ffb17` |

## Ajuste de alcance

Durante la fase, el equipo amplió el alcance con estos requerimientos. Están documentados en el README y en [`modelo-datos.md`](../modelo-datos.md). Falta incorporarlos al documento del Proyecto de Aula (Fase 7).

| ID | Requerimiento | Motivo |
|---|---|---|
| RF19 | Registrar docentes como personas que reportan o reclaman objetos | Los docentes también pierden y reclaman objetos |
| RF20 | Registrar y consultar la foto de un objeto | El encargado puede ver el objeto sin ir a buscarlo |
| RF21 | Ocultar la foto en la reclamación hasta registrar la descripción del reclamante | Evitar que el reclamante copie lo que ve en pantalla |
| RF22 | Foto de la persona junto al objeto al entregarlo | Evidencia de quién se llevó qué |
| RF23 | Registrar incidentes de entregas fraudulentas | Saber cómo ocurrió y qué mejorar en el proceso |
| RF24 | Alertar sobre personas con 3 o más reclamaciones rechazadas de objetos distintos | Tener más cuidado con quien intenta reclamar objetos ajenos |
| RF25 | Editar los datos de un objeto no entregado, con trazabilidad | Corregir datos que no se tuvieron en cuenta al registrarlo |
| RF26 | Mostrar si un objeto ya se entregó, a quién y con qué descripción, al comparar o buscar coincidencias | Evaluar si quien se llevó un objeto lo robó cuando aparece otra persona que lo describe |
| RF27 | Vincular la reclamación con el reporte de pérdida de la persona y cerrarlo como recuperado al entregar | Que los reportes no queden abiertos para siempre y saber qué reclamación resolvió cada reporte |
| RF28 | Coincidencias en las dos direcciones: para un objeto encontrado, los reportes de pérdida abiertos | Al registrar un objeto encontrado, saber a quién podría pertenecer sin tener que buscarlo |
| RF29 | Vencer a los 15 días los reportes de pérdida no resueltos, sin borrarlos | Sacar de la lista los reportes que nadie cierra, sin perder la evidencia |

## Decisiones de diseño

1. **Sesión con token JWT de 8 horas.** Es lo estándar en FastAPI y dura una jornada de trabajo del encargado. El token lleva el id del encargado, y por eso el responsable de cada decisión y entrega se registra solo (RF13). Si el encargado se desactiva, su token deja de servir de inmediato.
2. **El responsable y la fecha nunca vienen del formulario.** Los esquemas rechazan `encargado_id`, `estado` y fechas automáticas: salen del token y del servidor.
3. **Verificación a ciegas (RF21).** La lista de objetos no muestra las características. La descripción del reclamante se registra una sola vez y no se puede editar. La comparación, con la foto y las características, solo aparece después de esa descripción.
4. **La decisión siempre es del encargado.** El sistema no aprueba ni rechaza nada por su cuenta: impide aprobar dos reclamaciones del mismo objeto, pero cada reclamación necesita su propia decisión con motivo. La alerta del RF24 solo informa.
5. **Entrega en una transacción.** La entrega y el cambio del objeto a `ENTREGADO` se guardan juntos. Si algo falla, no se guarda nada y se borra la foto.
6. **Posibles fraudes (RF26).** Se puede reclamar un objeto ya entregado para comparar con quien se lo llevó, pero no se puede aprobar. Si se comprueba que el objeto era de quien reclama ahora, se registra un incidente con esa persona como dueña real, y ese rechazo no cuenta en su alerta.
7. **Fotos protegidas.** Se guardan como archivos con nombre aleatorio. Se revisa su formato real (JPG, PNG o WEBP) y su tamaño (máximo 5 MB). Solo se ven con sesión iniciada.
8. **Código estudiantil normalizado.** `t70496` se guarda como `T00070496`. La base rechaza cualquier código que no tenga el formato `T` + 8 dígitos.
9. **Sin eliminar registros.** No hay endpoints para borrar personas, objetos ni reclamaciones, para no romper la trazabilidad.

## Trazabilidad de requerimientos

| RF | Requerimiento | Implementación |
|---|---|---|
| RF01 | Autenticar al encargado | `POST /auth/login`, `GET /auth/me` |
| RF02 | Registrar estudiantes | `POST /personas/estudiantes`, `GET /personas`, `GET /personas/codigo/{codigo}` |
| RF03 | Registrar objetos perdidos | `POST /objetos/perdidos` |
| RF04 | Registrar objetos encontrados | `POST /objetos/encontrados` |
| RF05 | Consultar objetos | `GET /objetos` (filtros), `GET /objetos/{id}`, `GET /objetos/{id}/coincidencias` |
| RF06 | Registrar reclamaciones | `POST /reclamaciones` |
| RF07 | Información del reclamante | `POST /reclamaciones/{id}/informacion` |
| RF08 | Consultar pendientes | `GET /reclamaciones` |
| RF09 | Comparar objeto y reclamante | `GET /reclamaciones/{id}/comparacion` |
| RF10, RF11 | Aprobar o rechazar | `POST /reclamaciones/{id}/decision` |
| RF12 | Motivo obligatorio | Esquema `DecisionCrear` y `CHECK` en la tabla `decision` |
| RF13, RF14 | Encargado y fecha/hora automáticos | Dependencia `get_encargado_actual` y valor por defecto `ahora()` |
| RF15 | Registrar entrega | `POST /reclamaciones/{id}/entrega` |
| RF16 | Actualizar estado del objeto | La misma transacción de la entrega |
| RF17 | Historial de reclamaciones y decisiones | `GET /historial/reclamaciones` |
| RF18 | Historial de entregas | `GET /historial/entregas`, `GET /entregas/{id}` |
| RF19 | Docentes | `POST /personas/docentes` |
| RF20 | Foto del objeto | `PUT /objetos/{id}/foto`, `GET /objetos/{id}/foto` |
| RF21 | Foto oculta hasta la descripción | Regla en `comparacion()`; la descripción no se puede editar |
| RF22 | Foto al entregar | Campo obligatorio en la entrega; `GET /entregas/{id}/foto` |
| RF23 | Incidentes de fraude | `POST /entregas/{id}/incidente`, `GET /historial/incidentes` |
| RF24 | Alerta de intentos fallidos | Campo `alerta` en cada reclamación; `GET /personas/alertas` |
| RF25 | Editar objetos | `PATCH /objetos/{id}` |
| RF26 | Entrega previa y coincidencias | Campo `entrega_previa` en la comparación; `GET /objetos/{id}/coincidencias` |
| RF27 | Reporte vinculado y recuperado | `reporte_id` en `POST /reclamaciones`; la entrega cierra el reporte como `RECUPERADO` |
| RF28 | Coincidencias inversas | `GET /objetos/{id}/coincidencias` desde un objeto encontrado, con `reportado_por` |
| RF29 | Vencimiento de reportes | `vencer_reportes()` antes de consultar objetos; campo `vence_el`; estado `VENCIDO` |

| RNF | Cómo se cumple |
|---|---|
| RNF-01 Seguridad | Todos los endpoints, excepto `/health` y `/auth/login`, exigen el token; sin él responden 401 |
| RNF-02 Autorización | Solo los encargados activos obtienen y usan un token válido |
| RNF-03 Integridad | Llaves foráneas activas en SQLite y validación en los servicios |
| RNF-04 Validación | Esquemas Pydantic y restricciones de la base; mensajes en español |
| RNF-05 Trazabilidad | Cada decisión, entrega, edición e incidente guarda encargado y fecha; los reportes de pérdida vencen sin borrarse |
| RNF-07 Mantenibilidad | Arquitectura por capas; las pruebas automatizadas se agregan en la Fase 6 |

## Verificación

Se probó todo desde un clon limpio del repositorio:

- `python verificar_bd.py`: **33 verificaciones** de datos, relaciones y restricciones, todas correctas.
- Pruebas de la API: **178 casos**, sin fallas. Cubren:
  - inicio de sesión: token válido, contraseña incorrecta, token alterado, vencido o firmado con otra clave, y encargado desactivado (16 casos);
  - personas y objetos: normalización y validación de datos, duplicados, filtros, edición y fotos (55 casos);
  - flujo de reclamación a historial: cada regla del flujo y cada caso que debe fallar (59 casos);
  - posibles fraudes: escenario de la calculadora entregada y reclamada después, y coincidencias (21 casos);
  - reportes de pérdida: vínculo con la reclamación, cierre como recuperado, coincidencias inversas y vencimiento (27 casos).
- Los 30 endpoints de la API coinciden con la tabla del README.
- Ningún archivo privado (`.env`, base de datos, fotos) está en el repositorio ni en su historial.

## Datos de prueba

`python seed.py` crea 1 encargado, 4 estudiantes, 1 docente, 10 objetos (5 encontrados y 5 reportes de pérdida) y 7 reclamaciones. Incluye un caso pendiente, entregas, rechazos, una persona con alerta, un fraude con incidente, un reporte recuperado y uno que vence. Todos los datos son inventados, y las fotos son imágenes de un solo color.

## Ajuste posterior al cierre (23/10/2026)

Al revisar qué pasa cuando un estudiante reporta una pérdida, se encontraron tres huecos: el reporte nunca se cerraba, no se relacionaba con la reclamación que lo resolvía, y las coincidencias solo se buscaban desde el reporte. Se agregaron los RF27, RF28 y RF29:

- **RF27:** la reclamación puede llevar `reporte_id`, que debe ser un reporte abierto de la misma persona. Al entregar, el reporte pasa a `RECUPERADO` en la misma transacción. La comparación muestra también lo que la persona dijo en su reporte.
- **RF28:** desde un objeto encontrado, las coincidencias muestran los reportes de pérdida abiertos de la misma categoría, con el teléfono de quien lo reportó.
- **RF29:** un reporte que no se resuelve en 15 días (`DIAS_VIGENCIA_REPORTE`) pasa a `VENCIDO`. El equipo propuso borrarlo, pero se decidió **vencerlo sin borrarlo**: su descripción es evidencia en un posible fraude y borrar contradice la trazabilidad (RNF-05). El vencimiento se aplica justo antes de consultar objetos, sin un proceso programado.

No se agregaron endpoints: siguen siendo 30.

## Hallazgos

- **Clave secreta en el historial.** El 05/10/2026 se subió por error una `SECRET_KEY` real en `.env.example` (commit `d333528`), y se corrigió en el commit siguiente. Como el historial es público, esa clave no debe usarse en ningún `.env`. Se decidió no reescribir el historial, porque la clave solo se usaba en desarrollo local con datos de prueba.
- **Ramas en desuso.** El equipo pasó a trabajar directamente en `main`; las ramas `develop` y `feature/modelo-bd` se eliminan.

## Pendiente para las siguientes fases

- **Fase 4 (frontend):** construir las pantallas en Astro. La foto del objeto se muestra detrás de un botón, no de inmediato. El frontend guarda el token y lo borra al cerrar sesión.
- **Fase 6 (pruebas):** convertir los 151 casos en pruebas de `pytest` dentro de `backend/tests/`.
- **Fase 7 (documentación):** agregar RF19–RF29 al documento del Proyecto de Aula, reemplazar la Figura 2 por el diagrama de clases actualizado y alinear los diagramas de secuencia, componentes y despliegue con el stack y los endpoints.
