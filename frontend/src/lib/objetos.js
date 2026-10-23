/*
  Piezas para mostrar objetos en las pantallas: categorías sugeridas, datos
  del objeto, su foto protegida y la entrega previa (RF26).
*/
import { api, apiImagen } from './api.js';
import { escapar, fecha, fechaHora, etiquetaEstado } from './ui.js';

/**
 * Categorías sugeridas al escribir el tipo de objeto. Son solo sugerencias
 * (se puede escribir otra), pero usar siempre el mismo nombre ayuda a que
 * las coincidencias entre perdidos y encontrados funcionen (RF05).
 */
export const CATEGORIAS = [
  'Audífonos',
  'Billetera',
  'Botella',
  'Calculadora',
  'Cargador',
  'Carné',
  'Chaqueta',
  'Celular',
  'Computador portátil',
  'Cuaderno',
  'Gafas',
  'Libro',
  'Llaves',
  'Maleta',
  'Sombrilla',
  'Termo',
];

/** Una línea corta para listas: "Celular · Teléfono con forro · Biblioteca". */
export function resumenObjeto(objeto) {
  const partes = [escapar(objeto.descripcion)];
  if (objeto.tipo_registro === 'ENCONTRADO') {
    if (objeto.lugar_encontrado) partes.push(escapar(objeto.lugar_encontrado));
    if (objeto.fecha_encontrado) partes.push(`encontrado el ${fecha(objeto.fecha_encontrado)}`);
  } else if (objeto.fecha_reporte) {
    partes.push(`perdido el ${fecha(objeto.fecha_reporte)}`);
  }
  return partes.join(' · ');
}

/**
 * Datos de un objeto como lista "nombre: valor". Solo incluye las
 * características si vienen en el objeto (la lista general no las trae).
 * "extra" agrega filas al final, por ejemplo [['Registrado', '...']].
 */
export function htmlDatosObjeto(objeto, extra = []) {
  const filas = [
    ['Tipo', escapar(objeto.tipo)],
    ['Estado', etiquetaEstado(objeto.estado)],
    ['Descripción', escapar(objeto.descripcion)],
    ['Características', objeto.caracteristicas !== undefined ? escapar(objeto.caracteristicas) : null],
    ['Encontrado el', objeto.fecha_encontrado ? fecha(objeto.fecha_encontrado) : null],
    ['Lugar', objeto.lugar_encontrado ? escapar(objeto.lugar_encontrado) : null],
    ['Perdido el', objeto.fecha_reporte ? fecha(objeto.fecha_reporte) : null],
    ['Vence el', objeto.vence_el ? fecha(objeto.vence_el) : null],
    ...extra,
  ].filter(([, valor]) => valor);
  return `<dl class="datos">${filas.map(([n, v]) => `<dt>${n}</dt><dd>${v}</dd>`).join('')}</dl>`;
}

/**
 * Carga en los <img data-foto="/ruta"> de un contenedor las fotos protegidas.
 * Se piden con el token (apiImagen); si alguna falla, se oculta.
 */
export function cargarFotos(contenedor) {
  contenedor.querySelectorAll('img[data-foto]').forEach(async (img) => {
    try {
      img.src = await apiImagen(img.dataset.foto);
    } catch {
      img.hidden = true;
    }
  });
}

/** HTML de una foto protegida, para usar con cargarFotos(). */
export function htmlFoto(ruta, texto) {
  return ruta ? `<img class="foto-objeto" data-foto="${escapar(ruta)}" alt="${escapar(texto)}" />` : '';
}

/**
 * Caja con la entrega previa del objeto (RF26): a quién se entregó, cuándo,
 * qué describió esa persona y con qué motivo se aprobó, más la foto de la
 * entrega. Sirve para evaluar si quien reclama ahora es el dueño real.
 */
export function htmlEntregaPrevia(previa) {
  if (!previa) return '';
  const p = previa.persona;
  const dada = previa.descripcion_dada;
  return `
    <div class="caja-entrega-previa">
      <h3>Este objeto ya se entregó</h3>
      <dl class="datos">
        <dt>Entregado a</dt><dd>${escapar(p.nombre)}${p.codigo ? ` (${escapar(p.codigo)})` : ''}</dd>
        <dt>Fecha</dt><dd>${fechaHora(previa.fecha_hora)}</dd>
        <dt>Lo entregó</dt><dd>${escapar(previa.entregado_por.nombre)}</dd>
        <dt>Describió</dt><dd>${dada ? escapar(dada.caracteristicas) : '—'}</dd>
        ${dada?.observaciones ? `<dt>Observaciones</dt><dd>${escapar(dada.observaciones)}</dd>` : ''}
        <dt>Motivo de aprobación</dt><dd>${escapar(previa.motivo_aprobacion)}</dd>
        ${previa.incidente ? `<dt>Incidente</dt><dd>Ya tiene un incidente registrado (${fechaHora(previa.incidente.fecha_hora)}).</dd>` : ''}
      </dl>
      ${htmlFoto(previa.foto_url, 'Foto de la entrega')}
    </div>`;
}

/** Lista de objetos con un filtro. Devuelve [] si no hay. */
export function listarObjetos(parametros) {
  const consulta = new URLSearchParams(
    Object.entries(parametros).filter(([, v]) => v !== undefined && v !== null && v !== ''),
  );
  return api(`/objetos?${consulta}`);
}

/**
 * Coincidencia vista desde un OBJETO ENCONTRADO (RF28): un reporte de
 * pérdida abierto, con el contacto de quien lo reportó para avisarle.
 */
export function htmlCoincidenciaReporte({ objeto: reporte, reportado_por: p }) {
  return `
    <li class="tarjeta">
      <div class="persona-cabecera">
        <strong>${escapar(p.nombre)}</strong>
        <span class="texto-suave">${escapar(p.telefono)} · ${escapar(p.correo)}</span>
      </div>
      ${htmlDatosObjeto(reporte)}
    </li>`;
}

/**
 * Coincidencia vista desde un REPORTE DE PÉRDIDA (RF05, RF26): un objeto
 * encontrado de la misma categoría, con su entrega si ya se entregó, y el
 * botón para reclamarlo con la persona y el reporte ya elegidos (RF27).
 */
export function htmlCoincidenciaEncontrado({ objeto, entrega_previa }, { personaId, reporteId }) {
  const enlace = `/mostrador/reclamar?persona=${personaId}&objeto=${objeto.id}&reporte=${reporteId}`;
  const boton =
    objeto.estado === 'DISPONIBLE'
      ? `<a class="boton boton-principal" href="${enlace}">Reclamar este objeto</a>`
      : `<a class="boton boton-secundario" href="${enlace}">Reclamar para comparar</a>`;
  return `
    <li class="tarjeta">
      <div class="comparacion">
        <div>
          ${htmlDatosObjeto(objeto)}
          ${htmlFoto(objeto.foto_url, `Foto de ${objeto.tipo}`)}
        </div>
        <div>${htmlEntregaPrevia(entrega_previa)}</div>
      </div>
      <div class="acciones">${boton}</div>
    </li>`;
}

/** Enlace al detalle de un objeto. */
export function enlaceObjeto(objeto, texto = null) {
  return `<a href="/objetos/detalle?id=${objeto.id}">${escapar(texto ?? objeto.tipo)}</a>`;
}

/**
 * Siguiente paso de una reclamación y el botón para retomarla en el
 * mostrador (/mostrador/reclamar?reclamacion=ID). Devuelve null si ya no
 * le falta nada (rechazada o entregada).
 */
export function siguientePaso(reclamacion) {
  const enlace = `/mostrador/reclamar?reclamacion=${reclamacion.id}`;
  if (reclamacion.estado === 'PENDIENTE' && !reclamacion.tiene_informacion) {
    return { texto: 'Tomar la descripción de la persona', boton: 'Continuar', enlace };
  }
  if (reclamacion.estado === 'PENDIENTE') {
    return { texto: 'Comparar y decidir', boton: 'Continuar', enlace };
  }
  if (reclamacion.estado === 'APROBADA' && reclamacion.objeto.estado === 'DISPONIBLE') {
    return { texto: 'Entregar con foto', boton: 'Entregar', enlace };
  }
  return null;
}
