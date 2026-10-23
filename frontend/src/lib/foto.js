/*
  Lógica del selector de foto (componente SelectorFoto.astro).

  Cámara web: el navegador pide permiso para usar la cámara
  (navigator.mediaDevices.getUserMedia). El video se muestra en pantalla y,
  al presionar "Capturar", se copia el cuadro actual a un <canvas> y se
  convierte en una imagen JPG. Solo funciona en "localhost" o con HTTPS:
  es una regla de seguridad de los navegadores.

  Archivo: se usa un <input type="file">. Antes de aceptarlo se revisa el
  tipo y el tamaño; el backend lo vuelve a validar al recibirlo.

  En los dos casos la foto queda como un Blob (un archivo en memoria) que la
  página envía al backend con FormData.
*/

const TIPOS_PERMITIDOS = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_BYTES = 5 * 1024 * 1024;

export function crearSelectorFoto(raiz) {
  const q = (selector) => raiz.querySelector(selector);
  const botones = q('[data-botones]');
  const ayuda = q('[data-ayuda]');
  const zonaCamara = q('[data-camara]');
  const video = q('[data-video]');
  const zonaVista = q('[data-vista]');
  const imagen = q('[data-imagen]');
  const archivo = q('[data-archivo]');
  const error = q('[data-error]');

  let foto = null; // Blob con la foto elegida
  let flujo = null; // MediaStream de la cámara
  let urlVista = null;

  const mostrarError = (texto) => {
    error.textContent = texto;
    error.hidden = false;
  };
  const ocultarError = () => {
    error.hidden = true;
  };

  function apagarCamara() {
    flujo?.getTracks().forEach((pista) => pista.stop());
    flujo = null;
    video.srcObject = null;
    zonaCamara.hidden = true;
  }

  function mostrarVista(blob) {
    foto = blob;
    if (urlVista) URL.revokeObjectURL(urlVista);
    urlVista = URL.createObjectURL(blob);
    imagen.src = urlVista;
    zonaVista.hidden = false;
    botones.hidden = true;
    ayuda.hidden = true;
  }

  function limpiar() {
    apagarCamara();
    foto = null;
    if (urlVista) URL.revokeObjectURL(urlVista);
    urlVista = null;
    imagen.removeAttribute('src');
    zonaVista.hidden = true;
    botones.hidden = false;
    ayuda.hidden = false;
    archivo.value = '';
    ocultarError();
  }

  raiz.addEventListener('click', async (evento) => {
    const accion = evento.target.closest('[data-accion]')?.dataset.accion;
    if (!accion) return;
    ocultarError();

    if (accion === 'camara') {
      if (!navigator.mediaDevices?.getUserMedia) {
        mostrarError('Este navegador no permite usar la cámara. Usa "Subir archivo".');
        return;
      }
      try {
        flujo = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = flujo;
        zonaCamara.hidden = false;
        botones.hidden = true;
      } catch {
        mostrarError(
          'No se pudo acceder a la cámara. Revisa que esté conectada y que el navegador tenga permiso, o usa "Subir archivo".',
        );
      }
    }

    if (accion === 'capturar') {
      const lienzo = document.createElement('canvas');
      lienzo.width = video.videoWidth || 640;
      lienzo.height = video.videoHeight || 480;
      lienzo.getContext('2d').drawImage(video, 0, 0, lienzo.width, lienzo.height);
      const blob = await new Promise((resolver) => lienzo.toBlob(resolver, 'image/jpeg', 0.9));
      apagarCamara();
      if (blob) mostrarVista(blob);
      else mostrarError('No se pudo capturar la foto. Intenta de nuevo.');
    }

    if (accion === 'cancelar') {
      apagarCamara();
      botones.hidden = false;
    }

    if (accion === 'quitar') {
      limpiar();
    }
  });

  archivo.addEventListener('change', () => {
    ocultarError();
    const elegido = archivo.files?.[0];
    if (!elegido) return;
    if (!TIPOS_PERMITIDOS.includes(elegido.type)) {
      mostrarError('El archivo debe ser una imagen JPG, PNG o WEBP.');
      archivo.value = '';
      return;
    }
    if (elegido.size > MAX_BYTES) {
      mostrarError('La foto supera el tamaño máximo de 5 MB.');
      archivo.value = '';
      return;
    }
    mostrarVista(elegido);
  });

  // Si el encargado sale de la página con la cámara encendida, se apaga.
  window.addEventListener('pagehide', apagarCamara);

  return {
    /** La foto elegida (Blob) o null si no hay ninguna. */
    obtener: () => foto,
    limpiar,
  };
}
