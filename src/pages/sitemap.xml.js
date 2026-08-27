import site from '../data/site.json';
import detalleTipos from '../data/tipos-detalle.json';
import detalleMarcas from '../data/marcas-detalle.json';
import detalleServicios from '../data/servicios-detalle.json';
import detalleCursos from '../data/cursos-detalle.json';
import detalleAccesorios from '../data/accesorios-detalle.json';

const modulos = import.meta.glob('../content/pages/*.json', { eager: true });

const paginas = Object.values(modulos)
  .map((m) => m.default ?? m)
  .filter((p) => p.url && !p.noindex)
  .map((p) => p.url);

// Las páginas de detalle se generan por ruta dinámica en la raíz (/{slug}/):
// no están en content/pages, así que hay que añadirlas explícitamente.
const detalles = [
  detalleTipos, detalleMarcas, detalleServicios, detalleCursos, detalleAccesorios,
].flatMap((datos) =>
  Object.keys(datos).filter((k) => !k.startsWith('_')).map((slug) => `/${slug}/`)
);

const urls = [...new Set([...paginas, ...detalles])].sort();

export function GET() {
  const hoy = new Date().toISOString().split('T')[0];
  const cuerpo = urls.map((u) => `  <url>
    <loc>${site.dominio}${u}</loc>
    <lastmod>${hoy}</lastmod>
  </url>`).join('\n');

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${cuerpo}
</urlset>`,
    { headers: { 'Content-Type': 'application/xml; charset=utf-8' } }
  );
}
