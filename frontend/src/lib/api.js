/*
  Cliente de la API de L&F.

  Todas las pantallas hablan con el backend a través de este archivo. Así,
  el manejo del token, de los errores y de la sesión vencida está en un
  solo lugar y no se repite en cada página.

  Cómo funciona la sesión (RF01):
  1. iniciarSesion() envía usuario y contraseña a POST /auth/login.
  2. El backend devuelve un token que dura 8 horas.
  3. El token se guarda en el navegador (localStorage) y se envía en cada
     petición en el encabezado "Authorization: Bearer <token>".
  4. cerrarSesion() borra el token. Si el backend responde 401 (token
     vencido o inválido), también se borra y se vuelve al inicio de sesión.

  Se usa localStorage (y no sessionStorage) para que la sesión siga abierta
  aunque se cierre la pestaña: el encargado decide cuándo cerrarla.
*/

/** Dirección del backend. Se lee de PUBLIC_API_URL en el .env de la raíz. */
export const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

const CLAVE_TOKEN = 'lf_token';

export function obtenerToken() {
  return localStorage.getItem(CLAVE_TOKEN);
}

export function haySesion() {
  return Boolean(obtenerToken());
}

function guardarToken(token) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

/** Cierra la sesión: borra el token y vuelve a la pantalla de inicio de sesión. */
export function cerrarSesion(motivo = '') {
  localStorage.removeItem(CLAVE_TOKEN);
  const destino = motivo ? `/login?motivo=${encodeURIComponent(motivo)}` : '/login';
  window.location.href = destino;
}

/** Error que viene del backend, con un mensaje listo para mostrar al encargado. */
export class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.estado = estado;
  }
}

/**
 * Convierte la respuesta de error del backend en un texto para el encargado.
 * - Errores de negocio: {"detail": "mensaje en español"}.
 * - Errores de validación (422 de Pydantic): {"detail": [{"loc": [...], "msg": "..."}]}.
 */
function mensajeDeError(cuerpo, estado) {
  const detalle = cuerpo?.detail;
  if (typeof detalle === 'string') {
    return detalle;
  }
  if (Array.isArray(detalle) && detalle.length > 0) {
    return detalle
      .map((e) => {
        const campo = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : '';
        const texto = String(e.msg || '').replace(/^Value error, /, '');
        return campo && typeof campo === 'string' ? `${campo}: ${texto}` : texto;
      })
      .join(' · ');
  }
  return `Ocurrió un error inesperado (código ${estado}). Intenta de nuevo.`;
}

/**
 * Hace una petición a la API con el token de la sesión.
 * - Si "datos" es un FormData (fotos), se envía tal cual.
 * - Si es un objeto, se envía como JSON.
 * Devuelve el JSON de la respuesta o lanza ErrorApi con un mensaje claro.
 */
export async function api(ruta, { metodo = 'GET', datos } = {}) {
  const opciones = { method: metodo, headers: {} };
  const token = obtenerToken();
  if (token) {
    opciones.headers.Authorization = `Bearer ${token}`;
  }
  if (datos instanceof FormData) {
    opciones.body = datos;
  } else if (datos !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(datos);
  }

  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, opciones);
  } catch {
    throw new ErrorApi(
      'No se pudo conectar con el servidor. Verifica que el backend esté encendido.',
      0,
    );
  }

  if (respuesta.status === 401) {
    // Sesión vencida o token inválido: se cierra la sesión.
    cerrarSesion('vencida');
    throw new ErrorApi('Tu sesión venció. Inicia sesión de nuevo.', 401);
  }

  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new ErrorApi(mensajeDeError(cuerpo, respuesta.status), respuesta.status);
  }
  return cuerpo;
}

/**
 * Inicia sesión (RF01). Devuelve true si las credenciales son correctas y
 * false si no lo son. Lanza ErrorApi si no hay conexión con el servidor.
 *
 * El backend recibe el usuario y la contraseña como formulario
 * (username, password), que es el formato estándar de OAuth2.
 */
export async function iniciarSesion(usuario, contrasena) {
  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: usuario, password: contrasena }),
    });
  } catch {
    throw new ErrorApi(
      'No se pudo conectar con el servidor. Verifica que el backend esté encendido.',
      0,
    );
  }
  if (respuesta.status === 401) {
    return false;
  }
  if (!respuesta.ok) {
    throw new ErrorApi(`El servidor respondió con un error (código ${respuesta.status}).`, respuesta.status);
  }
  const { access_token } = await respuesta.json();
  guardarToken(access_token);
  return true;
}

/**
 * Descarga una foto protegida (necesita el token) y devuelve una dirección
 * temporal para usarla en <img src>. Las fotos no son públicas, por eso no
 * se puede poner la ruta de la API directamente en el <img>.
 */
export async function apiImagen(ruta) {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    headers: { Authorization: `Bearer ${obtenerToken()}` },
  });
  if (respuesta.status === 401) {
    cerrarSesion('vencida');
    throw new ErrorApi('Tu sesión venció. Inicia sesión de nuevo.', 401);
  }
  if (!respuesta.ok) {
    throw new ErrorApi('No se pudo cargar la foto.', respuesta.status);
  }
  return URL.createObjectURL(await respuesta.blob());
}

