/*
  Lógica del componente BuscarPersona.astro (RF02, RF19, RF24).

  Búsqueda:
  - Si lo escrito parece un código estudiantil (T00000001, t1 o 1), se busca
    con GET /personas/codigo/{codigo}: el backend completa la T y los ceros.
  - Si no, se busca con GET /personas?buscar=texto (nombre, código o correo).

  Alerta de intentos fallidos (RF24): se consulta GET /personas/alertas una
  vez y se guarda en un mapa por id de persona. Si la persona elegida tiene
  la alerta activa, se muestra en rojo. La alerta solo informa: la decisión
  sigue siendo del encargado.
*/
import { api, ErrorApi } from './api.js';
import { escapar, mostrarMensaje, ocultarMensaje, conBoton } from './ui.js';

const PARECE_CODIGO = /^[tT]?\d{1,8}$/;

/** Tipo de persona en texto, para mostrarlo. */
export const NOMBRE_TIPO = { ESTUDIANTE: 'Estudiante', DOCENTE: 'Docente' };

/**
 * Activa el componente.
 * @param raiz el <div> del componente.
 * @param opciones.alSeleccionar(persona, alerta) se llama al elegir a alguien.
 * @param opciones.alCambiar() se llama al presionar "Cambiar persona".
 */
export function crearBuscarPersona(raiz, { alSeleccionar, alCambiar } = {}) {
  const q = (selector) => raiz.querySelector(selector);
  const zonaBuscar = q('[data-zona-buscar]');
  const formBuscar = q('[data-form-buscar]');
  const texto = q('[data-texto]');
  const errorBuscar = q('[data-error-buscar]');
  const sinResultados = q('[data-sin-resultados]');
  const resultados = q('[data-resultados]');
  const formNueva = q('[data-form-nueva]');
  const zonaElegida = q('[data-elegida]');
  const cajaAlerta = q('[data-alerta]');

  let alertas = null; // Map id -> alerta
  let encontradas = []; // última búsqueda
  let elegida = null;

  async function cargarAlertas() {
    if (alertas) return alertas;
    const lista = await api('/personas/alertas');
    alertas = new Map(lista.map((item) => [item.persona.id, item.alerta]));
    return alertas;
  }

  // ---------- Búsqueda ----------

  formBuscar.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    ocultarMensaje(errorBuscar);
    sinResultados.hidden = true;
    resultados.innerHTML = '';
    const valor = texto.value.trim();
    if (!valor) {
      mostrarMensaje(errorBuscar, 'Escribe el código, el nombre o el correo de la persona.');
      return;
    }
    const boton = formBuscar.querySelector('button[type=submit]');
    await conBoton(boton, 'Buscando…', async () => {
      try {
        if (PARECE_CODIGO.test(valor)) {
          try {
            encontradas = [await api(`/personas/codigo/${encodeURIComponent(valor)}`)];
          } catch (error) {
            if (error instanceof ErrorApi && error.estado === 404) encontradas = [];
            else throw error;
          }
        } else {
          encontradas = await api(`/personas?buscar=${encodeURIComponent(valor)}`);
        }
        await cargarAlertas();
        pintarResultados(valor);
      } catch (error) {
        mostrarMensaje(errorBuscar, error.message);
      }
    });
  });

  function pintarResultados(valor) {
    if (encontradas.length === 0) {
      sinResultados.textContent = `No se encontró a nadie con "${valor}". Si es la primera vez que viene, regístrala con el botón de abajo.`;
      sinResultados.hidden = false;
      return;
    }
    resultados.innerHTML = encontradas
      .map((p, i) => {
        const alerta = alertas.get(p.id);
        return `
        <li>
          <button type="button" class="elegir" data-indice="${i}">
            <span class="elegir-titulo">${escapar(p.nombre)}</span>
            <span class="elegir-detalle">${NOMBRE_TIPO[p.tipo]}${p.codigo ? ` · ${escapar(p.codigo)}` : ''} · ${escapar(p.correo)}</span>
            ${alerta?.activa ? '<span class="etiqueta etiqueta-alerta">Con alerta</span>' : ''}
          </button>
        </li>`;
      })
      .join('');
  }

  resultados.addEventListener('click', (evento) => {
    const boton = evento.target.closest('[data-indice]');
    if (boton) seleccionar(encontradas[Number(boton.dataset.indice)]);
  });

  // ---------- Registro de una persona nueva ----------

  const registro = activarFormPersona(formNueva, {
    alRegistrar: (persona) => seleccionar(persona),
    alCancelar: () => {
      zonaBuscar.hidden = false;
    },
  });

  function abrirRegistro() {
    zonaBuscar.hidden = true;
    registro.abrir(texto.value.trim());
  }

  // ---------- Persona elegida ----------

  async function seleccionar(persona) {
    elegida = persona;
    let alerta = null;
    try {
      alerta = (await cargarAlertas()).get(persona.id) ?? null;
    } catch {
      // Si no se pudo consultar la alerta, se sigue sin ella.
    }

    q('[data-nombre]').textContent = persona.nombre;
    q('[data-tipo]').textContent = NOMBRE_TIPO[persona.tipo];
    const filas = [
      ['Código', persona.codigo],
      ['Carrera', persona.carrera],
      ['Correo', persona.correo],
      ['Teléfono', persona.telefono],
    ].filter(([, valor]) => valor);
    q('[data-datos]').innerHTML = filas
      .map(([nombre, valor]) => `<dt>${nombre}</dt><dd>${escapar(valor)}</dd>`)
      .join('');

    if (alerta?.activa) {
      cajaAlerta.innerHTML = `<strong>Alerta de intentos fallidos.</strong> ${escapar(alerta.mensaje)}`;
      cajaAlerta.hidden = false;
    } else {
      cajaAlerta.hidden = true;
    }

    zonaBuscar.hidden = true;
    formNueva.hidden = true;
    zonaElegida.hidden = false;
    alSeleccionar?.(persona, alerta);
  }

  function reiniciar() {
    elegida = null;
    zonaElegida.hidden = true;
    formNueva.hidden = true;
    zonaBuscar.hidden = false;
    resultados.innerHTML = '';
    sinResultados.hidden = true;
    texto.value = '';
    texto.focus();
  }

  raiz.addEventListener('click', (evento) => {
    const accion = evento.target.closest('[data-accion]')?.dataset.accion;
    if (accion === 'nueva') abrirRegistro();
    if (accion === 'cambiar') {
      reiniciar();
      alCambiar?.();
    }
  });

  return {
    /** Elige a una persona ya conocida (por ejemplo, al llegar con ?persona=ID). */
    seleccionar,
    /** Persona elegida o null. */
    persona: () => elegida,
    reiniciar,
  };
}

/**
 * Activa el formulario de registro de personas (componente FormPersona.astro).
 * @param form el <form data-form-nueva>.
 * @param opciones.alRegistrar(persona) se llama cuando el backend la registró.
 * @param opciones.alCancelar() se llama al presionar "Cancelar".
 * Devuelve { abrir(textoBuscado) }: muestra el formulario vacío y, si lo
 * buscado parecía un código o un nombre, lo deja escrito.
 */
export function activarFormPersona(form, { alRegistrar, alCancelar } = {}) {
  const error = form.querySelector('[data-error-nueva]');
  const radios = [...form.querySelectorAll('input[type=radio]')];
  const tipoElegido = () => radios.find((r) => r.checked).value;

  function ajustarCamposPorTipo() {
    const esEstudiante = tipoElegido() === 'ESTUDIANTE';
    form.querySelectorAll('[data-solo-estudiante]').forEach((campo) => {
      campo.hidden = !esEstudiante;
    });
  }
  radios.forEach((r) => r.addEventListener('change', ajustarCamposPorTipo));

  form.querySelector('[data-accion="cancelar-nueva"]').addEventListener('click', () => {
    form.hidden = true;
    alCancelar?.();
  });

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    ocultarMensaje(error);
    const campos = form.elements;
    const tipo = tipoElegido();
    const datos = {
      nombre: campos.nombre.value.trim(),
      correo: campos.correo.value.trim(),
      telefono: campos.telefono.value.trim(),
    };
    if (tipo === 'ESTUDIANTE') {
      datos.codigo = campos.codigo.value.trim();
      datos.carrera = campos.carrera.value.trim();
    }
    if (Object.values(datos).some((v) => !v)) {
      mostrarMensaje(error, 'Completa todos los campos.');
      return;
    }
    const ruta = tipo === 'ESTUDIANTE' ? '/personas/estudiantes' : '/personas/docentes';
    const boton = form.querySelector('button[type=submit]');
    await conBoton(boton, 'Registrando…', async () => {
      try {
        const persona = await api(ruta, { metodo: 'POST', datos });
        form.hidden = true;
        alRegistrar?.(persona);
      } catch (e) {
        mostrarMensaje(error, e.message);
      }
    });
  });

  return {
    abrir(textoBuscado = '') {
      form.reset();
      ocultarMensaje(error);
      if (PARECE_CODIGO.test(textoBuscado)) form.elements.codigo.value = textoBuscado;
      else if (textoBuscado && !textoBuscado.includes('@')) form.elements.nombre.value = textoBuscado;
      ajustarCamposPorTipo();
      form.hidden = false;
      form.elements.nombre.focus();
    },
  };
}

/** HTML de la caja roja de alerta de intentos fallidos, para otros pasos. */
export function htmlAlerta(alerta) {
  if (!alerta?.activa) return '';
  return `<div class="caja-alerta" role="alert"><strong>Alerta de intentos fallidos.</strong> ${escapar(alerta.mensaje)}</div>`;
}

/** Mapa id de persona → alerta, con las personas que tienen alerta activa (RF24). */
export async function mapaAlertas() {
  const lista = await api('/personas/alertas');
  return new Map(lista.map((item) => [item.persona.id, item.alerta]));
}

/** Enlace al detalle de una persona, con su código si lo tiene. */
export function enlacePersona(persona) {
  const codigo = persona.codigo ? ` <span class="texto-suave">(${escapar(persona.codigo)})</span>` : '';
  return `<a href="/personas/detalle?id=${persona.id}">${escapar(persona.nombre)}</a>${codigo}`;
}
