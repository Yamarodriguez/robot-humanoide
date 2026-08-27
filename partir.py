#!/usr/bin/env python3
"""Reparte las secciones de la home en paginas propias (silo).

La seccion completa pasa a su URL. En la home, en /que-es/ y en
/santa-fe/ queda la entradilla, cuatro tarjetas de muestra y un boton
a la pagina completa. Asi no hay dos URLs compitiendo por la misma
intencion de busqueda (regla 4).

Solo la home genera las paginas nuevas; las otras dos enlazan a ellas.
Los titulos de /santa-fe/ llevan la localidad pegada, por eso el
emparejamiento la ignora.
"""
import json, re, html, unicodedata
from pathlib import Path

DETALLES = {}
for grupo, fich in (('/tipos/', 'tipos-detalle.json'),
                    ('/marcas/', 'marcas-detalle.json'),
                    ('/servicios/', 'servicios-detalle.json'),
                    ('/cursos/', 'cursos-detalle.json'),
                    ('/accesorios/', 'accesorios-detalle.json')):
    f = Path('/home/claude/robothumanoide/src/data') / fich
    if f.exists():
        DETALLES[grupo] = {k for k in json.loads(f.read_text(encoding='utf-8'))
                           if not k.startswith('_')}


def destino_tarjeta(grupo, slug):
    """Pagina propia si existe; si no, ancla dentro de la pagina del grupo."""
    if slug in DETALLES.get(grupo, set()):
        return f'{grupo}{slug}/'
    return f'{grupo}#{slug}'


def ancla(texto):
    """Identificador estable a partir del titulo de la tarjeta."""
    t = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower()
    return t[:48]


def enlazar_tarjeta(t, grupo):
    """Envuelve el titulo en un enlace si la tarjeta tiene pagina propia."""
    m = re.search(r'id="([^"]+)"', t)
    if not m or m.group(1) not in DETALLES.get(grupo, set()):
        return t
    url = f'{grupo}{m.group(1)}/'
    return re.sub(r'<h3>(.*?)</h3>',
                  lambda x: f'<h3><a href="{url}">{x.group(1)}</a></h3>', t, count=1)


def poner_anclas(tarjetas):
    """Anade id a cada tarjeta para poder enlazarla desde el menu."""
    salida, vistos = [], set()
    for t in tarjetas:
        m = re.search(r'<h3>(.*?)</h3>', t, re.S)
        if not m:
            salida.append(t); continue
        base = ancla(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))))
        idt, n = base, 2
        while idt in vistos:
            idt = f'{base}-{n}'; n += 1
        vistos.add(idt)
        salida.append(t.replace('<article class="tarjeta">',
                                f'<article class="tarjeta" id="{idt}">', 1))
    return salida

BASE = Path('/home/claude/robothumanoide/src')
PAGS = BASE / 'content/pages'
META = json.loads((BASE / 'data/paginas-nuevas.json').read_text(encoding='utf-8'))
# Todas las tarjetas visibles en la home, /que-es/ y /santa-fe/.
# El boton se conserva como acceso directo a la pagina completa.
EN_MUESTRA = None


def normalizar(t):
    t = re.sub(r'\s+(en\s+)?Santa\s*Fe\b', '', t, flags=re.I)
    return re.sub(r'\s+', ' ', t).strip().lower()


META_NORM = {normalizar(k): v for k, v in META.items()}
TITULOS = json.loads((BASE / 'data/titulos-contextuales.json').read_text(encoding='utf-8'))
creadas = []
indice = {}
bloques = {}   # url -> {'orden', 'titulo', 'completo', 'muestra'}


def guardar_pagina(meta, cuerpo, entradilla):
    datos = {
        'titulo': meta['metaTitulo'], 'url': meta['url'], 'slug': meta['archivo'],
        'h1': meta['h1'], 'entradilla': entradilla, 'cta': None, 'hero': None,
        'metaTitulo': meta['metaTitulo'], 'metaDescripcion': meta['metaDescripcion'],
        'focusKeyword': '', 'imagenPrincipal': None, 'faq': [], 'html': cuerpo,
    }
    (PAGS / f'{meta["archivo"]}.json').write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')


def procesar(fichero, crear):
    ruta = PAGS / f'{fichero}.json'
    doc = json.loads(ruta.read_text(encoding='utf-8'))
    botones = {normalizar(k): v for k, v in (doc.get('botones') or {}).items()}
    salida = []

    for clase, cont in re.findall(r'<section class="([^"]*)">(.*?)</section>',
                                  doc['html'], re.S):
        m = re.search(r'<h2>(.*?)</h2>', cont, re.S)
        titulo = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        meta = META_NORM.get(normalizar(titulo))

        if not meta:
            salida.append(f'<section class="{clase}">{cont}</section>')
            continue

        parrafos = re.findall(r'<p>.*?</p>', cont, re.S)
        entradilla = re.sub(r'</?p>', '', parrafos[0]).strip() if parrafos else ''
        # Texto original del boton de Elementor; si no lo hubiera, uno neutro
        etiqueta = (botones.get(normalizar(titulo), {}).get('texto') or 'Ver más')

        # --- seccion sin rejilla: prosa e imagen, se lleva entera ---
        if 'class="rejilla' not in cont:
            if crear:
                interior = re.search(r'<div class="contenedor">(.*)</div>\s*$', cont, re.S)
                cuerpo = interior.group(1) if interior else cont
                cuerpo = re.sub(r'<h2>.*?</h2>', '', cuerpo, count=1, flags=re.S)
                bloques[meta['url']] = {
                    'orden': len(bloques), 'titulo': titulo, 'entradilla': entradilla,
                    'completo': f'<div class="contenedor">{cuerpo}</div>',
                    'muestra': (f'<div class="contenedor"><div class="prosa">'
                                f'{{H2}}{parrafos[0] if parrafos else ""}</div>'
                                f'<p class="seccion__cta"><a class="pildora" '
                                f'href="{meta["url"]}">{html.escape(etiqueta)}</a></p></div>')}
                guardar_pagina(meta,
                               f'<section class="seccion"><div class="contenedor">'
                               f'{cuerpo}</div></section>', entradilla)
                creadas.append((meta['url'], 0))
            salida.append(
                f'<section class="{clase}"><div class="contenedor"><div class="prosa">'
                f'{m.group(0) if m else ""}{parrafos[0] if parrafos else ""}</div>'
                f'<p class="seccion__cta"><a class="pildora" href="{meta["url"]}">'
                f'{html.escape(etiqueta)}</a></p></div></section>')
            continue

        # --- seccion con rejilla ---
        tarjetas = poner_anclas(
            re.findall(r'<article class="tarjeta">.*?</article>', cont, re.S))
        tarjetas = [enlazar_tarjeta(t, meta['url']) for t in tarjetas]
        if crear:
            indice[meta['url']] = [
                {'texto': html.unescape(re.sub(r'<[^>]+>', '',
                    re.search(r'<h3>(.*?)</h3>', t, re.S).group(1))).strip(),
                 'url': destino_tarjeta(meta['url'], re.search(r'id="([^"]+)"', t).group(1))}
                for t in tarjetas if '<h3>' in t]
            bloques[meta['url']] = {
                'orden': len(bloques), 'titulo': titulo, 'entradilla': entradilla,
                'completo': (f'<div class="contenedor">'
                             f'<div class="rejilla">{"".join(tarjetas)}</div></div>'),
                'muestra': (f'<div class="contenedor"><div class="prosa">{{H2}}'
                            f'{parrafos[0] if parrafos else ""}</div>'
                            f'<div class="rejilla">{"".join(tarjetas[:EN_MUESTRA])}</div>'
                            f'<p class="seccion__cta"><a class="pildora" '
                            f'href="{meta["url"]}">{html.escape(etiqueta)}</a></p></div>')}
            guardar_pagina(meta,
                           f'<section class="seccion"><div class="contenedor">'
                           f'<div class="rejilla">{"".join(tarjetas)}</div>'
                           f'</div></section>', entradilla)
            creadas.append((meta['url'], len(tarjetas)))

        antes = cont[:cont.index('<div class="rejilla')]
        salida.append(
            f'<section class="{clase}">{antes}'
            f'<div class="rejilla">{"".join(tarjetas[:EN_MUESTRA])}</div>'
            f'<p class="seccion__cta"><a class="pildora" href="{meta["url"]}">'
            f'{html.escape(etiqueta)}</a></p>'
            f'</div></section>')

    doc['html'] = '\n'.join(salida)
    ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    return doc['html'].count('<article class=')


for fich, crear in (('home', True), ('que-es', False), ('santa-fe', False)):
    print(f'  {fich:<12}{procesar(fich, crear):>3} tarjetas de muestra')


def anteponer_que_es():
    """El contenido informativo va ANTES de las rejillas de producto.
    Search Console dice que /que-es/ recibe 1.698 impresiones por consultas
    definicionales; la pagina debe abrir respondiendolas, no con un catalogo."""
    prop = json.loads((BASE / 'data/que-es.json').read_text(encoding='utf-8'))
    ruta = PAGS / 'que-es.json'
    doc = json.loads(ruta.read_text(encoding='utf-8'))

    partes = []
    for i, b in enumerate(prop['bloques']):
        fondo = ' seccion--alt' if i % 2 == 1 else ''
        cuerpo = f'<div class="prosa"><h2>{html.escape(b["h2"])}</h2>{b["html"]}</div>'
        if b.get('tabla'):
            t = b['tabla']
            filas = ''.join(
                '<tr><th scope="row">' + html.escape(f[0]) + '</th>'
                + ''.join(f'<td>{html.escape(c)}</td>' for c in f[1:]) + '</tr>'
                for f in t['filas'])
            cuerpo += ('<div class="tabla-envoltorio"><table class="tabla"><thead><tr>'
                       + ''.join(f'<th scope="col">{html.escape(c)}</th>' for c in t['cabeceras'])
                       + f'</tr></thead><tbody>{filas}</tbody></table></div>')
        if b.get('cierre'):
            cuerpo += f'<div class="prosa">{b["cierre"]}</div>'
        partes.append(f'<section class="seccion{fondo}"><div class="contenedor">{cuerpo}</div></section>')

    # Acordeon de preguntas frecuentes, con su schema
    preguntas = ''.join(
        f'<details class="pregunta"><summary>{html.escape(f["pregunta"])}</summary>'
        f'<div class="pregunta__resp"><p>{html.escape(f["respuesta"])}</p></div></details>'
        for f in prop['faq'])
    partes.append(
        '<section class="seccion"><div class="contenedor">'
        '<div class="prosa"><h2>Preguntas frecuentes sobre robots humanoides</h2></div>'
        f'<div class="acordeon">{preguntas}</div></div></section>')

    for k in ('h1', 'entradilla', 'metaTitulo', 'metaDescripcion'):
        doc[k] = prop[k]
    doc['titulo'] = prop['metaTitulo']
    doc['faq'] = prop['faq']
    doc['html'] = '\n'.join(partes) + '\n' + doc['html']
    ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    pal = len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', '\n'.join(partes))).split())
    print(f'\n  /que-es/ : {len(prop["bloques"])} bloques informativos + '
          f'{len(prop["faq"])} preguntas ({pal} palabras propias)')


anteponer_que_es()

# --- Segunda pasada: cada pagina lleva su seccion completa arriba y
#     el resto en muestra, con el H2 adaptado a su contexto ---
destinos = list(bloques.items()) + [('/contacto/', None)]

for url, propio in destinos:
    ruta = PAGS / f'{url.strip("/")}.json'
    doc = json.loads(ruta.read_text(encoding='utf-8'))
    if propio:
        # La propia página no se enlaza a sí misma
        completo = re.sub(r'<p class="seccion__cta">.*?</p>', '',
                          propio['completo'], flags=re.S)
        partes = [f'<section class="seccion">{completo}</section>']
    else:
        # /contacto/ tiene contenido propio, fuera del export de WordPress
        propio_txt = json.loads(
            (BASE / 'data/contacto.json').read_text(encoding='utf-8'))
        for k in ('entradilla', 'metaTitulo', 'metaDescripcion', 'h1'):
            if k in propio_txt:
                doc[k] = propio_txt[k]
        doc['titulo'] = propio_txt['metaTitulo']
        partes = [propio_txt['html']]
    n = 1
    for otra_url, otra in sorted(bloques.items(), key=lambda kv: kv[1]['orden']):
        if otra_url == url:
            continue
        n += 1
        titulo_ctx = TITULOS.get(url, {}).get(otra_url, otra['titulo'])
        fondo = ' seccion--alt' if n % 2 == 0 else ''
        cuerpo = otra['muestra'].replace('{H2}', f'<h2>{html.escape(titulo_ctx)}</h2>')
        partes.append(f'<section class="seccion{fondo}">{cuerpo}</section>')
    doc['html'] = '\n'.join(partes)
    ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'  {url:<14}{doc["html"].count("<section"):>2} secciones, '
          f'{doc["html"].count("<article class="):>3} tarjetas')

(BASE / 'data/indice-tarjetas.json').write_text(
    json.dumps(indice, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'\n{"URL creada":<16}{"tarjetas":>9}  anclas')
for u, n in creadas:
    print(f'  {u:<14}{n:>9}  {len(indice.get(u, []))}')
