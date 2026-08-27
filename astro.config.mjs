import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://robothumanoide.org',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  compressHTML: true,

  vite: {
    build: {
      // Sin esto el minificador reescribe @media (max-width: 700px)
      // como @media (width<=700px), sintaxis que Safari ignora antes
      // de la 16.4: esos móviles verían la maqueta de escritorio.
      cssTarget: ['safari13', 'chrome80', 'firefox78', 'edge88'],
    },
  },
});
