import site from '../data/site.json';

/* Versión argentina del sitio: vive en /ar/ y cada página puede declarar
   en su JSON "alterna" con la URL de su equivalente en la raíz. Con eso se
   generan los hreflang en las dos direcciones sin mantener otra lista. */

const modulosAR = import.meta.glob('../content/pages/ar/*.json', { eager: true });
export const paginasAR = Object.values(modulosAR).map((m) => m.default ?? m);

// URL de la raíz -> URL argentina equivalente.
const deRaizAAR = Object.fromEntries(
  paginasAR.filter((p) => p.alterna).map((p) => [p.alterna, p.url])
);

export const esAR = (url) => url === '/ar/' || url.startsWith('/ar/');

/** Equivalente de una URL en la otra versión, o null si no existe. */
export function equivalente(url) {
  if (esAR(url)) return paginasAR.find((p) => p.url === url)?.alterna ?? null;
  return deRaizAAR[url] ?? null;
}

/**
 * Enlaces hreflang de una página. La raíz se marca como "es" (español
 * general, también para el resto de Latinoamérica) y /ar/ como "es-AR".
 * Solo se emiten cuando existe la pareja: un hreflang sin vuelta se ignora.
 */
export function alternas(url) {
  const otra = equivalente(url);
  if (!otra) return [];
  const raiz = esAR(url) ? otra : url;
  const ar = esAR(url) ? url : otra;
  return [
    { hreflang: 'es', href: site.dominio + raiz },
    { hreflang: 'es-AR', href: site.dominio + ar },
    { hreflang: 'x-default', href: site.dominio + raiz },
  ];
}
