# Fase 5 — Lista de verificación de integración

**Proyecto:** L&F — Lost And Found
**Responsables:** Sebastián Caicedo y Javier Carta
**Objetivo:** comprobar, en el computador de cada integrante, que el sistema completo funciona de punta a punta: Astro ↔ FastAPI ↔ SQLite, desde clonar el repositorio hasta entregar un objeto y consultarlo en el historial.

## Cómo usar esta lista

1. Cada integrante hace la lista **completa en su propio computador**. Así se detectan problemas de instalación que no aparecen en el otro equipo.
2. Sigue las secciones **en orden**: cada una usa lo que dejó la anterior.
3. Marca cada casilla al comprobarla: cambia `[ ]` por `[x]`. Se puede editar este archivo en VS Code o directamente en GitHub.
4. Si algo **no** da el resultado esperado, no lo arregles sobre la marcha: anótalo en la tabla [Registro de fallas](#registro-de-fallas) con los pasos para repetirlo y sigue con lo demás.
5. Todos los datos que se escriben son **de prueba**. No uses nombres, códigos ni fotos de personas reales; para las fotos usa objetos (un llavero, un cuaderno) o imágenes genéricas.

> Para cada falla guarda tres cosas: una **captura** de la pantalla, lo que dice la **consola del navegador** (tecla F12 → pestaña *Console*) y lo último que muestra la **terminal del backend**. Con eso se puede encontrar el error.

## 0. Datos de la prueba

| Dato | Sebastián | Javier |
|---|---|---|
| Fecha | | |
| Sistema operativo | | |
| Versión de Python (`python --version`) | | |
| Versión de Node (`node --version`) | | |
| Navegador y versión | | |
| ¿Tiene cámara web? | | |
| Commit probado (`git log --oneline -1`) | | |

---

## A. Instalación desde cero

Se hace en una **carpeta nueva**, como lo haría alguien que recibe el proyecto por primera vez. Comprueba que el README basta para ponerlo en marcha.

- [ ] **A1.** Clonar en una carpeta nueva: `git clone https://github.com/sebastian-caicedo/L-F-LostAndFound.git L-F-prueba` y entrar con `cd L-F-prueba`.
- [ ] **A2.** Crear el `.env` desde la plantilla: `copy .env.example .env` (cmd) o `cp .env.example .env`.
- [ ] **A3.** Arrancar el backend **sin** cambiar `SECRET_KEY` (pasos A5 a A7). Resultado esperado: el backend **no arranca** y dice *"Falta configurar SECRET_KEY en el archivo .env"*. Esto confirma que no se puede trabajar con la clave de ejemplo.
- [ ] **A4.** Generar una clave con `python -c "import secrets; print(secrets.token_hex(32))"`, pegarla en `SECRET_KEY` y escribir una contraseña de prueba en `SEED_ENCARGADO_PASSWORD`.
- [ ] **A5.** Crear y activar el entorno virtual: `cd backend`, `python -m venv venv`, `venv\Scripts\activate`. Resultado esperado: la terminal empieza con `(venv)`.
- [ ] **A6.** Instalar dependencias: `pip install -r requirements.txt`. Resultado esperado: termina sin errores en rojo.
- [ ] **A7.** Cargar los datos de prueba: `python seed.py`. Resultado esperado: un resumen con 1 encargado, 4 estudiantes, 1 docente, 10 objetos y 7 reclamaciones.
- [ ] **A8.** Verificar la base de datos: `python verificar_bd.py`. Resultado esperado: todas las comprobaciones en OK.
- [ ] **A9.** Encender la API: `uvicorn app.main:app --reload`. Abrir `http://localhost:8000/health`. Resultado esperado: `{"status": "ok"}`.
- [ ] **A10.** En **otra terminal**, desde la raíz: `cd frontend`, `npm install`. Resultado esperado: termina sin errores; si dice *vulnerabilities*, anótalo, pero **no** uses `npm audit fix --force`.
- [ ] **A11.** `npm run dev` y abrir `http://localhost:4321`. Resultado esperado: aparece la pantalla de **inicio de sesión**.

## B. Conexión entre las partes

Comprueba que Astro habla con FastAPI y que FastAPI guarda y lee de SQLite.

- [ ] **B1.** Iniciar sesión con usuario `mal` y cualquier contraseña. Resultado esperado: en rojo y en la misma pantalla, *"Usuario o contraseña incorrecta, intente nuevamente."*, sin ventanas emergentes.
- [ ] **B2.** Iniciar sesión con `encargado` y la contraseña de `SEED_ENCARGADO_PASSWORD`. Resultado esperado: entra directo al **Mostrador**, con el nombre del encargado arriba a la derecha.
- [ ] **B3.** Contadores del Mostrador con los datos de prueba: **1** reclamación pendiente, **3** reportes abiertos, **3** objetos disponibles y **1** persona con alerta.
- [ ] **B4.** Apagar el backend (Ctrl+C en su terminal) y recargar el Mostrador. Resultado esperado: el mensaje *"No se pudo conectar con el servidor. Verifica que el backend esté encendido."* Volver a encender el backend.
- [ ] **B5.** Abrir `http://127.0.0.1:4321` en vez de `localhost`. Resultado esperado: la página no abre o, si abre, no conecta con el backend (*"No se pudo conectar…"*), porque el backend solo acepta el origen `http://localhost:4321` (CORS). Volver a usar `localhost`.
- [ ] **B6.** Sesión vencida: en F12 → *Application* → *Local Storage* → `http://localhost:4321`, cambiar el valor de `lf_token` por cualquier texto y recargar. Resultado esperado: vuelve al inicio de sesión con *"Tu sesión venció. Inicia sesión de nuevo."*
- [ ] **B7.** Clic en **Cerrar sesión**. Resultado esperado: vuelve al inicio de sesión; si se escribe `http://localhost:4321/objetos` en la barra, redirige al inicio de sesión.

## C. Flujo completo del MVP (escenario guiado)

Una estudiante pierde unas llaves, alguien las encuentra y ella las reclama. Usa exactamente estos datos de prueba:

| Dato | Valor |
|---|---|
| Estudiante | Nombre `Estudiante Verificación Uno` · Código `t12345` · Carrera `Ingeniería de Sistemas` · Correo `verificacion.uno@example.edu.co` · Teléfono `300 000 1234` |
| Su reporte | Tipo `Llaves` · Descripción `Llavero con tres llaves` · Características `Llavero de un balón de fútbol, una de las llaves está pintada de rojo` |
| Objeto encontrado | Tipo `Llaves` · Descripción `Llavero con llaves` · Características `Llavero de balón de fútbol con tres llaves, una roja` · Lugar `Biblioteca, primer piso` |

**C.1 Perdió algo** (RF02, RF03, RF29)
- [ ] **C1.** Mostrador → **Perdió algo**. Buscar `t12345`. Resultado esperado: *"No se encontró a nadie…"*.
- [ ] **C2.** **+ Registrar persona nueva**: el código ya viene escrito. Completar los datos de la tabla y registrar. Resultado esperado: la tarjeta muestra el código completo **T00012345** y el teléfono sin espacios.
- [ ] **C3.** **Continuar**, llenar el reporte y **Registrar reporte**. Resultado esperado: *"Reporte registrado"* con la fecha de vencimiento (15 días después) y *"Por ahora no hay objetos encontrados de esta categoría"*. Clic en **Atender a otra persona**.

**C.2 Entrega un objeto** (RF04, RF20, RF28)
- [ ] **C4.** Mostrador → **Entrega un objeto**. Llenar los datos del objeto encontrado y **Registrar objeto**.
- [ ] **C5.** **Tomar foto** con la cámara (aceptar el permiso del navegador) o **Subir archivo**. Resultado esperado: se ve la vista previa. **Guardar foto**.
- [ ] **C6.** Resultado esperado en el paso 3: *"Objeto registrado"* con foto y, en coincidencias, el reporte de **Estudiante Verificación Uno** con su teléfono y correo para avisarle.

**C.3 Viene a reclamar** (RF06–RF16, RF21, RF22, RF27)
- [ ] **C7.** Mostrador → **Viene a reclamar**. Buscar `12345` (sin la T). Resultado esperado: aparece la estudiante y **no** tiene alerta. **Continuar**.
- [ ] **C8.** Lista de objetos: el llavero aparece **sin** sus características ni foto. Elegirlo. Resultado esperado: debajo aparece su reporte de pérdida **ya marcado**. **Registrar reclamación**.
- [ ] **C9.** Paso 3: se ve el aviso de describir sin mostrar el objeto y **no** se ven características ni foto. Escribir `Llavero de balón con tres llaves y una roja` y **Guardar y comparar**.
- [ ] **C10.** Paso 4: a la izquierda lo que describió y su reporte de pérdida; a la derecha las características y la foto del objeto.
- [ ] **C11.** Marcar **Aprobar** sin motivo y **Registrar decisión**. Resultado esperado: *"El motivo es obligatorio…"* (RF12).
- [ ] **C12.** Escribir el motivo `Describió el llavero de balón y la llave roja` y registrar. Resultado esperado: paso 5 con *"Reclamación aprobada por … el …"* (RF13, RF14).
- [ ] **C13.** **Registrar entrega** sin foto. Resultado esperado: *"La foto de la entrega es obligatoria…"* (RF22).
- [ ] **C14.** Tomar o subir la foto, escribir una observación y **Registrar entrega**. Resultado esperado: *"Entrega registrada"* y *"…su reporte de pérdida como recuperado"*.

**C.4 Trazabilidad del flujo** (RF16, RF17, RF18, RF27)
- [ ] **C15.** **Objetos → Entregados**: el llavero aparece. En su detalle: aviso de que ya se entregó, **sin** botón *Editar datos*, la entrega con la foto y la reclamación aprobada con su motivo.
- [ ] **C16.** **Objetos → Recuperados** (reportes): aparece el reporte de la estudiante.
- [ ] **C17.** **Personas** → detalle de la estudiante: su reporte (Recuperado), su reclamación (Aprobada) y las llaves en *Objetos que se ha llevado*.
- [ ] **C18.** **Historial → Entregas**: la entrega del llavero con su foto. **Historial → Aprobadas**: la reclamación con lo que describió, el motivo, quién decidió y cuándo.
- [ ] **C19.** El contador *Reportes abiertos* del Mostrador sigue en **3** y *Objetos disponibles* también en **3**: se sumó un reporte y un objeto, y los dos se cerraron.

## D. Reglas de negocio y casos especiales

**D.1 Posible fraude: el objeto ya se entregó** (RF23, RF26)
- [ ] **D1.** **Viene a reclamar** → **+ Registrar persona nueva** como **Docente**: `Docente Verificación Dos`, `docente.dos@example.edu.co`, `3000005678`. Resultado esperado: al elegir *Docente* se ocultan código y carrera.
- [ ] **D2.** En el paso 2, marcar **Incluir objetos ya entregados**, elegir el llavero y registrar la reclamación. Describir `Llavero de balón con mis tres llaves`.
- [ ] **D3.** Paso 4. Resultado esperado: aviso en rojo de que el objeto ya se entregó a la estudiante, la caja con esa entrega (qué describió, motivo y foto) y **Aprobar desactivado**.
- [ ] **D4.** Registrar el incidente con *"…es el dueño real"* marcado. Resultado esperado: *"Incidente registrado…"*. Luego **Rechazar** con motivo. Resultado esperado: *"Reclamación rechazada"*.
- [ ] **D5.** **Historial → Incidentes**: el incidente con la estudiante como quien se lo llevó y el docente como dueño real. El llavero sigue **Entregado**: no se borra nada.

**D.2 Alerta de intentos fallidos** (RF24)
- [ ] **D6.** **Viene a reclamar** → buscar `Pedro`. Resultado esperado: en la lista dice *"Con alerta"* y, al elegirlo, aparece la alerta en rojo. Clic en **Cancelar** (no se registra nada).
- [ ] **D7.** **Alertas**: Pedro con 3 objetos distintos rechazados y el motivo de cada rechazo.

**D.3 Edición y registros cerrados** (RF25, RF29)
- [ ] **D8.** **Objetos → Disponibles** → detalle de los **Audífonos** → **Editar datos** → cambiar el lugar → **Guardar cambios**. Resultado esperado: se ve el lugar nuevo y *"Última modificación"* con el encargado y la hora.
- [ ] **D9.** **Objetos → Vencidos** (reportes): la chaqueta de María. En su detalle: aviso de que venció y sin botón para editar.

**D.4 Retomar una reclamación** (RF08)
- [ ] **D10.** **Pendientes**: la reclamación de María. **Continuar** abre el mostrador en *"Comparar y decidir"*. Volver sin decidir.

## E. Validaciones y mensajes de error

Todos los errores deben salir **en rojo, en la misma pantalla y sin ventanas emergentes**.

- [ ] **E1.** Registrar una persona con código `TX123`. Resultado esperado: mensaje sobre el formato del código estudiantil.
- [ ] **E2.** Registrar una persona con correo `correo-malo`. Resultado esperado: *"El correo no tiene un formato válido…"*.
- [ ] **E3.** Registrar un estudiante con un código que ya existe (`T00000001`). Resultado esperado: mensaje de que el código ya está registrado.
- [ ] **E4.** **Entrega un objeto** con una fecha futura. Resultado esperado: *"La fecha no puede ser posterior a hoy."*
- [ ] **E5.** En el paso de foto, subir un archivo que no sea imagen (un `.txt` o `.pdf`). Resultado esperado: *"El archivo debe ser una imagen JPG, PNG o WEBP."*
- [ ] **E6.** Subir una imagen de más de 5 MB. Resultado esperado: *"La foto supera el tamaño máximo de 5 MB."*
- [ ] **E7.** Bloquear el permiso de la cámara (ícono del candado junto a la dirección → Cámara → Bloquear) y presionar **Tomar foto**. Resultado esperado: *"No se pudo acceder a la cámara…"* y el botón **Subir archivo** sigue funcionando.

## F. Persistencia

Comprueba que los datos se guardan y se recuperan correctamente (SQLite y carpeta de fotos).

- [ ] **F1.** Apagar el backend y el frontend, y volver a encenderlos **sin** ejecutar `seed.py`.
- [ ] **F2.** Resultado esperado: la estudiante, el docente, el llavero (Entregado), el incidente y el cambio de lugar de los audífonos siguen ahí.
- [ ] **F3.** Las fotos del llavero y de su entrega se siguen viendo.
- [ ] **F4.** `python seed.py` vuelve a dejar solo los datos de prueba originales (los contadores de **B3**). Así se reinicia la base antes de una demostración.

## G. Integración entre los dos computadores

- [ ] **G1.** `git status` está limpio en los dos equipos: `.env`, `backend/venv/`, `backend/lf.db`, `backend/uploads/` y `frontend/node_modules/` **no** aparecen como cambios (los ignora `.gitignore`).
- [ ] **G2.** Cada integrante tiene **su propia** `SECRET_KEY` en su `.env` y ninguna aparece en GitHub.
- [ ] **G3.** Un integrante hace un cambio pequeño (por ejemplo, una línea en este archivo), lo sube a `main` y el otro lo trae con `git pull --rebase origin main` sin conflictos.

---

## Registro de fallas

Una fila por falla. Al corregirla se anota el commit y se vuelve a probar el paso.

| # | Paso | Quién | Qué pasó (y qué se esperaba) | Captura / consola / terminal | Estado | Commit de la corrección |
|---|---|---|---|---|---|---|
| 1 | | | | | Abierta | |

## Cierre de la fase

La Fase 5 se da por terminada cuando:

- [ ] Las secciones A a G están marcadas en los **dos** computadores.
- [ ] Todas las fallas del registro están **Corregidas** y su paso se volvió a probar.
- [ ] El README sigue sirviendo para instalar el proyecto desde cero (sección A) sin pasos adicionales.
