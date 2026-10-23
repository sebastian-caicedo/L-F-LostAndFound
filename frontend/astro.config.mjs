// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  vite: {
    // Lee las variables del .env de la RAÍZ del repositorio (el mismo que usa
    // el backend), para no tener dos archivos .env. Astro solo deja llegar al
    // navegador las variables que empiezan con PUBLIC_ (como PUBLIC_API_URL);
    // las demás (SECRET_KEY, contraseñas) nunca salen del servidor.
    envDir: '../',
  },
});
