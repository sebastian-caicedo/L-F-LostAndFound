/*
  Controla los flujos por pasos del mostrador.

  Cada paso es una <section data-paso="N">. Solo se muestra el paso actual;
  los demás quedan ocultos. El indicador (componente Pasos.astro) marca el
  paso actual y los que ya se completaron.
*/
export function crearPasos() {
  const secciones = [...document.querySelectorAll('[data-paso]')];
  const indicadores = [...document.querySelectorAll('[data-indicador]')];
  let actual = 1;

  function ir(numero) {
    actual = numero;
    for (const seccion of secciones) {
      seccion.hidden = seccion.dataset.paso !== String(numero);
    }
    for (const indicador of indicadores) {
      const n = Number(indicador.dataset.indicador);
      indicador.classList.toggle('actual', n === numero);
      indicador.classList.toggle('hecho', n < numero);
    }
    window.scrollTo({ top: 0 });
    // Lleva el cursor al primer campo visible del paso, para escribir de una
    // vez, sin mover la página (así se ve el paso desde arriba).
    const seccion = secciones.find((s) => s.dataset.paso === String(numero));
    const campo = [...(seccion?.querySelectorAll('input:not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea, select') ?? [])]
      .find((c) => c.offsetParent !== null);
    campo?.focus({ preventScroll: true });
  }

  ir(1);
  return { ir, actual: () => actual };
}
