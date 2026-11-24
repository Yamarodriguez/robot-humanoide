# Genera las fichas argentinas (/ar/<slug>/) a partir de contenido-ar/*.txt,
# más las páginas de sección /ar/marcas/ y /ar/accesorios/.
#
# Orden:  python generar_ar.py
#         python generar_ciudades.py
#         python generar_fichas_ar.py     <- siempre el último: además cambia
#                                            los enlaces de /ar/ a su versión /ar/
#
# Formato de los .txt:
#   @slug[>slug-ar]|H1|título meta|meta descripción
#   !precio|puesto en Argentina|¿se puede comprar?|plazo     (solo marcas)
#   ## subtítulo    - viñeta    ? pregunta    = respuesta
#   [[slug|texto]] enlaza a otra ficha; [texto](/ruta/) a cualquier página.

import glob
import json
import os
import re

from generar_ar import (DESTINO, RAIZ, boton, pagina, preguntas, prosa,
                        rejilla, seccion, tabla)

GRUPOS = {
    'tipos': ('Otros tipos de robots humanoides', '/ar/tipos/', 'Ver todos los tipos', 'Pedir asesoramiento'),
    'marcas': ('Otras marcas y modelos', '/ar/marcas/', 'Ver todas las marcas', 'Consultar por este modelo'),
    'servicios': ('Otros servicios', '/ar/servicios/', 'Ver todos los servicios', 'Pedir presupuesto'),
    'cursos': ('Otros cursos', '/ar/cursos/', 'Ver todos los cursos', 'Consultar fechas'),
    'accesorios': ('Otros accesorios y repuestos', '/ar/accesorios/', 'Ver todos los accesorios', 'Consultar disponibilidad'),
}
# Filas de la ficha técnica que solo valen comprando desde España.
FILAS_ES = {'Marcado CE', 'Aranceles', 'Edición GEEK', 'Precio por volumen', 'Canal', 'Suscripción', 'Precio anunciado'}


def leer_json(*ruta):
    with open(os.path.join(RAIZ, *ruta), encoding='utf-8') as f:
        return json.load(f)


def guardar(ruta, datos):
    with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write('\n')


def leer_fichas():
    fichas = []
    for grupo in GRUPOS:
        with open(os.path.join(RAIZ, 'contenido-ar', grupo + '.txt'), encoding='utf-8') as f:
            for trozo in re.split(r'^@', f.read(), flags=re.M)[1:]:
                cabecera, *lineas = trozo.strip().split('\n')
                slugs, h1, meta, desc = cabecera.split('|')
                raiz, _, ar = slugs.partition('>')
                fichas.append({'grupo': grupo, 'raiz': raiz, 'ar': ar or raiz, 'h1': h1,
                               'meta': meta, 'desc': desc, 'lineas': lineas})
    return fichas


def en_linea(texto):
    texto = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', texto)
    texto = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'<a href="/ar/\1/">\2</a>', texto)
    return re.sub(r'\[([^\]]+)\]\((/[^)]*)\)', r'<a href="\2">\1</a>', texto)


def sin_html(texto):
    return re.sub(r'<[^>]+>', '', texto)


def nombre_corto(h1):
    return re.sub(r' (de|en) Argentina$', '', h1)


def cuerpo(f):
    """Devuelve (entradilla, bloques por H2, faq, precio)."""
    entradilla, bloques, faq, precio, lista = '', [], [], None, []

    def volcar():
        if lista:
            bloques[-1] += '<ul>' + ''.join(f'<li>{x}</li>' for x in lista) + '</ul>'
            lista.clear()

    for l in filter(None, (x.strip() for x in f['lineas'])):
        if l.startswith('!precio|'):
            precio = l.split('|')[1:]
        elif l.startswith('## '):
            volcar() if bloques else None
            bloques.append(f'<h2>{l[3:]}</h2>')
        elif l.startswith('- '):
            lista.append(en_linea(l[2:]))
        elif l.startswith('? '):
            faq.append([l[2:], ''])
        elif l.startswith('= '):
            faq[-1][1] = en_linea(l[2:])
        elif not bloques:
            entradilla += (' ' if entradilla else '') + en_linea(l)
        else:
            volcar()
            bloques[-1] += f'<p>{en_linea(l)}</p>'
    if bloques:
        volcar()
    return entradilla, bloques, faq, precio


def tarjetas_raiz():
    """slug -> (imagen, ancho, alto) sacado de las tarjetas de la raíz."""
    res = {}
    for grupo in GRUPOS:
        html = leer_json('src', 'content', 'pages', grupo + '.json')['html']
        for slug, art in re.findall(r'<article class="tarjeta" id="([^"]+)">(.*?)</article>', html, re.S):
            img = re.search(r'<img[^>]*>', art)
            if img:
                a = dict(re.findall(r'(\w+)="([^"]*)"', img[0]))
                res[slug] = (a['src'], int(a.get('width', 800)), int(a.get('height', 600)))
    return res


def ficha_tecnica(f, precio, marcas):
    if not precio:
        return ''
    d = marcas[f['raiz']]
    filas = [['Precio en origen', d['precio']['fabrica'].split(' (unos')[0].split(', unos')[0]], ['Puesto en Argentina', precio[0]],
             ['¿Se puede comprar?', precio[1]], ['Plazo', precio[2]]]
    filas += [x for x in (d.get('ficha') or []) if x[0] not in FILAS_ES]
    nombre = nombre_corto(f['h1'])
    filas[0][1] = filas[0][1].replace('$', 'USD').replace('€', 'USD')
    return seccion(prosa(f'<h2>{nombre}: ficha y precio en Argentina</h2>') +
                   tabla(['Dato', 'Detalle'], filas, 'Valores orientativos en dólares. Se confirman al cotizar.'), alt=True)


def relink(html, mapa):
    return re.sub(r'href="(/[a-z0-9-]+/)(?=["#])',
                  lambda m: f'href="{mapa.get(m[1], m[1])}', html)


def portada_seccion(slug, h1, meta, desc, entradilla, intro, fichas, resumen, faq, imgs, cierre, hero):
    items = []
    for f in fichas:
        src, w, h = imgs.get(f['raiz'], (None, 0, 0))
        if src:
            items.append((f'/ar/{f["ar"]}/', src, (w, h), nombre_corto(f['h1']), resumen(f)))
    s = [seccion(prosa(intro) + rejilla(items)), seccion(prosa(cierre) + boton('/ar/contacto/', 'Pedir asesoramiento'), alt=True),
         preguntas('Preguntas frecuentes', faq)]
    return pagina(slug, f'/{slug}/', h1, h1, meta, desc, entradilla, s, faq, hero=hero, focus=h1.lower())


def main():
    fichas = leer_fichas()
    marcas = leer_json('src', 'data', 'marcas-detalle.json')
    imgs = tarjetas_raiz()
    partes = {f['ar']: cuerpo(f) for f in fichas}
    secciones = ['que-es', 'tipos', 'precios', 'comprar', 'servicios', 'cursos', 'contacto', 'marcas', 'accesorios']
    mapa = {f'/{s}/': f'/ar/{s}/' for s in secciones}
    mapa.update({f'/{f["raiz"]}/': f'/ar/{f["ar"]}/' for f in fichas})

    for f in fichas:
        entradilla, bloques, faq, precio = partes[f['ar']]
        titulo_h, url_h, texto_h, cta = GRUPOS[f['grupo']]
        s = [seccion(prosa(b), alt=i % 2 == 1) for i, b in enumerate(bloques)]
        if precio:
            s.insert(0, ficha_tecnica(f, precio, marcas))
        s.append(preguntas(f'Preguntas sobre {nombre_corto(f["h1"])} en Argentina', faq))
        hermanos = [x for x in fichas if x['grupo'] == f['grupo'] and x is not f]
        # Cuatro vecinas de la lista, distintas en cada ficha.
        todas = [x for x in fichas if x['grupo'] == f['grupo']]
        i = todas.index(f)
        vecinas = [todas[(i + k) % len(todas)] for k in range(1, min(5, len(hermanos) + 1))]
        s.append(seccion(prosa(f'<h2>{titulo_h}</h2>') + '<ul class="lista-hermanos">' + ''.join(
            f'<li><h3><a href="/ar/{x["ar"]}/">{nombre_corto(x["h1"])}</a></h3></li>' for x in vecinas) +
            '</ul>' + boton(url_h, texto_h), alt=True))
        hero = imgs.get(f['raiz'], (None,))[0]
        p = pagina(f['ar'], f'/{f["raiz"]}/', f['h1'], f['h1'], f['meta'], f['desc'], entradilla, s,
                   [(q, sin_html(r)) for q, r in faq], hero=hero,
                   cta={'url': '/ar/contacto/', 'texto': cta}, focus=f['h1'].lower())
        guardar(os.path.join(DESTINO, f['ar'] + '.json'), p)

    de = lambda g: [f for f in fichas if f['grupo'] == g]
    guardar(os.path.join(DESTINO, 'marcas.json'), portada_seccion(
        'marcas', 'Marcas de Robots Humanoides en Argentina',
        'Marcas de Robots Humanoides en Argentina - Cuáles se Pueden Comprar',
        'Marcas de robots humanoides vistas desde Argentina: cuáles se importan, cuáles no se venden y cuánto cuestan puestas en el país.',
        'Cuáles se pueden traer a Argentina, cuáles no se venden en ningún lado y cuánto cuestan <strong>puestas en el país</strong>.',
        '<h2>Qué marcas se consiguen y cuáles solo se ven en videos</h2><p>De las marcas y modelos de esta guía, una minoría admite una compra desde Argentina. '
        'En cada ficha decimos primero si se puede traer y después qué hace.</p>',
        de('marcas'), lambda f: f'Puesto en Argentina: {partes[f["ar"]][3][0]}. ¿Se puede comprar? {partes[f["ar"]][3][1]}.',
        [('¿Qué marca conviene para empezar en Argentina?', 'Para aprender o mostrar, Unitree R1. Para desarrollar, Unitree G1 en versión EDU o Booster K1. Para escuelas, la línea educativa de UBTech.'),
         ('¿Hay marcas argentinas de humanoides?', 'No tenemos verificado ningún fabricante local de humanoides comerciales. Sí hay grupos universitarios que desarrollan prototipos.'),
         ('¿Hay representantes oficiales?', 'Cambian según la marca y el momento. Antes de pagar, confirmá en la web del fabricante que el vendedor figure como autorizado.')],
        imgs,
        '<h2>Cómo comparar marcas comprando desde acá</h2><ul><li><strong>Costo puesto en el país</strong>, no precio de fábrica.</li>'
        '<li><strong>Versión</strong>: con o sin acceso de desarrollo.</li><li><strong>Repuestos</strong> y plazo para que lleguen.</li>'
        '<li><strong>Idioma y servidores</strong>: que la aplicación funcione fuera de su mercado.</li></ul>',
        '/img/heroes/marcas-de-robots-humanoides.webp'))

    guardar(os.path.join(DESTINO, 'accesorios.json'), portada_seccion(
        'accesorios', 'Accesorios y Repuestos para Robots Humanoides en Argentina',
        'Accesorios y Repuestos para Robots Humanoides en Argentina',
        'Accesorios y repuestos para robots humanoides en Argentina: qué se consigue o fabrica en el país, qué se importa y qué tener en stock.',
        'Qué se consigue o se fabrica en el país, qué hay que importar y qué repuestos conviene <strong>tener en stock</strong>.',
        '<h2>Repuestos: lo local, lo importado y lo urgente</h2><p>Un robot parado por un repuesto que está en aduana es la situación más común en Argentina. '
        'Se evita pidiendo lo crítico junto con el equipo y resolviendo acá lo que se puede.</p>',
        de('accesorios'), lambda f: f['desc'],
        [('¿Los repuestos entran por courier?', 'Muchos sí, por valor y tamaño. Las baterías de litio grandes son la excepción habitual.'),
         ('¿Qué repuestos pido junto con el robot?', 'Como mínimo una batería, un actuador de rodilla, uno de tobillo, cables y cubiertas de manos.'),
         ('¿Sirven los genéricos?', 'En carcasas, soportes y cables, a veces. En encoders, baterías y actuadores conviene el original.')],
        imgs,
        '<h2>Lista de compra para el primer año</h2><ul><li><strong>Con el robot</strong>: batería extra, actuadores y cargador adicional.</li>'
        '<li><strong>En el país</strong>: soporte o arnés, protección eléctrica, herramientas y cubiertas impresas.</li>'
        '<li><strong>Según la tarea</strong>: manos, cámara o LiDAR adicional.</li></ul>',
        '/img/heroes/accesorios-y-repuestos-robot-humanoide.webp'))

    # Enlaces: todo lo que se ve en /ar/ apunta a su versión /ar/ si existe.
    for ruta in glob.glob(os.path.join(DESTINO, '*.json')):
        with open(ruta, encoding='utf-8') as fh:
            p = json.load(fh)
        p['html'] = relink(p['html'], mapa)
        guardar(ruta, p)

    # Menú de /ar/
    ruta_site = os.path.join(RAIZ, 'src', 'data', 'site.json')
    site = leer_json('src', 'data', 'site.json')
    nombres = {f'/ar/{f["ar"]}/': nombre_corto(f['h1']) for f in fichas}

    def recorrer(nodos):
        for n in nodos:
            if 'url' in n:
                n['url'] = mapa.get(n['url'], n['url'])
                n['texto'] = nombres.get(n['url'], n['texto'])
            recorrer(n.get('hijos', []))

    recorrer(site['navegacionAR'])
    # "Sobre nosotros" sigue pendiente de redactar (noindex): fuera del menú.
    site['navegacionAR'] = [n for n in site['navegacionAR'] if n.get('url') != '/sobre-nosotros/']
    site['_comentario_navegacionAR'] = 'Menú de las páginas /ar/ (versión Argentina). Las fichas enlazan a su versión /ar/ (generar_fichas_ar.py).'
    guardar(ruta_site, site)
    print(len(fichas), 'fichas y 2 secciones')


if __name__ == '__main__':
    main()
