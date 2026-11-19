import { defineConfig } from 'vite';
import { extensions, classicEmberSupport, ember } from '@embroider/vite';
import { babel } from '@rollup/plugin-babel';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // Fixed port: BACKEND_CORS_ORIGINS (.env.example) and playwright.config.ts
  // both expect the web app on 4200.
  server: { port: 4200, strictPort: true },
  plugins: [
    // Tailwind first, before the Ember plugins (ember-scaffold → Styling).
    tailwindcss(),
    classicEmberSupport(),
    ember(),
    // extra plugins here
    babel({
      babelHelpers: 'runtime',
      extensions,
    }),
  ],
});
