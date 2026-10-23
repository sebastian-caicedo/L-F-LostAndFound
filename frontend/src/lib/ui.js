/*
  Utilidades de interfaz que comparten todas las pantallas: mensajes,
  formato de fechas, nombres de estados y protección del texto que se
  inserta en la página.
*/

/** Atajo para document.getElementById. */
export const $ = (id) => document.getElementById(id);

/**
 * Escapa un texto antes de insertarlo como HTML. Así, si alguien escribe
 * "<script>" en una descripción, se muestra como texto y no se ejecuta.
 */
export function escapar(texto) {
  return String(texto ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

/** "2026-10-07" o "2026-10-07T08:15:00" -> "07/10/2026". */
export function fecha(valor) {
  if (!valor) return '';
  const [anio, mes, dia] = String(valor).slice(0, 10).split('-');
  return `${dia}/${mes}/${anio}`;
}

/** "2026-10-07T08:15:00" -> "07/10/2026 08:15". */
export function fechaHora(valor) {
  if (!valor) return '';
  return `${fecha(valor)} ${String(valor).slice(11, 16)}`;
}

/** Fecha de hoy en formato AAAA-MM-DD, para los campos de fecha. */
export function hoy() {
  const d = new Date();
  const dos = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

/** Nombre en español de cada estado, para mostrarlo al encargado. */
export const NOMBRE_ESTADO = {
  PERDIDO: 'Reporte abierto',
  RECUPERADO: 'Recuperado',
  VENCIDO: 'Vencido',
  DISPONIBLE: 'Disponible',
  ENTREGADO: 'Entregado',
  PENDIENTE: 'Pendiente',
  APROBADA: 'Aprobada',
  RECHAZADA: 'Rechazada',
};

/** Etiqueta de color para un estado. */
export function etiquetaEstado(estado) {
  return `<span class="etiqueta etiqueta-${estado.toLowerCase()}">${NOMBRE_ESTADO[estado] ?? estado}</span>`;
}

/** Muestra un mensaje (de error o de confirmación) en un elemento de la página. */
export function mostrarMensaje(elemento, texto) {
  elemento.textContent = texto;
  elemento.hidden = false;
}

export function ocultarMensaje(elemento) {
  elemento.hidden = true;
  elemento.textContent = '';
}

/**
 * Ejecuta una acción asíncrona desactivando el botón mientras tanto, para
 * evitar que el encargado envíe dos veces lo mismo con un doble clic.
 */
export async function conBoton(boton, textoCargando, accion) {
  const textoOriginal = boton.textContent;
  boton.disabled = true;
  boton.textContent = textoCargando;
  try {
    return await accion();
  } finally {
    boton.disabled = false;
    boton.textContent = textoOriginal;
  }
}
