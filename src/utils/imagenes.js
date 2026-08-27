import fs from 'node:fs';

/** ¿Existe el archivo en public/? */
export const existe = (ruta) => fs.existsSync(`public${ruta}`);

/**
 * Si el archivo declarado no existe todavía, devuelve el marcador .svg
 * del mismo nombre. Así la maqueta no se rompe y se ve qué falta.
 */
export function resolverImagen(ruta) {
  if (!ruta) return null;
  if (existe(ruta)) return ruta;
  const marcador = ruta.replace(/\.[^.]+$/, '.svg');
  return existe(marcador) ? marcador : null;
}

/** Lo mismo, aplicado a todas las <img> de un bloque de HTML. */
export function sustituirFaltantes(htmlTexto) {
  return htmlTexto.replace(/src="(\/(?:wp-content|img)\/[^"]+)"/g, (todo, ruta) => {
    const r = resolverImagen(ruta);
    return r && r !== ruta ? `src="${r}"` : todo;
  });
}
