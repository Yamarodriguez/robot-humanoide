#!/usr/bin/env python3
"""Extrae el export WXR a colecciones JSON reconstruyendo la estructura visual.

Limpieza:
  - Elimina <article> y atributos de la interfaz de ChatGPT
  - URLs absolutas -> rutas relativas
  - loading=lazy / decoding=async en imagenes

Reconstruccion (lo que Elementor pintaba y el HTML plano perdia):
  - Rachas de [figure + titulo + p] -> rejilla de tarjetas
  - Titulos de tarjeta h2 -> h3 (jerarquia coherente)
  - Bloque de preguntas -> acordeon <details> nativo, sin JS
  - Hero separado del cuerpo
"""
import json, re, html
from pathlib import Path
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'wp': 'http://wordpress.org/export/1.2/',
      'content': 'http://purl.org/rss/1.0/modules/content/'}
SRC = '/mnt/user-data/uploads/robothumanoide_WordPress_2026-08-22.xml'
OUT = Path('/home/claude/robothumanoide/src/content/pages')
OUT.mkdir(parents=True, exist_ok=True)

# El hero de Elementor era un fondo, no vive en content:encoded.
HERO = {
    'robot-humanoide': '/wp-content/uploads/2025/03/robot-humanoide.webp',
    'que-es':          '/wp-content/uploads/2025/03/que-es-un-robot-humanoide.webp',
    'santa-fe':        '/wp-content/uploads/2026/01/robot-humanoide-santa-fe.webp',
    'contacto':        None,
}
DESTINO = {
    'robot-humanoide': ('home', '/'),
    'que-es':          ('que-es', '/que-es/'),
    'santa-fe':        ('santa-fe', '/santa-fe/'),
    'contacto':        ('contacto', '/contacto/'),
}


def mapa_elementor(item):
    """Elementor guarda las imagenes de seccion como fondo de columna y los
    botones como widgets. Nada de eso llega a content:encoded."""
    import json as _json
    crudo = None
    for pm in item.findall('wp:postmeta', NS):
        if pm.findtext('wp:meta_key', namespaces=NS) == '_elementor_data':
            crudo = pm.findtext('wp:meta_value', namespaces=NS)
    if not crudo:
        return []
    try:
        arbol = _json.loads(crudo)
    except Exception:
        return []

    plano = []

    def recorrer(nodos):
        for n in nodos:
            st = n.get('settings', {}) or {}
            if n.get('elType') == 'widget':
                w = n.get('widgetType')
                if w == 'heading':
                    t = html.unescape(re.sub(r'<[^>]+>', '', str(st.get('title', '')))).strip()
                    if t:
                        plano.append(('h', t))
                elif w == 'button':
                    enlace = (st.get('link') or {}).get('url', '')
                    texto = str(st.get('text', '')).strip()
                    if texto:
                        plano.append(('btn', {
                            'texto': texto,
                            'url': re.sub(r'https?://robothumanoide\.org', '', enlace)}))
                elif w == 'image':
                    u = (st.get('image') or {}).get('url', '')
                    if u:
                        plano.append(('img', re.sub(r'https?://robothumanoide\.org', '', u)))
            for clave in ('background_image', 'background_overlay_image'):
                u = (st.get(clave) or {}).get('url', '')
                if u:
                    plano.append(('img', re.sub(r'https?://robothumanoide\.org', '', u)))
            recorrer(n.get('elements', []) or [])

    recorrer(arbol)

    return plano


def emparejar(plano, titulos_seccion):
    """Asocia cada imagen y cada boton al H2 de seccion que los precede.
    En Elementor el fondo suele ir tras un subtitulo, asi que hay que
    remontar hasta el titular que realmente abre la seccion."""
    validos = {t.strip() for t in titulos_seccion}
    imagenes, botones, actual = {}, {}, None
    for tipo, valor in plano:
        if tipo == 'h':
            if valor.strip() in validos:
                actual = valor.strip()
        elif tipo == 'img' and actual and actual not in imagenes:
            imagenes[actual] = valor
        elif tipo == 'btn' and actual and actual not in botones:
            botones[actual] = valor
    return imagenes, botones


def limpiar(h):
    h = re.sub(r'</?article\b[^>]*>', '', h)
    h = re.sub(r'\s+data-(?:start|end|testid|scroll-anchor)="[^"]*"', '', h)
    h = re.sub(r'\s+(?:tabindex="-1"|dir="auto")', '', h)
    h = re.sub(r'https?://robothumanoide\.org', '', h)
    h = re.sub(r'[ \t]*\n[ \t]*', '\n', h)
    h = re.sub(r'\n{3,}', '\n\n', h)
    h = re.sub(r'[ \t]{2,}', ' ', h)
    h = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy" decoding="async"', h)
    return h.strip()


def trocear(h):
    """Divide el HTML en bloques de primer nivel conservando el orden."""
    patron = re.compile(r'<(h2|h3|figure|p|ul|a)\b[^>]*>.*?</\1>', re.S | re.I)
    bloques, pos = [], 0
    for m in patron.finditer(h):
        if m.start() > pos and h[pos:m.start()].strip():
            bloques.append(('otro', h[pos:m.start()].strip()))
        bloques.append((m.group(1).lower(), m.group(0)))
        pos = m.end()
    if h[pos:].strip():
        bloques.append(('otro', h[pos:].strip()))
    return bloques


def _a_h3(fragmento):
    return fragmento.replace('<h2>', '<h3>').replace('</h2>', '</h3>')


def reconstruir(bloques):
    """Agrupa rachas figure+titulo+p en rejillas y preguntas en acordeon."""
    salida, i = [], 0
    while i < len(bloques):
        # --- rejilla de tarjetas ---
        tarjetas, j = [], i
        while (j + 2 < len(bloques)
               and bloques[j][0] == 'figure'
               and bloques[j + 1][0] in ('h2', 'h3')
               and bloques[j + 2][0] == 'p'):
            tarjetas.append(
                f'<article class="tarjeta">{bloques[j][1]}'
                f'<div class="tarjeta__texto">{_a_h3(bloques[j + 1][1])}'
                f'{bloques[j + 2][1]}</div></article>')
            j += 3
        if len(tarjetas) >= 2:
            salida.append(('rejilla', f'<div class="rejilla">{"".join(tarjetas)}</div>'))
            i = j
            continue

        # --- acordeon de preguntas ---
        preguntas, j = [], i
        while j + 1 < len(bloques) and bloques[j][0] == 'h3':
            texto = re.sub(r'<[^>]+>', '', bloques[j][1]).strip()
            if not texto.endswith('?'):
                break
            cuerpo, k = [], j + 1
            while k < len(bloques) and bloques[k][0] in ('p', 'ul'):
                cuerpo.append(bloques[k][1])
                k += 1
            if not cuerpo:
                break
            preguntas.append(
                f'<details class="pregunta"><summary>{html.escape(texto)}</summary>'
                f'<div class="pregunta__resp">{"".join(cuerpo)}</div></details>')
            j = k
        if len(preguntas) >= 3:
            salida.append(('acordeon', f'<div class="acordeon">{"".join(preguntas)}</div>'))
            i = j
            continue

        salida.append(bloques[i])
        i += 1
    return salida


def _fusionar(bloques):
    salida, acum = [], []
    for tipo, cont in bloques:
        if tipo in ('rejilla', 'acordeon'):
            if acum:
                salida.append(('prosa', ''.join(acum)))
                acum = []
            salida.append((tipo, cont))
        else:
            acum.append(cont)
    if acum:
        salida.append(('prosa', ''.join(acum)))
    return salida


def normalizar(t):
    """Quita marcas de localizacion para que /santa-fe/ case con la home."""
    t = re.sub(r'\s+(en\s+)?Santa\s*Fe\b', '', t, flags=re.I)
    return re.sub(r'\s+', ' ', t).strip().lower()


DESTINOS_NORM = None


def normalizar_titulo(t):
    """Clave comun para home y /santa-fe/, que lleva la localidad pegada."""
    global DESTINOS_NORM
    if DESTINOS_NORM is None:
        DESTINOS_NORM = {normalizar(k): v for k, v in DESTINOS.items()}
    return normalizar(t)


def buscar_ampliacion(titulo):
    clave = normalizar(titulo)
    for k, v in AMPL.items():
        if not k.startswith('_') and normalizar(k) == clave:
            return v
    return []


def envolver_secciones(bloques, imagenes=None, botones=None):
    """Cada h2 abre seccion. Si Elementor tenia imagen de fondo para ese
    titulo, la seccion se monta a dos columnas alternando el lado."""
    imagenes = imagenes or {}
    botones = botones or {}
    partes, buffer, n, duos = [], [], 0, 0

    def cerrar():
        nonlocal buffer, n, duos
        if not buffer:
            return
        n += 1
        fondo = ' seccion--alt' if n % 2 == 0 else ''

        titulo = ''
        if buffer and buffer[0][0] == 'h2':
            titulo = html.unescape(re.sub(r'<[^>]+>', '', buffer[0][1])).strip()
        img = imagenes.get(titulo)
        btn = botones.get(titulo)
        hay_rejilla = any(t in ('rejilla', 'acordeon') for t, _ in buffer)

        extras = buscar_ampliacion(titulo) if titulo else []
        nuevas = ''.join(
            f'<article class="tarjeta"><figure>'
            f'<img src="{e["imagen"]}" alt="{html.escape(e["titulo"])}" '
            f'width="800" height="600" loading="lazy" decoding="async"></figure>'
            f'<div class="tarjeta__texto"><h3>{html.escape(e["titulo"])}</h3>'
            f'<p>{e["texto"]}</p></div></article>'
            for e in extras) if extras else ''

        # Si la seccion ya tiene rejilla, las nuevas se anaden al final de esa
        if nuevas and hay_rejilla:
            buffer = [(t, c[:c.rfind('</div>')] + nuevas + '</div>') if t == 'rejilla'
                      else (t, c) for t, c in buffer]

        cuerpo = ''.join(
            c if t in ('rejilla', 'acordeon') else f'<div class="prosa">{c}</div>'
            for t, c in _fusionar(buffer))

        if btn and btn.get('url'):
            cuerpo += (f'<p class="seccion__cta">'
                       f'<a class="pildora" href="{btn["url"]}">{html.escape(btn["texto"])}</a></p>')

        # Dos columnas solo si hay imagen y la seccion es de prosa
        if img and not hay_rejilla:
            duos += 1
            lado = ' duo--invertido' if duos % 2 == 0 else ''
            cuerpo = (f'<div class="duo{lado}"><div class="duo__texto">{cuerpo}</div>'
                      f'<figure class="duo__figura">'
                      f'<img src="{img}" alt="{html.escape(titulo)}" '
                      f'width="1024" height="768" loading="lazy" decoding="async"></figure></div>')

        # Si no habia rejilla, la cuadricula nueva va debajo, a todo el ancho
        if nuevas and not hay_rejilla:
            # El CTA va al final del todo, detras de la cuadricula nueva
            cta = ''
            m_cta = re.search(r'<p class="seccion__cta">.*?</p>', cuerpo, re.S)
            if m_cta:
                cta = m_cta.group(0)
                cuerpo = cuerpo.replace(cta, '', 1)
            cuerpo += f'<div class="rejilla rejilla--anadida">{nuevas}</div>{cta}'

        partes.append(f'<section class="seccion{fondo}">'
                      f'<div class="contenedor">{cuerpo}</div></section>')
        buffer = []

    for tipo, cont in bloques:
        if tipo == 'h2':
            cerrar()
        buffer.append((tipo, cont))
    cerrar()
    return '\n'.join(partes)


def extraer_faq(bloques):
    faqs = []
    for tipo, cont in bloques:
        if tipo != 'acordeon':
            continue
        for m in re.finditer(
                r'<summary>(.*?)</summary>\s*<div[^>]*>(.*?)</details>', cont, re.S):
            p = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
            r = html.unescape(re.sub(r'\s+', ' ',
                                     re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
            if p and len(r) > 40:
                faqs.append({'pregunta': p, 'respuesta': r})
    return faqs


_D = Path('/home/claude/robothumanoide/src/data')
AMPL = json.loads((_D / 'ampliaciones.json').read_text(encoding='utf-8'))
DESTINOS = {k: v for k, v in
            json.loads((_D / 'destinos-botones.json').read_text(encoding='utf-8')).items()
            if not k.startswith('_')}

ch = ET.parse(SRC).getroot().find('channel')
resumen = []

for item in ch.findall('item'):
    if item.findtext('wp:post_type', namespaces=NS) != 'page':
        continue
    slug = item.findtext('wp:post_name', namespaces=NS)
    if slug not in DESTINO:
        continue
    fichero, url = DESTINO[slug]

    meta = {pm.findtext('wp:meta_key', namespaces=NS):
            pm.findtext('wp:meta_value', namespaces=NS) or ''
            for pm in item.findall('wp:postmeta', NS)
            if (pm.findtext('wp:meta_key', namespaces=NS) or '').startswith('_yoast')}

    crudo = limpiar(item.findtext('content:encoded', namespaces=NS) or '')

    h1 = ''
    m = re.search(r'<h1>(.*?)</h1>', crudo, re.S)
    if m:
        h1 = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
        crudo = crudo.replace(m.group(0), '', 1).lstrip()
    crudo = re.sub(r'<h2>\s*Contacto\s*</h2>', '', crudo, flags=re.I)

    plano = mapa_elementor(item)
    bloques = reconstruir(trocear(crudo))
    titulos = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
               for t, c in bloques if t == 'h2']
    imagenes, botones = emparejar(plano, titulos)
    for clave, btn in botones.items():
        if not btn.get('url'):
            normalizar_titulo(clave)
            btn['url'] = DESTINOS_NORM.get(normalizar(clave), '')

    entradilla, cta = '', None
    if bloques and bloques[0][0] == 'p':
        entradilla = re.sub(r'</?p>', '', bloques.pop(0)[1]).strip()
    if bloques and bloques[0][0] == 'a':
        m = re.match(r'<a href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', bloques[0][1], re.S)
        if m:
            cta = {'url': m.group(1), 'texto': re.sub(r'\s+', ' ', m.group(2)).strip()}
            bloques.pop(0)

    datos = {
        'titulo': item.findtext('title'),
        'url': url,
        'slug': slug,
        'h1': h1,
        'entradilla': entradilla,
        'cta': cta,
        'hero': HERO[slug],
        'metaTitulo': meta.get('_yoast_wpseo_title', ''),
        'metaDescripcion': meta.get('_yoast_wpseo_metadesc', ''),
        'focusKeyword': meta.get('_yoast_wpseo_focuskw', ''),
        'imagenPrincipal': HERO[slug],
        'faq': extraer_faq(bloques),
        'botones': botones,
        'html': envolver_secciones(bloques, imagenes, botones),
    }
    (OUT / f'{fichero}.json').write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    resumen.append((fichero, datos['html'].count('class="rejilla"'),
                    datos['html'].count('class="tarjeta"'),
                    datos['html'].count('<details'), len(datos['faq']),
                    datos['html'].count('class="duo')))

print(f'{"pagina":<11}{"rejillas":>10}{"tarjetas":>10}{"details":>9}{"faq":>5}{"duos":>7}')
for r in resumen:
    print(f'{r[0]:<11}{r[1]:>10}{r[2]:>10}{r[3]:>9}{r[4]:>5}{r[5]:>7}')

print('\nComprobaciones:')
for f in OUT.glob('*.json'):
    d = json.loads(f.read_text(encoding='utf-8'))
    for mal, msg in [('data-start', 'data-start'), ('robothumanoide.org', 'URL absoluta'),
                     ('<h1', 'H1 en el cuerpo'), ('conversation-turn', 'markup ChatGPT')]:
        assert mal not in d['html'], f'{f.name}: {msg}'
print('  OK - limpio, sin H1 duplicado, sin URLs absolutas')
