# Estudio SEO y AEO de robothumanoide.org

24 de noviembre de 2026. Alcance: las 246 páginas de la rama `hreflang-ar` (España y Argentina).
No se usaron datos de Search Console ni volúmenes de búsqueda: no estaban disponibles. Las palabras clave salen de búsquedas reales y de lo que publican otros sitios.

## Diagnóstico

| Problema | Antes | Después |
|---|---|---|
| Páginas generales de España sin preguntas (FAQ) | 77 de 79 | 6 de 79 (las legales, de agradecimiento y otras sin contenido comercial) |
| Páginas generales de España sin H2 en forma de pregunta | 77 de 79 | 6 de 79 |
| Páginas con respuesta corta al inicio | 0 | 83 |
| Ciudades con un bloque que solo tienen ellas | 0 | 92 de 92 |
| Páginas de ciudad con `Service` y zona | 0 | 92 |
| Fichas de curso con `Course` | 0 | 24 |
| `llms.txt` | no | sí |

## Qué se añadió

- **186 H2** nuevos, ninguno repetido.
- **165 preguntas** con respuesta visible, también en los datos estructurados.
- **83 respuestas cortas** («En resumen») con la cifra o definición que busca el usuario.
- **Un bloque propio por ciudad**: título, situación local y pregunta diferentes.

## Palabras clave trabajadas

| Intención | Términos | Dónde |
|---|---|---|
| Precio | precio robot humanoide, robot humanoide barato, cuánto cuesta alquilar | `/`, `/precios/`, `/ar/precios/` |
| Compra | dónde comprar un robot humanoide, en España, en Argentina | `/comprar/`, `/ar/comprar/` |
| Comparación | Unitree R1 o G1, G1 y G1 EDU, humanoide o cobot, AMR o humanoide | fichas de marcas y tipos |
| Definición | qué es, partes, definición corta, grados de libertad | `/que-es/`, accesorios |
| Disponibilidad | cuándo sale Tesla Optimus, comprar 1X NEO en España | marcas |
| Formación | qué estudiar, Python o C++, sim-to-real, qué es un SDK | cursos |
| Normativa | Reglamento (UE) 2023/1230, ISO 10218, ISO 13482 | normativa y seguridad |
| Local | alquiler o uso de robot humanoide en cada ciudad | 92 ciudades |

## Google y las inteligencias artificiales

Google dice que sus funciones de IA no necesitan `llms.txt` ni marcado especial: cuenta el SEO normal, con contenido útil y visible. Por eso el esfuerzo está en respuestas y contenido; `llms.txt` es un extra opcional para otros sistemas, sin beneficio garantizado.

`robots.txt` ya permite la entrada a todos los rastreadores.

## Pendiente, por orden de impacto

1. **Sobre nosotros**: dice «PENDIENTE DE REDACTAR». Sin empresa, dirección ni responsable identificables falta la señal de confianza más importante.
2. **Pruebas propias**: fotos, vídeos, clientes o casos reales. Es lo que distingue una ciudad de otra mejor que cualquier texto.
3. **AgiBot**: se vende en España (X2 en MediaMarkt) y no tiene ficha. Es la laguna de catálogo más clara.
4. **Textos que convendría cambiar** (no se tocaron): 64 títulos superan los 62 caracteres; `/que-es/` repite dos veces sus preguntas frecuentes; el `lastmod` del sitemap es igual en todas.
5. **Ciudades pequeñas**: si Search Console las sigue mostrando como «rastreada, sin indexar», concentrar esfuerzo en 10-15.
6. **Contraste**: Argentina ya tiene importadores de Unitree con prensa; conviene comprobar precios y condiciones frente a ellos.

## Cómo medirlo

Anotar hoy en Search Console páginas indexadas, impresiones y clics, y comparar a las 4 y 8 semanas de publicar. Para IA, repetir cada mes las mismas 10 preguntas en ChatGPT, Gemini, Perplexity y Copilot, y anotar si citan el sitio.

## Dónde se edita

- `contenido-seo/paginas.txt`, `fichas.txt` y `ciudades.txt`: los añadidos.
- `python generar_refuerzo.py`: los aplica.
- Para retirar un añadido basta con borrar su bloque; el texto original no depende de él.

## Fuentes

- [Google: optimización para funciones de IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [TÜV SÜD: Reglamento de máquinas](https://www.tuvsud.com/es-es/centro-recursos/articulos-de-opinion/explicacion-nueva-regulacion-maquinas)
- [Forbes Argentina: alquiler AgiBot](https://www.forbesargentina.com/innovacion/ahora-podes-alquilar-robot-us-1000-dia-cuales-son-sus-habilidades-n87126)
- [MediaMarkt: AgiBot X2](https://www.mediamarkt.es/es/product/_robot-humanoide-agibot-x2-181100990.html)
- [La Nación: límite courier](https://www.lanacion.com.ar/economia/el-gobierno-elevo-a-us3000-el-limite-para-compras-online-en-el-exterior-por-puerta-a-puerta-nid30072026/)
- [InfoNegocios: Unitree G1 en Argentina](https://infonegocios.info/enfoque/big-dipper-lo-hace-de-nuevo-g1-el-nuevo-humanoide-de-unitree-hermano-del-robot-h1-ya-esta-en-argentina)
