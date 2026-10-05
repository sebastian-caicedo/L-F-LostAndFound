# L&F — Lost And Found

Sistema web para la **gestión de objetos perdidos y encontrados dentro de una institución universitaria**. La solución permite al personal encargado registrar objetos, gestionar reclamaciones, verificar la posible pertenencia de un objeto y mantener la trazabilidad de las decisiones y entregas realizadas.

---

## 📌 Descripción del proyecto

En el entorno universitario es común que estudiantes pierdan objetos personales dentro de las instalaciones, mientras que otros estudiantes, profesores o trabajadores pueden encontrarlos y entregarlos al personal encargado.

Cuando este proceso se gestiona mediante mecanismos informales, puede resultar difícil:

* Saber qué objetos han sido encontrados.
* Registrar adecuadamente las características de cada objeto.
* Identificar a la persona relacionada con un objeto perdido.
* Verificar que una reclamación corresponda realmente al propietario.
* Mantener un historial de las decisiones tomadas.
* Llevar un registro de los objetos que finalmente fueron entregados.

**L&F (Lost And Found)** busca centralizar este proceso mediante una aplicación web que permita al encargado registrar y gestionar la información relacionada con objetos perdidos, objetos encontrados y reclamaciones.

Una característica importante del sistema es la **verificación mediante comparación de características**. El encargado podrá consultar la información registrada del objeto encontrado y compararla con las características proporcionadas por la persona que reclama el objeto antes de tomar una decisión.

La decisión final sobre una reclamación será tomada por el encargado, quien deberá registrar si la reclamación es aprobada o rechazada, junto con el motivo, la fecha y el responsable de la decisión.

---

## 🎯 Objetivo

Desarrollar un sistema web que permita gestionar de manera organizada y trazable el proceso de **registro, reclamación, verificación, decisión y entrega de objetos perdidos y encontrados dentro de una institución universitaria**.

### Objetivos específicos

1. Registrar estudiantes relacionados con procesos de pérdida o reclamación.
2. Registrar objetos perdidos y sus características.
3. Registrar objetos encontrados y sus características.
4. Consultar los objetos registrados.
5. Registrar reclamaciones asociando un estudiante con un objeto encontrado.
6. Registrar la información proporcionada por el reclamante.
7. Facilitar al encargado la comparación entre la información del objeto y la información proporcionada por el reclamante.
8. Permitir aprobar o rechazar una reclamación.
9. Registrar obligatoriamente el motivo de la decisión.
10. Mantener la trazabilidad del encargado responsable y de la fecha de cada decisión.
11. Registrar la entrega de los objetos cuya reclamación haya sido aprobada.
12. Mantener un historial básico de reclamaciones, decisiones y entregas.

---

## 👤 Usuario del sistema

En el alcance actual del proyecto, el **encargado de objetos perdidos** es el usuario directo de la aplicación.

El encargado es responsable de:

* Autenticarse en el sistema.
* Registrar estudiantes.
* Registrar objetos perdidos.
* Registrar objetos encontrados.
* Consultar objetos.
* Registrar reclamaciones.
* Registrar la información proporcionada por el reclamante.
* Revisar y comparar la información de una reclamación.
* Aprobar o rechazar reclamaciones.
* Registrar el motivo de la decisión.
* Registrar la entrega de objetos aprobados.
* Consultar el historial de reclamaciones, decisiones y entregas.

El **estudiante no utiliza directamente la aplicación** dentro del alcance actual. Sus datos son registrados por el encargado cuando participa en un proceso de pérdida o reclamación.

---

## 🔄 Flujo principal del sistema

El proceso principal de L&F puede resumirse de la siguiente manera:

```text
Encargado
    │
    ▼
Iniciar sesión
    │
    ▼
Registrar estudiante
    │
    ├──────────────► Registrar objeto perdido
    │
    └──────────────► Registrar objeto encontrado
                              │
                              ▼
                     Objeto disponible
                              │
                              ▼
                    Registrar reclamación
                              │
                              ▼
                Registrar información del reclamante
                              │
                              ▼
                    Revisar reclamación
                              │
                              ▼
                 Comparar características
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 Aprobar             Rechazar
                    │                   │
                    ▼                   ▼
              Registrar entrega    Registrar motivo
                    │
                    ▼
            Actualizar estado
                    │
                    ▼
                 Historial
```

---

## ⚙️ Funcionalidades principales

### 🔐 Autenticación

El sistema permite al encargado iniciar sesión mediante sus credenciales y acceder únicamente a las funcionalidades autorizadas.

### 👨‍🎓 Registro de estudiantes

Permite registrar los datos básicos de un estudiante que estén relacionados con un objeto perdido o con una reclamación.

### 📦 Registro de objetos perdidos

Permite registrar un objeto que un estudiante reporta como perdido junto con sus características relevantes.

### 🔎 Registro de objetos encontrados

Permite registrar objetos encontrados y almacenar información como sus características, lugar y fecha de hallazgo.

### 📋 Consulta de objetos

Permite consultar los objetos registrados y visualizar la información necesaria para la gestión de pérdidas y posibles reclamaciones.

### 📝 Gestión de reclamaciones

Permite registrar una reclamación asociando un estudiante con un objeto encontrado disponible.

### 🔍 Verificación de reclamaciones

El encargado puede visualizar y comparar:

* Las características registradas del objeto encontrado.
* La información proporcionada por el reclamante.

El sistema **facilita la comparación**, pero la decisión final corresponde al encargado.

### ✅ Aprobación de reclamaciones

Cuando el encargado determina que existen elementos suficientes para establecer que el objeto corresponde al reclamante, puede aprobar la reclamación.

La aprobación requiere registrar un motivo y queda asociada al encargado responsable y a la fecha y hora de la decisión.

### ❌ Rechazo de reclamaciones

Cuando la información no es suficiente para establecer la pertenencia del objeto, el encargado puede rechazar la reclamación.

El rechazo también requiere registrar el motivo de la decisión.

### 📦 Registro de entrega

Cuando una reclamación es aprobada, el encargado puede registrar la entrega del objeto y actualizar su estado para evitar que vuelva a aparecer como disponible.

### 📚 Historial

El sistema conserva información relacionada con:

* Reclamaciones.
* Decisiones.
* Encargados responsables.
* Fechas de decisión.
* Motivos de aprobación o rechazo.
* Entregas realizadas.

---

## 📋 Requerimientos funcionales principales

| ID   | Requerimiento                                                                     |
| ---- | --------------------------------------------------------------------------------- |
| RF01 | Autenticar al encargado mediante sus credenciales.                                |
| RF02 | Registrar los datos del estudiante relacionado con un proceso.                    |
| RF03 | Registrar objetos perdidos y sus características.                                 |
| RF04 | Registrar objetos encontrados y sus características.                              |
| RF05 | Consultar los objetos registrados.                                                |
| RF06 | Registrar reclamaciones asociando estudiantes y objetos encontrados.              |
| RF07 | Registrar las características proporcionadas por el reclamante.                   |
| RF08 | Consultar reclamaciones pendientes.                                               |
| RF09 | Mostrar la información del objeto y del reclamante para facilitar su comparación. |
| RF10 | Aprobar una reclamación.                                                          |
| RF11 | Rechazar una reclamación.                                                         |
| RF12 | Exigir un motivo para aprobar o rechazar una reclamación.                         |
| RF13 | Registrar el encargado responsable de la decisión.                                |
| RF14 | Registrar la fecha y hora de la decisión.                                         |
| RF15 | Registrar la entrega de un objeto cuya reclamación fue aprobada.                  |
| RF16 | Actualizar el estado del objeto después de la entrega.                            |
| RF17 | Consultar el historial de reclamaciones y decisiones.                             |
| RF18 | Consultar el historial de entregas.                                               |

---

## 🚫 Funcionalidades fuera del alcance

Para mantener el proyecto como un **Producto Mínimo Viable (MVP)**, las siguientes funcionalidades no hacen parte del alcance actual:

* Reconocimiento de objetos mediante inteligencia artificial.
* Reconocimiento facial.
* Determinación automática del propietario mediante inteligencia artificial.
* Chat entre estudiantes y encargados.
* Pagos o transacciones económicas.
* Geolocalización avanzada.
* Sistema de reputación de usuarios.
* Integración con redes sociales.
* Aplicación móvil nativa independiente.
* Integraciones complejas con sistemas institucionales externos.
* Automatización completa de la decisión de una reclamación.
* Rol independiente de supervisor.

---

## 🏗️ Arquitectura general

La solución está planteada como una aplicación web compuesta por una interfaz frontend, un backend encargado de la lógica del sistema y una base de datos para almacenar la información.

```text
┌──────────────────────────┐
│       Encargado          │
│     Usuario directo      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│        Frontend          │
│      Aplicación web      │
└────────────┬─────────────┘
             │ HTTP / API
             ▼
┌──────────────────────────┐
│         Backend          │
│   Lógica de aplicación   │
│                          │
│ - Autenticación          │
│ - Estudiantes            │
│ - Objetos                │
│ - Reclamaciones          │
│ - Verificación           │
│ - Decisiones             │
│ - Entregas               │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       Base de datos      │
│                          │
│ - Usuarios/encargados    │
│ - Estudiantes            │
│ - Objetos                │
│ - Reclamaciones          │
│ - Decisiones             │
│ - Entregas               │
└──────────────────────────┘
```

---

## 🛠️ Tecnologías

Las tecnologías utilizadas actualmente en el proyecto son:

| Componente           | Tecnología            |
| -------------------- | --------------------- |
| Frontend             | Astro                 |
| Backend              | FastAPI / Python      |
| Base de datos        | SQLite                |
| Control de versiones | Git / GitHub          |
| Gestión del proyecto | Jira / Trello / Taiga |

---

## 📁 Estructura del proyecto

La estructura del repositorio puede evolucionar conforme avance el desarrollo. Actualmente se contemplan, entre otros elementos, los siguientes:

```text
L-F-LostAndFound/
│
├── docs/
│   └── Documentación del proyecto
│
├── README.md
├── .env.example
└── ...
```

---

## 🚀 Instalación

### Prerrequisitos

Antes de ejecutar el proyecto se requiere tener instalado:

* Git
* Python
* Node.js y npm
* Las dependencias correspondientes del frontend y backend

### Clonar el repositorio

```bash
git clone https://github.com/sebastian-caicedo/L-F-LostAndFound.git
cd L-F-LostAndFound
```

### Configuración

Crear las variables de entorno necesarias a partir del archivo:

```text
.env.example
```

No se deben subir al repositorio contraseñas, tokens, claves privadas ni otras credenciales reales.

---

## ▶️ Ejecución

La ejecución del sistema se divide en sus componentes principales:

### Backend

El backend está desarrollado utilizando **FastAPI con Python** y se encarga de la lógica de negocio y comunicación con la base de datos.

### Frontend

El frontend está desarrollado utilizando **Astro** y proporciona la interfaz web mediante la cual el encargado interactúa con el sistema.

> Los comandos específicos de instalación y ejecución se documentarán y actualizarán conforme avance la implementación del proyecto.

---

## 🧪 Pruebas

El proyecto contempla pruebas orientadas principalmente a verificar:

* Autenticación y autorización.
* Validación de datos.
* Registro de objetos.
* Registro de reclamaciones.
* Comparación de información.
* Aprobación y rechazo de reclamaciones.
* Registro obligatorio del motivo de decisión.
* Registro de entregas.
* Actualización del estado de los objetos.
* Trazabilidad de las decisiones.

---

## 📐 Documentación UML

El proyecto cuenta con modelos UML orientados a representar la estructura y comportamiento de la solución:

* Diagrama de casos de uso.
* Diagrama de clases.
* Diagramas de secuencia.
* Diagrama de actividades.
* Diagrama de componentes.
* Diagrama de despliegue.

Estos diagramas deben mantenerse alineados con los requerimientos y con la implementación del sistema.

---

## 👥 Equipo

**Sebastián Caicedo**
**Javier Carta**

### Asignatura

Ingeniería de Software — Séptimo semestre

### Docente

Aisner José Marrugo Juliao

### Fecha de inicio

24/08/2026

---

## 📌 Estado del proyecto

El proyecto se encuentra en proceso de desarrollo como **Producto Mínimo Viable (MVP)**.

Las funcionalidades se implementarán de manera incremental, priorizando el flujo principal:

**Registro → Reclamación → Verificación → Decisión → Entrega → Trazabilidad**

---

## 📄 Proyecto de Aula

L&F — Lost And Found forma parte del Proyecto de Aula de la asignatura **Ingeniería de Software**.

El desarrollo busca aplicar prácticas de:

* Ingeniería de requisitos.
* Historias de usuario.
* Modelado UML.
* Diseño arquitectónico.
* Desarrollo incremental.
* Pruebas de software.
* Control de versiones.
* Gestión ágil del proyecto.
* Trazabilidad entre requisitos, diseño e implementación.

---

## 🔗 Repositorio

[Repositorio oficial de L&F — Lost And Found](https://github.com/sebastian-caicedo/L-F-LostAndFound.git)
