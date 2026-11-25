# Da a las páginas de /ar/ las mismas secciones que su versión de España,
# en español rioplatense (argentino.py), sin quitar lo propio de Argentina.
# Lo llama generar_fichas_ar.py; no hace falta ejecutarlo aparte.
import json
import os
import re

from argentino import argentino, depurar
from generar_ar import RAIZ, boton, prosa, seccion

# Bloques de cada ficha, en el mismo orden que src/components/detalle/Cuerpo*.astro
CAMPOS = {
    'marcas': [('Qué es', 'queEs'), ('Qué hace', 'queHace'), ('Para quién es', 'paraQuien'), ('A tener en cuenta', 'aTenerEnCuenta')],
    'servicios': [('En qué consiste', 'enQueConsiste'), ('Cómo trabajamos', 'comoTrabajamos'), ('A tener en cuenta', 'aTenerEnCuenta')],
    'cursos': [('En qué consiste', 'enQueConsiste'), ('Qué aprendés', 'queAprendes'), ('Para quién es', 'paraQuien'), ('A tener en cuenta', 'aTenerEnCuenta')],
    'accesorios': [('Qué es', 'queEs'), ('Para qué sirve', 'paraQueSirve'), ('Cómo elegirlo', 'comoElegir'), ('A tener en cuenta', 'aTenerEnCuenta')],
}

# Fichas cuyo texto de España gira en torno a comprar dentro de la UE.
PROPIOS = {
    'neura-robotics-4ne-1': {
        'queEs': '<p>El <strong>Neura 4NE-1</strong> es un <strong>robot humanoide alemán</strong> para industria y hogar.</p><p>Neura lleva años en robótica colaborativa antes de entrar en humanoides, así que su planteo parte de la seguridad en espacios compartidos con personas.</p><h3>Características principales del Neura 4NE-1</h3><ul><li><strong>Fabricado en Alemania</strong>: desarrollo y soporte del fabricante allá.</li><li><strong>Percepción táctil</strong>: detecta contacto y reacciona.</li><li><strong>Documentación técnica</strong>: útil para tu análisis de riesgos.</li></ul>',
        'queHace': '<p>El <strong>4NE-1</strong> hace manipulación industrial y tareas domésticas con percepción táctil para trabajar junto a personas.</p><h3>Neura Robotics 4NE-1: qué hace</h3><p>Su percepción táctil le permite detectar contacto y reaccionar. Está pensado para trabajar junto a operarios, no en una celda aislada.</p>',
        'paraQuien': '<p>El <strong>Neura 4NE-1</strong> encaja en industrias que priorizan seguridad y respaldo técnico.</p><h3>Neura Robotics 4NE-1: para quién es</h3><ul><li><strong>Filiales de grupos alemanes</strong> que pueden coordinar con su casa matriz.</li><li><strong>Plantas</strong> con tareas compartidas entre robot y operario.</li></ul>',
        'aTenerEnCuenta': '<p>Con el <strong>Neura 4NE-1</strong>, la compra desde Argentina es una importación extrazona como cualquier otra.</p><h3>Neura Robotics 4NE-1: qué tener en cuenta</h3><ul><li><strong>Aduana.</strong> Sumá flete, derechos, IVA y despacho.</li><li><strong>Precio.</strong> Suele ser superior a las alternativas chinas.</li><li><strong>Soporte.</strong> Acordá por escrito quién repara y en qué plazo.</li></ul>',
    },
    'marcado-ce-y-normativa': {
        'enQueConsiste': '<p>La <strong>normativa para robots humanoides</strong> depende de qué lleva adentro el equipo y de si <strong>comparte espacio con personas</strong>.</p><p>Cubrimos el <strong>análisis de riesgos</strong>, la documentación técnica y la lista de organismos que pueden intervenir.</p><h3>Características principales de la normativa</h3><ul><li><strong>Con personas</strong>: rigen Higiene y Seguridad y la ART.</li><li><strong>Análisis de riesgos</strong>: de tu instalación concreta, no del robot en abstracto.</li><li><strong>Carpeta técnica</strong>: manuales, fichas y responsabilidades.</li></ul>',
        'comoTrabajamos': '<p>El <strong>análisis de un robot humanoide</strong> mira los riesgos de tu instalación concreta.</p><h3>Normativa para Robots: cómo trabajamos</h3><ol><li>Relevamos los riesgos de la instalación.</li><li>Definimos medidas: distancias de seguridad, paradas de emergencia, señalización.</li><li>Armamos la carpeta técnica con tu responsable de Higiene y Seguridad.</li><li>Capacitamos al personal que va a trabajar junto al robot.</li></ol>',
        'aTenerEnCuenta': '<p>Antes de dar por cumplida la <strong>normativa</strong>, recordá que integrar el robot cambia las responsabilidades.</p><h3>Normativa para Robots: qué tener en cuenta</h3><ul><li>La documentación del fabricante no alcanza: cuenta cómo lo instalás y usás.</li><li>Un accidente sin carpeta en regla tiene consecuencias que van más allá de la multa.</li><li>Resolvelo antes de instalar. Rehacer una instalación sale mucho más caro.</li></ul>',
    },
}

GRUPOS_REL = [
    ('tipos', 'Tipos de Robot Humanoides', 'Descubrí los <strong>tipos de robot humanoide</strong> que existen hoy y para qué sirve cada uno, del uso doméstico a la industria.', 'Explorá los tipos de robot humanoide'),
    ('marcas', 'Marcas y Empresas de Robots Humanoide', 'Conocé las <strong>marcas de robots humanoides</strong> líderes en inteligencia artificial y automatización, y cuáles se pueden comprar de verdad.', 'Marcas de robots humanoides destacadas'),
    ('servicios', 'Servicios Para Robots Humanoides', 'Ofrecemos <strong>servicios para robots humanoides</strong>: venta, importación, programación, mantenimiento y alquiler.', 'Nuestros servicios para robots humanoides'),
    ('cursos', 'Capacitación y Cursos en Robótica Humanoide', 'Capacitate con nuestros <strong>cursos de robótica humanoide</strong>, desde la operación básica hasta la programación con el SDK del fabricante.', 'Cursos de robótica humanoide disponibles'),
    ('accesorios', 'Accesorios y Repuestos para Robot', 'Encontrá <strong>accesorios y repuestos para robots humanoides</strong>: baterías, sensores, actuadores, cámaras, reductoras y carcasas.', 'Accesorios y repuestos para robots humanoides'),
]
quitados = []


def leer(*p):
    with open(os.path.join(RAIZ, *p), encoding='utf-8') as f:
        return json.load(f)


def adaptar(html, origen):
    h, q = depurar(argentino(html))
    quitados.extend((origen, x) for x in q)
    return h


DET = {g: leer('src', 'data', g + '-detalle.json') for g in ('tipos', 'marcas', 'servicios', 'cursos', 'accesorios')}


def bloques_ficha(f, ficha_html=''):
    """Los bloques de la ficha de España, adaptados. La tabla de marcas va
    después de «Qué es», igual que allí."""
    d = DET[f['grupo']][f['raiz']]
    propio = PROPIOS.get(f['raiz'], {})
    if f['grupo'] == 'tipos':
        n = argentino(d['h1'])
        pl = n.startswith('Robots')
        campos = [(f'Para qué se usan los {n}' if pl else f'Para qué se usa un {n}', 'paraQue'),
                  (f'Qué modelos de {n} existen', 'modelos'),
                  (f'Qué tener en cuenta antes de comprar {n}' if pl else f'Qué tener en cuenta antes de comprar un {n}', 'tenerEnCuenta')]
    else:
        campos = CAMPOS[f['grupo']]
    out = []
    for h2, k in campos:
        html = propio.get(k) or adaptar(d[k], f['raiz'])
        out.append(prosa(f'<h2>{h2}</h2>{html}'))
        if k == 'queEs' and ficha_html:
            out.append(ficha_html)
    return out


def relacionados(grupo, ar_slug, fichas, nombre):
    """Igual que Relacionados.astro: primero el grupo propio y luego el resto."""
    orden = sorted(GRUPOS_REL, key=lambda g: g[0] != grupo)
    s = []
    for i, (g, h2, desc, h3) in enumerate(orden):
        li = ''.join(f'<li><h3><a href="/ar/{x["ar"]}/">{nombre(x["h1"])}</a></h3></li>'
                     for x in fichas if x['grupo'] == g and x['ar'] != ar_slug)
        s.append(seccion(prosa(f'<h2>{h2}</h2><p>{desc}</p><h3>{h3}</h3>') + f'<ul class="lista-hermanos">{li}</ul>' +
                         boton(f'/ar/{g}/', 'Ver todos'), alt=i % 2 == 0))
    s.append(seccion(prosa('<h2>Robot Humanoide precio</h2><p>Consultá los <strong>precios de referencia</strong> de un robot humanoide por modelo y tipo antes de decidir tu compra.</p>'
                           '<h3>¿Cuánto cuesta un robot humanoide?</h3>') + boton('/ar/precios/', 'Precios'), alt=True))
    return s


def clave(t):
    return re.sub(r'\W', '', re.sub('<[^>]+>', '', t)).lower()


def sumar_paginas(destino):
    """Añade a cada página de sección lo que tiene la de España."""
    for slug in ('home', 'que-es', 'tipos', 'marcas', 'servicios', 'cursos', 'accesorios', 'comprar', 'precios', 'contacto'):
        ruta = os.path.join(destino, slug + '.json')
        with open(ruta, encoding='utf-8') as fh:
            p = json.load(fh)
        if '<!--igual-->' in p['html']:
            p['html'] = p['html'].split('<!--igual-->')[0].rstrip()
            p['faq'] = p['faq'][:p.get('faqPropias', len(p['faq']))]
        p['faqPropias'] = len(p['faq'])
        origen = re.findall(r'<section .*?</section>', leer('src', 'content', 'pages', slug + '.json')['html'], re.S)
        if slug in ('tipos', 'marcas', 'servicios', 'cursos', 'accesorios', 'contacto'):
            origen = origen[1:]          # la rejilla propia (o el formulario) ya está
        if slug == 'precios':
            d = leer('src', 'data', 'precios.json')
            origen = [f'<section class="seccion"><div class="contenedor"><div class="prosa">{d[k]}</div></div></section>'
                      for k in ('preciosServicios', 'preciosCursos', 'preciosAccesorios')] + origen
        hechos = {clave(x) for x in re.findall(r'<(?:h2|summary)[^>]*>(.*?)</(?:h2|summary)>', p['html'], re.S)}
        nuevas = []
        for s in origen:
            if 'PENDIENTE' in s:
                continue
            s = adaptar(s, slug)
            h2 = re.search(r'<h2[^>]*>(.*?)</h2>', s, re.S)
            if h2 and clave(h2[1]) in hechos:
                continue
            if h2:
                hechos.add(clave(h2[1]))
            # Preguntas que la página ya responde: no se repiten.
            for det in re.findall(r'<details.*?</details>', s, re.S):
                q = re.search(r'<summary>(.*?)</summary>.*?<div class="pregunta__resp">(.*?)</div>', det, re.S)
                resp = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', q[2])).strip()
                resp = re.sub(r' ([.,;:])', r'\1', resp)
                if clave(q[1]) in hechos or not resp:
                    s = s.replace(det, '')
                else:
                    hechos.add(clave(q[1]))
                    p['faq'].append({'pregunta': re.sub('<[^>]+>', '', q[1]).strip(), 'respuesta': resp})
            if 'class="acordeon"' in s and '<details' not in s:
                continue
            nuevas.append(s)
        p['html'] += '\n<!--igual-->\n' + '\n'.join(nuevas)
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(p, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
