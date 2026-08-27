# robothumanoide.org — proyecto Astro

Migración de WordPress a sitio estático. 80 páginas, sin JavaScript.

---

## Desplegar en Netlify desde GitHub

### 1. Crear el repositorio

En GitHub, repositorio nuevo **privado**, sin README ni .gitignore
(el proyecto ya trae el suyo).

### 2. Subirlo

Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Migración de WordPress a Astro"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/robothumanoide.git
git push -u origin main
```

### 3. Conectarlo a Netlify

En Netlify: **Add new site → Import an existing project → GitHub**,
y elige el repositorio.

Netlify lee `netlify.toml` y configura sola la build. **No cambies nada
en el panel:** si el formulario de Netlify muestra otro comando o
carpeta, déjalo en blanco y deja que mande el archivo.

Al terminar te da una URL tipo `nombre-aleatorio.netlify.app`.

---

## Antes de apuntar el dominio

**1. Poner la access key del formulario.**
En `src/data/site.json`, sustituir `PENDIENTE-PEGAR-ACCESS-KEY` por la
clave de [web3forms.com](https://web3forms.com). Sin eso el formulario
no envía nada.

**2. Bloquear la URL temporal.**
`nombre.netlify.app` se indexa sola y crea un duplicado de todo el sitio
mientras WordPress sigue vivo. En Netlify, **Site settings → Build &
deploy → Post processing**, activar la opción que bloquea la indexación
de los despliegues de previsualización.

**3. Comprobar en la URL temporal:**

- Las 80 páginas cargan y el menú funciona
- El formulario envía y redirige a `/gracias/`
- `/sitemap.xml` lista 75 URLs
- `/robots.txt` responde
- Una URL inventada da el 404 propio
- `/sitemap_index.xml` redirige a `/sitemap.xml`

**4. Rellenar los datos pendientes** (ver más abajo).

**5. Solo entonces**, apuntar el dominio: en Netlify, **Domain settings
→ Add custom domain**. WordPress se queda encendido hasta confirmar que
todo responde en el dominio real.

---

## Qué falta rellenar

| Dónde | Qué |
|---|---|
| `src/data/site.json` | Access key de Web3Forms |
| `src/data/site.json` | Etiquetas de verificación de Google y Bing |
| `src/data/contacto.json` | Teléfono, dirección y horario |
| `src/data/legales.json` | Datos fiscales en las tres páginas legales |
| `src/content/pages/sobre-nosotros.json` | Contenido de la página |

Las páginas legales y `/sobre-nosotros/` están en `noindex` hasta que se
completen. Se quita borrando `"noindex": true` de su archivo.

---

## Estructura

```
src/
  data/          contenido que se edita a mano
  content/pages/ contenido generado desde el export de WordPress
  pages/         rutas
  layouts/       plantilla base
  components/    cabecera, pie, formulario, migas, relacionados
  styles/        sistema de diseño en variables CSS
public/
  wp-content/uploads/  imágenes migradas, con su ruta original
  img/                 imágenes nuevas
  _redirects           redirecciones de los sitemaps de Yoast
  robots.txt
```

**Importante:** las rutas bajo `/wp-content/uploads/` no se renombran
nunca. Están indexadas en Google Imágenes desde marzo de 2025.

---

## Editar contenido

Casi todo se cambia en `src/data/`, sin tocar código:

- `ampliaciones.json` — las 37 tarjetas añadidas
- `precios.json` — tabla de precios **(caduca rápido: revisar cada 3 meses)**
- `marcas-detalle.json`, `tipos-detalle.json`, `servicios-detalle.json`,
  `cursos-detalle.json`, `accesorios-detalle.json` — páginas de detalle
- `heroes.json` — imagen principal de cada página
- `site.json` — menú, pie, formulario

Después de editar:

```bash
npm install     # solo la primera vez
npm run dev     # ver en local, http://localhost:4321
npm run build   # comprobar que compila
```

Al hacer `git push`, Netlify reconstruye sola.

---

## Regenerar desde WordPress

Solo si vuelves a exportar el XML. Los dos scripts van **siempre en este
orden**, porque no son idempotentes:

```bash
python3 extraer.py    # XML de WordPress -> src/content/pages/*.json
python3 partir.py     # reparte secciones en el silo de páginas
```

Ejecutar `partir.py` dos veces seguidas sin `extraer.py` delante duplica
el contenido.

---

## Imágenes pendientes

Diez son ilustraciones vectoriales generadas, no fotografías. Se
sustituyen dejando la foto real **con el mismo nombre de archivo**:

- `robot-para-el-hogar.jpeg`, `robot-educativo.jpeg`,
  `cursos-robotica-humanoide.jpeg` (1280×1280)
- Los seis heroes de `public/img/heroes/` (1792×1024)

Si la nueva imagen es `.webp` y creas una variante `-896.webp` al lado,
se sirve sola en móviles.
