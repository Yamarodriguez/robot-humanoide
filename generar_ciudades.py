# Genera las páginas de ciudad (src/content/pages/<slug>.json) a partir de
# los datos propios de cada ciudad en src/data/ciudades.json.
#
# Cada página se construye con secciones y preguntas frecuentes escritas a
# partir de los sectores, centros de formación, accesos y recintos de esa
# ciudad, de modo que ninguna sea una copia de otra (Google descartaba las
# páginas clonadas y solo mostraba Santa Fe).
#
# Uso:  python generar_ciudades.py
# Toca solo los ficheros de ciudades presentes en ciudades.json (España, en
# la raíz) y ciudades-ar.json (Argentina, en /ar/). Después, ejecutar
# generar_fichas_ar.py para que los enlaces de /ar/ apunten a /ar/.

import hashlib
import json
import os

RAIZ = os.path.dirname(os.path.abspath(__file__))
PAGINAS = os.path.join(RAIZ, 'src', 'content', 'pages')
DATOS = os.path.join(RAIZ, 'src', 'data')


def leer(nombre):
    with open(os.path.join(DATOS, nombre), encoding='utf-8') as f:
        return json.load(f)


ciudades = leer('ciudades.json')
ciudades_ar = leer('ciudades-ar.json')
tipos = leer('tipos-detalle.json')
cursos = leer('cursos-detalle.json')

# Imagen de tarjeta de cada tipo (las mismas que usa el índice de tipos).
IMG_TIPO = {
    'robot-industrial': '/wp-content/uploads/2025/03/robot-humanoide-industrial.jpg',
    'robot-de-compania': '/wp-content/uploads/2025/03/robot-humanoide-de-compania.jpeg',
    'robots-medicos': '/wp-content/uploads/2025/03/robot-medicos.jpeg',
    'robot-camarero': '/wp-content/uploads/2025/03/robot-camarero.jpeg',
    'robots-educativos': '/wp-content/uploads/2025/03/robot-educativo.jpeg',
    'robots-para-el-hogar': '/wp-content/uploads/2025/03/robot-para-el-hogar.jpeg',
    'robots-empresariales': '/wp-content/uploads/2025/03/robot-humanoide-para-empresas.jpeg',
}

# Curso que mejor encaja con cada tipo de robot (para la sección de formación).
CURSO_DE_TIPO = {
    'robot-industrial': 'seguridad-y-robotica-colaborativa',
    'robots-de-logistica-y-almacen': 'simulacion-antes-del-despliegue',
    'robots-de-inspeccion-industrial': 'vision-artificial-y-percepcion',
    'robots-de-investigacion': 'programacion-con-sdk',
    'robots-medicos': 'interaccion-por-voz-y-lenguaje',
    'robots-de-rehabilitacion': 'manipulacion-y-agarre',
    'robot-de-compania': 'interaccion-por-voz-y-lenguaje',
    'robots-educativos': 'robotica-para-centros-educativos',
    'robots-de-atencion-al-cliente': 'interaccion-por-voz-y-lenguaje',
    'robot-camarero': 'manipulacion-y-agarre',
    'robots-para-eventos': 'operacion-y-mantenimiento',
    'robots-empresariales': 'formacion-para-equipos-tecnicos',
    'robots-seguridad': 'operacion-y-mantenimiento',
    'robot-de-vigilancia': 'vision-artificial-y-percepcion',
    'robots-para-el-hogar': 'introduccion-a-la-robotica-humanoide',
}


def titulo_tipo(slug):
    return tipos[slug]['h1']


def titulo_curso(slug):
    return cursos[slug]['h1']


def elegir(slug, opciones, sal=''):
    """Elige una variante de forma estable para cada ciudad."""
    h = hashlib.md5((slug + sal).encode('utf-8')).hexdigest()
    return opciones[int(h, 16) % len(opciones)]


def lista_es(items):
    items = list(items)
    if len(items) == 1:
        return items[0]
    ultimo = items[-1]
    # "y" pasa a "e" delante de palabras que empiezan por i- / hi-.
    conj = ' e ' if ultimo.lower().startswith(('i', 'hi')) and not ultimo.lower().startswith('hie') else ' y '
    return ', '.join(items[:-1]) + conj + ultimo


def minus(texto):
    """Primera letra en minúscula salvo siglas/nombres propios evidentes."""
    if not texto:
        return texto
    palabras = texto.split()
    primera = palabras[0]
    # Siglas (UPC), marcas (TechPark) o nombres propios compuestos (Málaga TechPark,
    # Corredor del Henares) se dejan como están.
    if primera.isupper() or any(ch.isupper() for ch in primera[1:]):
        return texto
    if any(w[0].isupper() for w in palabras[1:] if w[0].isalpha()):
        return texto
    return texto[0].lower() + texto[1:]


def etiqueta(sector):
    """Nombre corto del sector para listas: 'Turismo y hostelería' -> 'turismo'."""
    nombre = sector['nombre']
    if ':' in nombre:
        nombre = nombre.split(':', 1)[1].strip()
    for sep in (' y ', ' e '):
        if sep in nombre:
            nombre = nombre.split(sep, 1)[0]
    return minus(nombre)


def nota_fiscal(c):
    if c['pais'] == 'Argentina':
        return ('Al tratarse de una importación, al precio hay que sumar los derechos de aduana y '
                'los impuestos argentinos; nos ocupamos del despacho y te damos el coste total antes de comprar.')
    if c['comunidad'] == 'Canarias':
        return ('En Canarias no se aplica IVA sino IGIC, y el envío desde la península requiere '
                'documentación de exportación; te lo incluimos en el presupuesto para que no haya sorpresas.')
    if c['comunidad'].startswith('Ciudad Autónoma'):
        return ('En ' + c['nombre'] + ' no se aplica IVA sino IPSI, y el envío requiere despacho de aduana; '
                'lo gestionamos nosotros y te damos el precio final puesto en la ciudad.')
    return ('Los precios que publicamos son para toda España e incluyen el IVA; el transporte hasta '
            + c['nombre'] + ' se presupuesta aparte según el volumen del equipo.')


def seccion(clase, interior):
    alt = ' seccion--alt' if clase else ''
    return f'<section class="seccion{alt}"><div class="contenedor">{interior}</div></section>'


def prosa(interior):
    return f'<div class="prosa">{interior}</div>'


def construir(slug, c):
    n = c['nombre']
    sect = c['sectores']
    nombres_sect = [s['nombre'] for s in sect]
    cerca = c['cercanas']

    # ---- 1. Introducción -------------------------------------------------
    h2_intro = elegir(slug, [
        f'Robots humanoides en {n}: para qué sirven y cómo conseguir uno',
        f'Robot humanoide en {n}: guía para empresas, centros y particulares',
        f'Qué puede hacer un robot humanoide en {n}',
        f'Robots humanoides para {n}: usos reales y cómo empezar',
    ], 'intro')
    p_servicio = elegir(slug, [
        f'Desde robothumanoide.org atendemos a empresas, centros educativos, hospitales y particulares de {n} y de toda la provincia de {c["provincia"]}: te ayudamos a elegir el modelo, gestionamos la <a href="/comprar/">compra</a> o el <a href="/alquiler-de-robots-humanoides/">alquiler</a>, lo enviamos y te acompañamos en la puesta en marcha y el <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a>.',
        f'En {n} trabajamos con el mismo equipo que en el resto de España: asesoramiento por videollamada para elegir el <a href="/tipos/">tipo de robot humanoide</a> adecuado, presupuesto cerrado, envío hasta tu dirección y soporte técnico después de la entrega. Si el proyecto lo necesita, concertamos una visita presencial.',
        f'Si buscas un <strong>robot humanoide en {n}</strong>, aquí encontrarás qué modelos encajan con la actividad de la ciudad, cuánto cuestan, cómo llegan y quién te da soporte. Vendemos, alquilamos y programamos robots humanoides de las principales <a href="/marcas/">marcas</a> y los entregamos en toda la provincia de {c["provincia"]}.',
    ], 'serv')
    h3_intro = elegir(slug, [
        f'Qué encontrarás en esta guía de {n}',
        f'Resumen: robots humanoides en {n}',
        f'Lo que debes saber antes de comprar un robot humanoide en {n}',
    ], 'h3i')
    puntos = [
        f'<li><strong>Aplicaciones</strong> en {lista_es(etiqueta(x) for x in sect[:3])}.</li>',
        f'<li><strong>Cómo compramos, entregamos y damos soporte</strong> en {n} y en {lista_es(cerca[:3])}.</li>',
        f'<li><strong>Precio</strong> de un robot humanoide en {n} y qué incluye.</li>',
        f'<li><strong>Formación</strong> en robótica humanoide: centros de {n} y nuestros cursos.</li>',
        f'<li><strong>Preguntas frecuentes</strong> de clientes de {n}.</li>',
    ]
    intro = seccion(False, prosa(
        f'<h2>{h2_intro}</h2><p>{c["rasgo"]}</p><p>{p_servicio}</p>'
        f'<h3>{h3_intro}</h3><ul>{"".join(puntos)}</ul>'
    ))

    # ---- 2. Aplicaciones por sector ---------------------------------------
    h2_apl = elegir(slug, [
        f'Aplicaciones de robots humanoides en {n}',
        f'Dónde se usan los robots humanoides en {n}',
        f'Sectores de {n} que ya pueden usar robots humanoides',
    ], 'apl')
    p_apl = elegir(slug, [
        f'No todos los robots humanoides sirven para lo mismo. Estas son las aplicaciones con más recorrido en {n} según la actividad económica de la ciudad y de su entorno.',
        f'Hemos seleccionado los usos con más sentido para {n} teniendo en cuenta su tejido productivo. Cada uno enlaza con el tipo de robot humanoide que mejor lo resuelve.',
        f'La actividad de {n} marca qué tipo de robot humanoide conviene. Estas son las aplicaciones que más nos consultan desde la ciudad y su comarca.',
    ], 'papl')
    bloques = ''
    for s in sect:
        bloques += (f'<h3>{s["nombre"]}</h3><p>{s["texto"]} '
                    f'<a href="/{s["tipo"]}/">Ver {titulo_tipo(s["tipo"])}</a>.</p>')
    aplicaciones = seccion(True, prosa(f'<h2>{h2_apl}</h2><p>{p_apl}</p>{bloques}'))

    # ---- 3. Cómo trabajamos (con imagen del primer tipo) ------------------
    h2_como = elegir(slug, [
        f'Cómo compramos, entregamos y damos soporte en {n}',
        f'Comprar un robot humanoide en {n}: paso a paso',
        f'Así trabajamos con clientes de {n}',
    ], 'como')
    pasos = [
        f'<li><strong>Asesoramiento</strong>: una videollamada para entender tu caso en {n} y proponerte dos o tres modelos con precio.</li>',
        f'<li><strong>Presupuesto cerrado</strong> con el robot, los <a href="/accesorios/">accesorios</a>, el transporte hasta {n} y, si lo necesitas, la <a href="/importacion-y-gestion-aduanera/">gestión de importación</a>.</li>',
        f'<li><strong>Envío</strong>: {c["acceso"]}</li>',
        f'<li><strong>Puesta en marcha y formación</strong> de tu equipo, online o presencial concertada, con la <a href="/programacion-de-robot-humanoides/">programación</a> inicial que necesite el robot.</li>',
        f'<li><strong>Soporte</strong> remoto continuado y <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a>, con repuestos originales y actualizaciones de software.</li>',
    ]
    p_cerca = elegir(slug, [
        f'Además de {n}, atendemos a clientes de {lista_es(cerca)} y del resto de {c["provincia"]}.',
        f'La misma cobertura se aplica a {lista_es(cerca)}: mismo plazo, mismo soporte.',
        f'Si estás en {lista_es(cerca)} u otro municipio cercano, el proceso es idéntico.',
    ], 'cerca')
    tipo_img = next((s['tipo'] for s in sect if s['tipo'] in IMG_TIPO), None)
    figura = ''
    if tipo_img:
        figura = (f'<figure class="duo__figura"><img src="{IMG_TIPO[tipo_img]}" '
                  f'alt="{titulo_tipo(tipo_img)} en {n}" width="500" height="500" loading="lazy" decoding="async"></figure>')
    invertido = ' duo--invertido' if elegir(slug, [0, 1], 'inv') else ''
    como = seccion(False,
        f'<div class="duo{invertido}"><div class="duo__texto">' +
        prosa(f'<h2>{h2_como}</h2><ol>{"".join(pasos)}</ol><p>{p_cerca}</p>') +
        f'<p class="seccion__cta"><a class="pildora" href="/comprar/">Cómo comprar</a></p></div>{figura}</div>')

    # ---- 4. Precio ----------------------------------------------------------
    h2_precio = elegir(slug, [
        f'Precio de un robot humanoide en {n}',
        f'Cuánto cuesta un robot humanoide en {n}',
        f'Robot humanoide en {n}: precios orientativos',
    ], 'precio')
    s0 = sect[0]
    p_precio = (
        f'El precio depende sobre todo del uso: un <a href="/robots-educativos/">robot humanoide educativo</a> de tamaño pequeño '
        f'parte de alrededor de 1.000 €, un modelo de la categoría <a href="/{s0["tipo"]}/">{titulo_tipo(s0["tipo"])}</a>, como los que se usan en '
        f'{etiqueta(s0)} en {n}, se mueve entre 15.000 y 50.000 € según autonomía y manipulación, y las plataformas de investigación '
        f'de gama alta superan esa cifra. {nota_fiscal(c)} Si prefieres no inmovilizar capital, en {n} también ofrecemos '
        f'<a href="/renting-y-robot-como-servicio/">renting y robot como servicio</a> y <a href="/alquiler-de-robots-humanoides/">alquiler</a> por días o meses.'
    )
    precio = seccion(True, prosa(f'<h2>{h2_precio}</h2><p>{p_precio}</p>') +
                     '<p class="seccion__cta"><a class="pildora" href="/precios/">Ver todos los precios</a></p>')

    # ---- 5. Formación ------------------------------------------------------
    h2_form = elegir(slug, [
        f'Formación en robótica humanoide en {n}',
        f'Dónde aprender robótica humanoide en {n}',
        f'Cursos de robótica humanoide para {n}',
    ], 'form')
    cursos_ciudad = []
    for s in sect:
        cs = CURSO_DE_TIPO.get(s['tipo'])
        if cs and cs not in cursos_ciudad:
            cursos_ciudad.append(cs)
    cursos_ciudad = cursos_ciudad[:3]
    li_cursos = ''.join(
        f'<li><a href="/{cs}/">{titulo_curso(cs)}</a></li>' for cs in cursos_ciudad)
    p_form2 = elegir(slug, [
        f'Nuestros <a href="/cursos/">cursos</a> se imparten online en directo, con el robot delante, y para grupos de {n} organizamos sesiones presenciales en tus instalaciones. Los que más encajan con la actividad de la ciudad son:',
        f'Complementamos esa oferta con <a href="/cursos/">formación práctica</a> sobre el robot que vas a usar: online para particulares y equipos pequeños, y presencial en {n} para empresas y centros. Para {n} recomendamos especialmente:',
        f'Si tu equipo en {n} necesita ponerse al día, tenemos <a href="/cursos/">cursos</a> cortos y prácticos, online o presenciales en tus instalaciones. Los más relacionados con los sectores de la ciudad:',
    ], 'form2')
    formacion = seccion(False, prosa(
        f'<h2>{h2_form}</h2><p>{c["centros"]}</p><p>{p_form2}</p><ul>{li_cursos}</ul>'))

    # ---- 6. Eventos ---------------------------------------------------------
    h2_ev = elegir(slug, [
        f'Robots humanoides para eventos en {n}',
        f'Alquiler de robots para ferias y eventos en {n}',
        f'Un robot humanoide en tu evento de {n}',
    ], 'ev')
    p_ev = (f'{c["eventos"]} Ofrecemos <a href="/alquiler-para-eventos/">alquiler de robots humanoides para eventos</a> '
            f'con técnico, guion de interacción y transporte incluidos hasta {n}.')
    eventos = seccion(True, prosa(f'<h2>{h2_ev}</h2><p>{p_ev}</p>'))

    # ---- 7. Preguntas frecuentes --------------------------------------------
    faq = [
        (f'¿Hacéis envíos de robots humanoides a {n}?',
         f'Sí. {c["acceso"]} Entregamos en {n} y en {lista_es(cerca[:4])}; el plazo depende del modelo y de si está en stock en Europa o hay que importarlo, y te lo confirmamos en el presupuesto.'),
        (f'¿Qué robot humanoide conviene a una empresa de {n}?',
         f'Depende del sector. En {n} las aplicaciones con más recorrido son: {"; ".join(minus(x) for x in nombres_sect)}. Para {etiqueta(sect[0])} solemos recomendar modelos de la categoría {titulo_tipo(sect[0]["tipo"])}; para {etiqueta(sect[1])}, de la categoría {titulo_tipo(sect[1]["tipo"])}. Te asesoramos sin compromiso.'),
        (f'¿Puedo alquilar un robot humanoide para un evento en {n}?',
         f'Sí, alquilamos robots humanoides por días para ferias, congresos y presentaciones. {c["eventos"]} Incluimos técnico y transporte.'),
        (f'¿Dónde puedo formarme en robótica humanoide en {n}?',
         f'{c["centros"]} Además, nuestros cursos online y presenciales cubren desde la introducción hasta la programación con SDK y la operación diaria del robot.'),
        (f'¿Cuánto cuesta un robot humanoide en {n}?',
         f'Desde unos 1.000 € en modelos educativos pequeños hasta más de 50.000 € en plataformas avanzadas. {nota_fiscal(c)}'),
        (f'¿Ofrecéis soporte técnico en {n}?',
         f'Sí. El soporte de primer nivel es remoto y continuado; para averías que requieran intervención física en {n} coordinamos la recogida del equipo o una visita concertada, y trabajamos con repuestos originales de cada marca.'),
    ]
    acordeon = ''.join(
        f'<details class="pregunta"><summary>{q}</summary><div class="pregunta__resp"><p>{r}</p></div></details>'
        for q, r in faq)
    h2_faq = elegir(slug, [
        f'Preguntas frecuentes sobre robots humanoides en {n}',
        f'Dudas habituales de clientes de {n}',
        f'Preguntas frecuentes: robot humanoide en {n}',
    ], 'faq')
    preguntas = seccion(False, prosa(f'<h2>{h2_faq}</h2>') + f'<div class="acordeon">{acordeon}</div>')

    html = '\n'.join([intro, aplicaciones, como, precio, formacion, eventos, preguntas])

    # ---- Metadatos -----------------------------------------------------------
    tres = [etiqueta(x) for x in sect[:3]]
    candidatas = [
        f'Robots humanoides en {n} ({c["provincia"]}): venta, alquiler y formación para {lista_es(tres)}. Envío a {n} y {cerca[0]}, asesoramiento y soporte.',
        f'Robots humanoides en {n}: venta, alquiler y formación para {lista_es(tres)}. Envío, asesoramiento y soporte técnico.',
        f'Robots humanoides en {n}: venta, alquiler y formación para {lista_es(tres[:2])}. Envío y soporte.',
        f'Robot humanoide en {n}: venta, alquiler, formación y soporte.',
    ]
    meta_desc = next(m for m in candidatas if len(m) <= 160)
    entradilla = (f'<strong>Robots humanoides</strong> para {lista_es(tres)} en {n}: '
                  f'venta, alquiler, formación y soporte')

    return {
        'h1': f'Robot Humanoide en {n} - {c["pais"]}',
        'entradilla': entradilla,
        'metaDescripcion': meta_desc,
        'faq': [{'pregunta': q, 'respuesta': r} for q, r in faq],
        'html': html,
    }


def construir_ar(slug, c):
    """Página de ciudad para la versión argentina (/ar/<slug>/).

    Mismo esqueleto que construir(), pero redactada para Argentina: voseo,
    precios en dólares, importación con despachante ante ARCA y enlaces a
    las páginas de /ar/ cuando existen.
    """
    n = c['nombre']
    sect = c['sectores']
    nombres_sect = [s['nombre'] for s in sect]
    cerca = c['cercanas']
    prov = c['provincia']
    en_prov = 'la Ciudad de Buenos Aires y el conurbano' if slug == 'buenos-aires' else f'toda la provincia de {prov}'

    # ---- 1. Introducción -------------------------------------------------
    h2_intro = elegir(slug, [
        f'Robots humanoides en {n}: para qué sirven y cómo conseguir uno',
        f'Robot humanoide en {n}: guía para empresas, instituciones y particulares',
        f'Qué puede hacer un robot humanoide en {n}',
        f'Robots humanoides para {n}: usos reales y cómo empezar',
    ], 'intro')
    p_servicio = elegir(slug, [
        f'Desde robothumanoide.org atendemos a empresas, escuelas, universidades, clínicas y particulares de {n} y de {en_prov}: te ayudamos a elegir el modelo, gestionamos la <a href="/ar/comprar/">compra e importación</a> o el <a href="/alquiler-de-robots-humanoides/">alquiler</a>, lo traemos hasta tu puerta y te acompañamos en la puesta en marcha y el <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a>.',
        f'En {n} trabajamos igual que en el resto de Argentina: asesoramiento por videollamada para elegir el <a href="/ar/tipos/">tipo de robot humanoide</a> adecuado, presupuesto en dólares con la importación incluida, entrega en tu dirección y soporte técnico después. Si el proyecto lo pide, coordinamos una visita presencial.',
        f'Si buscás un <strong>robot humanoide en {n}</strong>, acá vas a encontrar qué modelos encajan con la actividad de la ciudad, cuánto cuestan puestos en Argentina, cómo se importan y quién te da soporte. Vendemos, alquilamos y programamos robots humanoides de las principales <a href="/marcas/">marcas</a> y los entregamos en {en_prov}.',
    ], 'serv')
    h3_intro = elegir(slug, [
        f'Qué vas a encontrar en esta guía de {n}',
        f'Resumen: robots humanoides en {n}',
        f'Lo que tenés que saber antes de comprar un robot humanoide en {n}',
    ], 'h3i')
    puntos = [
        f'<li><strong>Aplicaciones</strong> en {lista_es(etiqueta(x) for x in sect[:3])}.</li>',
        f'<li><strong>Cómo importamos, entregamos y damos soporte</strong> en {n} y en {lista_es(cerca[:3])}.</li>',
        f'<li><strong>Precio</strong> de un robot humanoide en {n}, en dólares y con la importación.</li>',
        f'<li><strong>Formación</strong> en robótica humanoide: universidades de {n} y nuestros cursos.</li>',
        f'<li><strong>Preguntas frecuentes</strong> de clientes de {n}.</li>',
    ]
    intro = seccion(False, prosa(
        f'<h2>{h2_intro}</h2><p>{c["rasgo"]}</p><p>{p_servicio}</p>'
        f'<h3>{h3_intro}</h3><ul>{"".join(puntos)}</ul>'
    ))

    # ---- 2. Aplicaciones por sector ---------------------------------------
    h2_apl = elegir(slug, [
        f'Aplicaciones de robots humanoides en {n}',
        f'Dónde se usan los robots humanoides en {n}',
        f'Sectores de {n} que ya pueden usar robots humanoides',
    ], 'apl')
    p_apl = elegir(slug, [
        f'No todos los robots humanoides sirven para lo mismo. Estas son las aplicaciones con más recorrido en {n} según la actividad económica de la ciudad y su zona.',
        f'Elegimos los usos con más sentido para {n} teniendo en cuenta su entramado productivo. Cada uno enlaza con el tipo de robot humanoide que mejor lo resuelve.',
        f'La actividad de {n} define qué tipo de robot humanoide conviene. Estas son las aplicaciones por las que más nos consultan desde la ciudad y alrededores.',
    ], 'papl')
    bloques = ''
    for s in sect:
        bloques += (f'<h3>{s["nombre"]}</h3><p>{s["texto"]} '
                    f'<a href="/{s["tipo"]}/">Ver {titulo_tipo(s["tipo"])}</a>.</p>')
    aplicaciones = seccion(True, prosa(f'<h2>{h2_apl}</h2><p>{p_apl}</p>{bloques}'))

    # ---- 3. Cómo trabajamos -------------------------------------------------
    h2_como = elegir(slug, [
        f'Cómo importamos, entregamos y damos soporte en {n}',
        f'Comprar un robot humanoide en {n}: paso a paso',
        f'Así trabajamos con clientes de {n}',
    ], 'como')
    pasos = [
        f'<li><strong>Asesoramiento</strong>: una videollamada para entender tu caso en {n} y proponerte dos o tres modelos con precio en dólares.</li>',
        f'<li><strong>Presupuesto con costo total</strong>: robot, <a href="/accesorios/">accesorios</a>, flete internacional, derechos de importación, IVA y entrega en {n}, para que sepas cuánto vas a pagar antes de decidir.</li>',
        f'<li><strong>Importación</strong>: el despacho ante ARCA (ex AFIP) lo hace un despachante de aduana; nosotros coordinamos la documentación y la <a href="/importacion-y-gestion-aduanera/">gestión aduanera</a>.</li>',
        f'<li><strong>Entrega</strong>: {c["acceso"]}</li>',
        f'<li><strong>Puesta en marcha y capacitación</strong> de tu equipo, online o presencial, con la <a href="/programacion-de-robot-humanoides/">programación</a> inicial que necesite el robot.</li>',
        f'<li><strong>Soporte</strong> remoto continuo y <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a>, con repuestos originales y actualizaciones de software.</li>',
    ]
    p_cerca = elegir(slug, [
        f'Además de {n}, atendemos a clientes de {lista_es(cerca)} y del resto de la provincia de {prov}.',
        f'La misma cobertura vale para {lista_es(cerca)}: mismo proceso, mismo soporte.',
        f'Si estás en {lista_es(cerca)} u otra localidad cercana, el proceso es idéntico.',
    ], 'cerca')
    tipo_img = next((s['tipo'] for s in sect if s['tipo'] in IMG_TIPO), None)
    figura = ''
    if tipo_img:
        figura = (f'<figure class="duo__figura"><img src="{IMG_TIPO[tipo_img]}" '
                  f'alt="{titulo_tipo(tipo_img)} en {n}" width="500" height="500" loading="lazy" decoding="async"></figure>')
    invertido = ' duo--invertido' if elegir(slug, [0, 1], 'inv') else ''
    como = seccion(False,
        f'<div class="duo{invertido}"><div class="duo__texto">' +
        prosa(f'<h2>{h2_como}</h2><ol>{"".join(pasos)}</ol><p>{p_cerca}</p>') +
        f'<p class="seccion__cta"><a class="pildora" href="/ar/comprar/">Cómo comprar desde Argentina</a></p></div>{figura}</div>')

    # ---- 4. Precio ----------------------------------------------------------
    h2_precio = elegir(slug, [
        f'Precio de un robot humanoide en {n}',
        f'Cuánto cuesta un robot humanoide en {n}',
        f'Robot humanoide en {n}: precios orientativos en dólares',
    ], 'precio')
    s0 = sect[0]
    p_precio = (
        f'En Argentina los robots humanoides se cotizan en dólares. Un <a href="/robots-educativos/">robot humanoide educativo</a> chico '
        f'arranca en torno a 1.500 USD puesto en el país; un modelo de la categoría <a href="/{s0["tipo"]}/">{titulo_tipo(s0["tipo"])}</a>, como los que se usan en '
        f'{etiqueta(s0)} en {n}, va de 20.000 a 60.000 USD según autonomía y manipulación, y las plataformas de investigación de gama alta superan esa cifra. '
        f'Sobre el precio de fábrica hay que sumar flete, derechos de importación, tasa de estadística, IVA y percepciones: en total, entre un 40% y un 70% más. '
        f'Si no querés inmovilizar capital, en {n} también ofrecemos <a href="/alquiler-de-robots-humanoides/">alquiler</a> por días o meses.'
    )
    precio = seccion(True, prosa(f'<h2>{h2_precio}</h2><p>{p_precio}</p>') +
                     '<p class="seccion__cta"><a class="pildora" href="/ar/precios/">Ver precios en Argentina</a></p>')

    # ---- 5. Formación ------------------------------------------------------
    h2_form = elegir(slug, [
        f'Formación en robótica humanoide en {n}',
        f'Dónde aprender robótica humanoide en {n}',
        f'Cursos de robótica humanoide para {n}',
    ], 'form')
    cursos_ciudad = []
    for s in sect:
        cs = CURSO_DE_TIPO.get(s['tipo'])
        if cs and cs not in cursos_ciudad:
            cursos_ciudad.append(cs)
    li_cursos = ''.join(
        f'<li><a href="/{cs}/">{titulo_curso(cs)}</a></li>' for cs in cursos_ciudad[:3])
    p_form2 = elegir(slug, [
        f'Nuestros <a href="/ar/cursos/">cursos</a> se dictan online en vivo, en horario de Argentina y con el robot delante, y para grupos de {n} organizamos jornadas presenciales. Los que mejor encajan con la actividad de la ciudad son:',
        f'Sumamos a esa oferta <a href="/ar/cursos/">capacitación práctica</a> sobre el robot que vas a usar: online para particulares y equipos chicos, y presencial en {n} para empresas e instituciones. Para {n} recomendamos especialmente:',
        f'Si tu equipo en {n} necesita ponerse al día, tenemos <a href="/ar/cursos/">cursos</a> cortos y prácticos, online o presenciales en tu empresa. Los más relacionados con los sectores de la ciudad:',
    ], 'form2')
    formacion = seccion(False, prosa(
        f'<h2>{h2_form}</h2><p>{c["centros"]}</p><p>{p_form2}</p><ul>{li_cursos}</ul>'))

    # ---- 6. Eventos ---------------------------------------------------------
    h2_ev = elegir(slug, [
        f'Robots humanoides para eventos en {n}',
        f'Alquiler de robots para ferias y eventos en {n}',
        f'Un robot humanoide en tu evento en {n}',
    ], 'ev')
    p_ev = (f'{c["eventos"]} Ofrecemos <a href="/alquiler-para-eventos/">alquiler de robots humanoides para eventos</a> '
            f'con técnico, guion de interacción y traslado hasta {n}.')
    eventos = seccion(True, prosa(f'<h2>{h2_ev}</h2><p>{p_ev}</p>'))

    # ---- 7. Preguntas frecuentes --------------------------------------------
    faq = [
        (f'¿Hacen envíos de robots humanoides a {n}?',
         f'Sí. {c["acceso"]} Entregamos en {n} y en {lista_es(cerca[:4])}; el plazo depende del modelo y de la aduana, y te lo confirmamos en el presupuesto.'),
        (f'¿Cuánto cuesta un robot humanoide en {n}?',
         f'Desde unos 1.500 USD en modelos educativos chicos hasta más de 60.000 USD en plataformas avanzadas, ya puestos en Argentina. El precio de fábrica es solo una parte: flete, derechos de importación, IVA y percepciones suman entre un 40% y un 70%. Te pasamos el costo total antes de comprar.'),
        (f'¿Se puede importar un robot humanoide a Argentina sin ser importador?',
         f'Sí. Como particular podés traer modelos chicos por courier dentro de los límites de valor del régimen vigente; para equipos profesionales conviene una importación formal con despachante de aduana. Desde {n} te gestionamos las dos vías y te decimos cuál conviene según el modelo.'),
        (f'¿Qué robot humanoide conviene a una empresa de {n}?',
         f'Depende del sector. En {n} las aplicaciones con más recorrido son: {"; ".join(minus(x) for x in nombres_sect)}. Para {etiqueta(sect[0])} solemos recomendar modelos de la categoría {titulo_tipo(sect[0]["tipo"])}; para {etiqueta(sect[1])}, de la categoría {titulo_tipo(sect[1]["tipo"])}. Te asesoramos sin compromiso.'),
        (f'¿Dónde puedo capacitarme en robótica humanoide en {n}?',
         f'{c["centros"]} Además, nuestros cursos online y presenciales cubren desde la introducción hasta la programación con SDK y la operación diaria del robot.'),
        (f'¿Tienen soporte técnico en {n}?',
         f'Sí. El soporte de primer nivel es remoto y continuo; para fallas que requieran intervención física en {n} coordinamos el retiro del equipo o una visita, y trabajamos con repuestos originales de cada marca.'),
    ]
    acordeon = ''.join(
        f'<details class="pregunta"><summary>{q}</summary><div class="pregunta__resp"><p>{r}</p></div></details>'
        for q, r in faq)
    h2_faq = elegir(slug, [
        f'Preguntas frecuentes sobre robots humanoides en {n}',
        f'Dudas habituales de clientes de {n}',
        f'Preguntas frecuentes: robot humanoide en {n}',
    ], 'faq')
    preguntas = seccion(False, prosa(f'<h2>{h2_faq}</h2>') + f'<div class="acordeon">{acordeon}</div>')

    html = '\n'.join([intro, aplicaciones, como, precio, formacion, eventos, preguntas])

    tres = [etiqueta(x) for x in sect[:3]]
    candidatas = [
        f'Robots humanoides en {n}, Argentina: venta, importación, alquiler y formación para {lista_es(tres)}. Precios en dólares y soporte.',
        f'Robots humanoides en {n}, Argentina: venta, importación y formación para {lista_es(tres[:2])}. Precios en dólares y soporte.',
        f'Robot humanoide en {n}, Argentina: venta, importación, alquiler, formación y soporte.',
    ]
    meta_desc = next((m for m in candidatas if len(m) <= 160), candidatas[-1])
    entradilla = (f'<strong>Robots humanoides</strong> para {lista_es(tres)} en {n}: '
                  f'venta, importación, alquiler, formación y soporte')

    return {
        'titulo': f'Robot Humanoide {n}',
        'url': f'/ar/{slug}/',
        'slug': slug,
        'h1': f'Robot Humanoide en {n} - Argentina',
        'entradilla': entradilla,
        'cta': {'url': '/ar/contacto/', 'texto': 'Pedir presupuesto'},
        'metaTitulo': f'Robot Humanoide en {n}, Argentina - Precios y Venta',
        'metaDescripcion': meta_desc,
        'focusKeyword': f'robot humanoide {n}',
        'faq': [{'pregunta': q, 'respuesta': r} for q, r in faq],
        'html': html,
    }


def main():
    hechas = 0
    for slug, c in ciudades.items():
        ruta = os.path.join(PAGINAS, slug + '.json')
        with open(ruta, encoding='utf-8') as f:
            pagina = json.load(f)
        nuevo = construir(slug, c)
        pagina.update(nuevo)
        pagina.pop('noindex', None)
        pagina['botones'] = {}
        with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(pagina, f, ensure_ascii=False, indent=2)
            f.write('\n')
        hechas += 1

    # Versión argentina: se crean si no existen. La imagen se declara con el
    # nombre esperado; mientras no se suba, la página sale sin cabecera.
    os.makedirs(os.path.join(PAGINAS, 'ar'), exist_ok=True)
    for slug, c in ciudades_ar.items():
        if slug.startswith('_'):
            continue
        ruta = os.path.join(PAGINAS, 'ar', slug + '.json')
        pagina = {}
        if os.path.exists(ruta):
            with open(ruta, encoding='utf-8') as f:
                pagina = json.load(f)
        imagen = pagina.get('hero') or f'/wp-content/uploads/2026/01/robot-humanoide-{slug}.webp'
        if slug == 'cordoba':
            # /cordoba/ es Córdoba (España): la de Argentina lleva otro archivo.
            imagen = '/wp-content/uploads/2026/01/robot-humanoide-cordoba-argentina.webp'
        pagina.update(construir_ar(slug, c))
        pagina['hero'] = imagen
        pagina['imagenPrincipal'] = imagen if os.path.exists(os.path.join(RAIZ, 'public', imagen.lstrip('/'))) else None
        pagina['botones'] = {}
        pagina.pop('noindex', None)
        with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(pagina, f, ensure_ascii=False, indent=2)
            f.write('\n')
        hechas += 1
    print(f'{hechas} páginas de ciudad generadas')


if __name__ == '__main__':
    main()
