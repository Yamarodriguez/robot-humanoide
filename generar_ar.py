# Genera las páginas principales de la versión argentina (/ar/) en
# src/content/pages/ar/. Cada una declara "alterna" con su equivalente en la
# raíz: de ahí salen los hreflang (es / es-AR / x-default).
#
# El contenido está escrito para Argentina, no traducido: voseo, precios en
# dólares, importación con despachante ante ARCA, ciudades argentinas.
# Un clon con cuatro palabras cambiadas Google lo trata como duplicado.
#
# Uso:  python generar_ar.py
# Las ciudades argentinas las genera generar_ciudades.py.

import json
import os

RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(RAIZ, 'src', 'content', 'pages', 'ar')
CIUDADES_ENLACE = [('buenos-aires', 'Buenos Aires'), ('cordoba', 'Córdoba'), ('rosario', 'Rosario'),
                   ('mendoza', 'Mendoza'), ('santa-fe', 'Santa Fe'), ('la-plata', 'La Plata'),
                   ('mar-del-plata', 'Mar del Plata'), ('tucuman', 'Tucumán'),
                   ('neuquen', 'Neuquén'), ('salta', 'Salta')]


# ---------------------------------------------------------------- piezas --
def seccion(interior, alt=False):
    clase = 'seccion seccion--alt' if alt else 'seccion'
    return f'<section class="{clase}"><div class="contenedor">{interior}</div></section>'


def prosa(interior):
    return f'<div class="prosa">{interior}</div>'


def boton(url, texto):
    return f'<p class="seccion__cta"><a class="pildora" href="{url}">{texto}</a></p>'


def duo(texto, img, alt, ancho=1024, alto=768, invertido=False):
    inv = ' duo--invertido' if invertido else ''
    return (f'<div class="duo{inv}"><div class="duo__texto">{texto}</div>'
            f'<figure class="duo__figura"><img src="{img}" alt="{alt}" width="{ancho}" height="{alto}" '
            f'loading="lazy" decoding="async"></figure></div>')


def rejilla(tarjetas):
    out = ''
    for url, img, (w, h), titulo, texto in tarjetas:
        out += (f'<article class="tarjeta"><figure><img loading="lazy" decoding="async" width="{w}" height="{h}" '
                f'src="{img}" alt="{titulo}" /></figure><div class="tarjeta__texto">'
                f'<h3><a href="{url}">{titulo}</a></h3><p>{texto}</p></div></article>')
    return f'<div class="rejilla">{out}</div>'


def tabla(cabeceras, filas, nota=''):
    th = ''.join(f'<th scope="col">{c}</th>' for c in cabeceras)
    tr = ''.join('<tr><th scope="row">' + f[0] + '</th>' + ''.join(f'<td>{c}</td>' for c in f[1:]) + '</tr>'
                 for f in filas)
    n = f'<p class="tabla__nota">{nota}</p>' if nota else ''
    return (f'<div class="tabla-envoltorio"><table class="tabla"><thead><tr>{th}</tr></thead>'
            f'<tbody>{tr}</tbody></table></div>{n}')


def preguntas(titulo, faq, alt=False):
    acordeon = ''.join(
        f'<details class="pregunta"><summary>{q}</summary><div class="pregunta__resp"><p>{r}</p></div></details>'
        for q, r in faq)
    return seccion(prosa(f'<h2>{titulo}</h2>') + f'<div class="acordeon">{acordeon}</div>', alt)


def lista_ciudades():
    return '<ul>' + ''.join(f'<li><a href="/ar/{s}/">Robot humanoide en {n}</a></li>'
                            for s, n in CIUDADES_ENLACE) + '</ul>'


def pagina(slug, alterna, titulo, h1, meta_titulo, meta_desc, entradilla, secciones, faq=None,
           hero=None, cta=None, focus=''):
    return {
        'titulo': titulo,
        'url': '/ar/' if slug == 'home' else f'/ar/{slug}/',
        'slug': slug,
        'alterna': alterna,
        'h1': h1,
        'entradilla': entradilla,
        'cta': cta,
        'hero': hero,
        'metaTitulo': meta_titulo,
        'metaDescripcion': meta_desc,
        'focusKeyword': focus,
        'imagenPrincipal': hero,
        'faq': [{'pregunta': q, 'respuesta': r} for q, r in (faq or [])],
        'botones': {},
        'html': '\n'.join(secciones),
    }


# Imágenes de tarjeta (las mismas que usa la versión de la raíz).
U = '/wp-content/uploads/2025/03/'
IMG = {
    'robot-industrial': (U + 'robot-humanoide-industrial.jpg', (500, 500)),
    'robot-de-compania': (U + 'robot-humanoide-de-compania.jpeg', (1280, 1280)),
    'robots-medicos': (U + 'robot-medicos.jpeg', (1280, 1280)),
    'robot-camarero': (U + 'robot-camarero.jpeg', (1280, 1280)),
    'robots-educativos': (U + 'robot-educativo.jpeg', (1280, 1280)),
    'robots-para-el-hogar': (U + 'robot-para-el-hogar.jpeg', (1280, 1280)),
    'robots-empresariales': (U + 'robot-humanoide-para-empresas.jpeg', (1280, 1280)),
    'robots-seguridad': (U + 'robot-seguridad.jpeg', (1280, 1280)),
    'robot-de-vigilancia': (U + 'robot-vigilancia.jpeg', (1280, 1280)),
    'robots-de-logistica-y-almacen': ('/img/tipos/logistica.svg', (800, 600)),
    'robots-de-rehabilitacion': ('/img/tipos/rehabilitacion.svg', (800, 600)),
    'robots-de-investigacion': ('/img/tipos/investigacion.svg', (800, 600)),
    'robots-de-atencion-al-cliente': ('/img/tipos/atencion-cliente.svg', (800, 600)),
    'robots-de-inspeccion-industrial': ('/img/tipos/inspeccion.svg', (800, 600)),
    'robots-para-eventos': ('/img/tipos/eventos.svg', (800, 600)),
    'venta-de-robots-humanoides': (U + 'venta-robot-humanoide.jpeg', (1024, 1024)),
    'programacion-de-robot-humanoides': (U + 'programacion-de-robot-humanoide.jpeg', (1280, 1280)),
    'mantenimiento-y-reparacion-de-robot': (U + 'mantenimiento-robot-humanoide.jpeg', (1280, 1280)),
    'alquiler-de-robots-humanoides': (U + 'alquiler-robot-humanoides.jpeg', (1280, 1280)),
    'implementacion-de-robot-en-empresas-y-negocios': (U + 'empresas-robot-humanoide.jpeg', (1280, 1280)),
    'importacion-y-gestion-aduanera': ('/img/servicios/importacion.svg', (800, 600)),
    'alquiler-para-eventos': ('/img/servicios/eventos.svg', (800, 600)),
    'renting-y-robot-como-servicio': ('/img/servicios/renting.svg', (800, 600)),
    'marcado-ce-y-normativa': ('/img/servicios/marcado-ce.svg', (800, 600)),
    'formacion-y-cursos': ('/img/servicios/formacion.svg', (800, 600)),
    'estudio-de-viabilidad-y-roi': ('/img/servicios/viabilidad.svg', (800, 600)),
    'renting-y-robot-como-servicio': ('/img/servicios/renting.svg', (800, 600)),
    'marcado-ce-y-normativa': ('/img/servicios/marcado-ce.svg', (800, 600)),
    'introduccion-a-la-robotica-humanoide': ('/img/cursos/introduccion.svg', (800, 600)),
    'programacion-con-sdk': ('/img/cursos/sdk.svg', (800, 600)),
    'operacion-y-mantenimiento': ('/img/cursos/mantenimiento.svg', (800, 600)),
    'robotica-para-centros-educativos': ('/img/cursos/educativos.svg', (800, 600)),
    'formacion-para-equipos-tecnicos': ('/img/cursos/equipos.svg', (800, 600)),
    'seguridad-y-robotica-colaborativa': ('/img/cursos/seguridad.svg', (800, 600)),
    'vision-artificial-y-percepcion': ('/img/cursos/vision.svg', (800, 600)),
    'aprendizaje-por-imitacion': ('/img/cursos/imitacion.svg', (800, 600)),
    'simulacion-antes-del-despliegue': ('/img/cursos/simulacion.svg', (800, 600)),
    'interaccion-por-voz-y-lenguaje': ('/img/cursos/voz.svg', (800, 600)),
    'manipulacion-y-agarre': ('/img/cursos/manipulacion.svg', (800, 600)),
    'certificacion-profesional': ('/img/cursos/certificacion.svg', (800, 600)),
}


def tarjetas(items):
    """items: [(slug, titulo, texto)] -> tarjetas con la imagen de IMG."""
    return rejilla([(f'/{s}/', IMG[s][0], IMG[s][1], t, x) for s, t, x in items])


# ----------------------------------------------------------- textos comunes --
COSTO_TOTAL = (
    '<ul>'
    '<li><strong>Precio de fábrica (FOB)</strong>: lo que cobra el fabricante, casi siempre en dólares.</li>'
    '<li><strong>Flete internacional y seguro</strong>: un humanoide viaja en caja de madera; por avión llega antes y cuesta más que por barco.</li>'
    '<li><strong>Derechos de importación</strong>: dependen de la posición arancelaria del equipo en el Nomenclador Común del Mercosur.</li>'
    '<li><strong>Tasa de estadística</strong>: un 3% sobre el valor en aduana.</li>'
    '<li><strong>IVA y percepciones</strong>: el IVA de importación más las percepciones de IVA y Ganancias que cobra ARCA (ex AFIP) en la aduana.</li>'
    '<li><strong>Despachante, depósito fiscal y entrega</strong>: honorarios del despachante, almacenaje y el traslado hasta tu ciudad.</li>'
    '</ul>'
)

TIPOS_AR = [
    ('robot-industrial', 'Robot Humanoide Industrial', 'Para terminales automotrices, autopartistas y metalmecánica: abastecimiento de línea, manipulación de piezas y control de calidad sin rediseñar la planta.'),
    ('robots-de-logistica-y-almacen', 'Robots Humanoides de Logística y Almacén', 'Centros de distribución del conurbano, empaques de fruta y cámaras de frío: picking, reposición y movimiento de cajas en temporada alta.'),
    ('robots-de-inspeccion-industrial', 'Robots Humanoides de Inspección Industrial', 'Plantas de Vaca Muerta, refinerías, ingenios y acopios: rondas de inspección en entornos donde conviene exponer menos al personal.'),
    ('robots-de-atencion-al-cliente', 'Robots Humanoides de Atención al Cliente', 'Bancos, shoppings, concesionarias y oficinas públicas: reciben, orientan y ordenan turnos en espacios con mucho público.'),
    ('robots-educativos', 'Robots Humanoides Educativos', 'Escuelas técnicas, institutos y universidades: enseñar programación, sensores y robótica con un equipo real y no solo con simuladores.'),
    ('robots-de-investigacion', 'Robots Humanoides de Investigación', 'Laboratorios de la UBA, UNC, UNLP, UNR y CONICET y startups de IA: plataformas abiertas para trabajar visión, control y aprendizaje.'),
    ('robots-medicos', 'Robots Humanoides Médicos', 'Hospitales y sanatorios: traslado de insumos, acompañamiento de pacientes y apoyo a un personal de salud que no alcanza.'),
    ('robots-de-rehabilitacion', 'Robots Humanoides de Rehabilitación', 'Centros de rehabilitación y kinesiología: ejercicios guiados, repeticiones medidas y seguimiento de la evolución.'),
    ('robots-para-eventos', 'Robots Humanoides para Eventos', 'Stands en La Rural, Expoagro o congresos: un humanoide atrae público, presenta productos y junta contactos.'),
    ('robot-camarero', 'Robot Camarero', 'Restaurantes, hoteles y balnearios de temporada: llevar platos y bandejas en los picos de trabajo.'),
    ('robot-de-compania', 'Robot Humanoide de Compañía', 'Acompañamiento de adultos mayores: conversación, recordatorios de medicación y aviso a la familia.'),
    ('robots-para-el-hogar', 'Robots Humanoides para el Hogar', 'Tareas domésticas simples y asistencia en casa; la categoría que más crece y la que más promete a mediano plazo.'),
    ('robots-empresariales', 'Robots Humanoides para Empresas', 'Recepción, demostraciones comerciales y tareas de back office en pymes y grandes empresas.'),
    ('robots-seguridad', 'Robots Humanoides de Seguridad', 'Rondas en barrios cerrados, parques industriales y depósitos, con cámaras y aviso a la central.'),
    ('robot-de-vigilancia', 'Robot Humanoide de Vigilancia', 'Monitoreo nocturno de plantas y edificios, detección de intrusos y registro de incidencias.'),
]

FAQ_GENERAL = [
    ('¿Cuánto cuesta un robot humanoide en Argentina?',
     'Depende del modelo. Los educativos chicos arrancan en torno a 1.500 USD puestos en el país; el Unitree G1, el humanoide completo más vendido, cuesta unos 16.000 USD en fábrica y entre 23.000 y 28.000 USD puesto en Argentina con flete, impuestos y despacho. Las plataformas industriales superan los 60.000 USD.'),
    ('¿Se puede comprar un robot humanoide en Argentina?',
     'Sí, pero casi siempre por importación: no hay fabricantes locales de humanoides comerciales y los distribuidores oficiales son pocos. Lo habitual es importarlo desde China, Estados Unidos o Europa con despachante de aduana. Nosotros gestionamos todo el proceso y te entregamos el robot funcionando.'),
    ('¿Puedo pagar en pesos?',
     'Los robots se cotizan en dólares porque así los venden los fabricantes. Consultanos las formas de pago disponibles al momento de pedir el presupuesto.'),
    ('¿Cuánto tarda en llegar un robot humanoide a Argentina?',
     'Entre cuatro semanas y tres meses. Influye si el modelo está en stock en fábrica, si viaja por avión o por barco y cuánto demora el despacho en aduana. En el presupuesto te damos un plazo realista.'),
    ('¿Tiene garantía y servicio técnico en Argentina?',
     'Sí. La garantía de fábrica suele ser de uno a dos años; nosotros damos soporte remoto, gestionamos repuestos originales y coordinamos la reparación cuando hace falta intervenir el equipo.'),
    ('¿Funciona con la corriente de Argentina?',
     'Sí. Los humanoides de fabricantes chinos como Unitree trabajan con 220 V y 50 Hz, igual que la red argentina, pero la ficha china, aunque se parece a la nuestra, tiene la polaridad invertida: hay que usar el cable adecuado. Igual lo verificamos modelo por modelo antes de importar.'),
]


# ------------------------------------------------------------------ páginas --
def home():
    s = [
        seccion(prosa(
            '<h2>Robots humanoides en Argentina: venta, importación y soporte</h2>'
            '<p>Somos un equipo especializado en <strong>robots humanoides</strong> que trabaja con clientes de toda Argentina: empresas industriales, '
            'universidades, escuelas técnicas, clínicas, agencias de eventos y particulares. Te ayudamos a elegir el modelo, lo <strong>importamos con despachante</strong>, '
            'te lo entregamos funcionando y te damos soporte después.</p>'
            '<p>En Argentina comprar un humanoide no es como comprar una notebook: no hay fabricantes locales, casi todo se importa y el precio final depende del '
            'dólar, del flete y de la aduana. Por eso esta sección está pensada para el comprador argentino: <strong>precios en dólares</strong>, costos de '
            'importación explicados y ciudades donde ya trabajamos.</p>'
            '<h3>Qué vas a encontrar acá</h3><ul>'
            '<li><a href="/ar/que-es/">Qué es un robot humanoide</a> y qué puede hacer hoy de verdad.</li>'
            '<li><a href="/ar/tipos/">Tipos de robots humanoides</a> según el sector: industria, agro, energía, salud, educación.</li>'
            '<li><a href="/ar/precios/">Precios en Argentina</a>: cuánto cuesta cada modelo puesto en el país.</li>'
            '<li><a href="/ar/comprar/">Cómo comprar e importar</a> un robot humanoide paso a paso.</li>'
            '<li><a href="/ar/servicios/">Servicios</a> y <a href="/ar/cursos/">cursos</a> con horario de Argentina.</li>'
            '</ul>')),
        seccion(duo(prosa(
            '<h2>¿Qué es un robot humanoide?</h2>'
            '<p>Un <strong>robot humanoide</strong> es una máquina con forma de persona —cabeza, torso, brazos y piernas— que combina motores, sensores e '
            'inteligencia artificial para moverse y trabajar en espacios pensados para humanos. Esa es su ventaja: no hace falta adaptar la fábrica, '
            'el depósito ni el local para que pueda operar.</p>'
            '<ul><li><strong>Se mueve</strong> como nosotros: camina, sube escalones, agarra objetos.</li>'
            '<li><strong>Percibe</strong> el entorno con cámaras, LiDAR y micrófonos.</li>'
            '<li><strong>Aprende</strong> tareas nuevas con programación o por imitación.</li></ul>') +
            boton('/ar/que-es/', 'Qué es un robot humanoide'),
            U + 'que-es-un-robot-humanoide.webp', '¿Qué es un robot humanoide?'), alt=True),
        seccion(prosa(
            '<h2>Tipos de robots humanoides para la economía argentina</h2>'
            '<p>El humanoide que conviene depende de la tarea. Estos son los tipos con más demanda en Argentina, ordenados por los sectores que más consultan.</p>') +
            tarjetas(TIPOS_AR[:6]) + boton('/ar/tipos/', 'Ver todos los tipos')),
        seccion(prosa(
            '<h2>Precio de un robot humanoide en Argentina</h2>'
            '<p>El error más común es mirar el precio de fábrica y pensar que es lo que se paga. Entre el precio en China y el robot en tu empresa se suman '
            'flete, derechos de importación, tasa de estadística, IVA, percepciones y despachante: <strong>entre un 40% y un 70% más</strong>.</p>') +
            tabla(['Modelo', 'Precio en fábrica', 'Puesto en Argentina (estimado)'], [
                ['Unitree R1', 'unos 5.900 USD', '8.500 – 10.500 USD'],
                ['Unitree G1', 'unos 16.000 USD', '23.000 – 28.000 USD'],
                ['Booster K1', 'consultar', 'a cotizar'],
                ['Humanoides industriales', '40.000 USD o más', '60.000 USD o más'],
            ], 'Valores orientativos de octubre de 2026. Dependen del dólar, del flete y de la posición arancelaria: pedí siempre presupuesto cerrado.') +
            boton('/ar/precios/', 'Ver precios en Argentina'), alt=True),
        seccion(duo(prosa(
            '<h2>Cómo comprar un robot humanoide desde Argentina</h2>'
            '<ol><li><strong>Nos contás el uso</strong> y te proponemos dos o tres modelos.</li>'
            '<li><strong>Presupuesto con costo total</strong>: robot, flete, impuestos y entrega, en dólares.</li>'
            '<li><strong>Importación</strong> con despachante de aduana ante ARCA.</li>'
            '<li><strong>Entrega y puesta en marcha</strong> en tu ciudad, con capacitación.</li>'
            '<li><strong>Soporte</strong> remoto, repuestos y mantenimiento.</li></ol>') +
            boton('/ar/comprar/', 'Guía de compra'),
            U + 'comprar-robot-humanoides.webp', 'Comprar un robot humanoide en Argentina', invertido=True)),
        seccion(prosa(
            '<h2>Servicios y capacitación</h2>'
            '<p>Además de la venta, hacemos <a href="/importacion-y-gestion-aduanera/">gestión de importación</a>, '
            '<a href="/programacion-de-robot-humanoides/">programación</a>, <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a> y '
            '<a href="/alquiler-para-eventos/">alquiler para eventos</a>. Los <a href="/ar/cursos/">cursos</a> se dictan online en vivo en horario de Argentina '
            'o presenciales para equipos de empresas y universidades.</p>') +
            boton('/ar/servicios/', 'Ver servicios'), alt=True),
        seccion(prosa(
            '<h2>Ciudades de Argentina donde trabajamos</h2>'
            '<p>Entregamos en todo el país. Estas son las ciudades con guía propia, con los sectores, universidades y espacios de eventos de cada una:</p>' +
            lista_ciudades())),
        preguntas('Preguntas frecuentes sobre robots humanoides en Argentina', FAQ_GENERAL, alt=True),
    ]
    return pagina('home', '/', 'Robot Humanoide Argentina', 'Robot Humanoide en Argentina',
                  'Robot Humanoide en Argentina - Precios, Venta e Importación',
                  'Robots humanoides en Argentina: precios en dólares, importación con despachante, venta, alquiler y cursos. Envíos a Buenos Aires, Córdoba, Rosario y todo el país.',
                  '<strong>Robots humanoides</strong> en Argentina: te ayudamos a elegir, importar y poner en marcha el modelo que necesitás.',
                  s, FAQ_GENERAL, hero=U + 'robot-humanoide.webp',
                  cta={'url': '/ar/contacto/', 'texto': 'Pedir presupuesto'}, focus='robot humanoide Argentina')


def que_es():
    faq = [
        ('¿Qué significa humanoide?', 'Humanoide quiere decir «con forma humana». Un robot humanoide tiene cabeza, torso, dos brazos y, en la mayoría de los casos, dos piernas.'),
        ('¿Es lo mismo un robot humanoide que un androide?', 'No exactamente. Todo androide es humanoide, pero el androide busca además parecerse a una persona en la piel, la cara y los gestos. La mayoría de los humanoides comerciales tienen aspecto claramente mecánico.'),
        ('¿Hay robots humanoides en Argentina?', 'Sí. Universidades como la UBA, la UNC o la UNLP y algunas empresas ya trabajan con humanoides importados, sobre todo de Unitree. También hay humanoides en eventos y en demostraciones comerciales. Todavía no hay fabricación local.'),
        ('¿Qué puede hacer hoy un robot humanoide?', 'Caminar, mantener el equilibrio, manipular objetos livianos, reconocer personas y objetos y conversar. Las tareas complejas o muy variables todavía necesitan programación específica o supervisión humana.'),
        ('¿Cuánto dura la batería?', 'Entre una y cuatro horas de trabajo continuo en los modelos actuales. Algunos permiten cambiar la batería en caliente para no frenar la operación.'),
    ]
    s = [
        seccion(prosa(
            '<h2>Robot humanoide: definición simple</h2>'
            '<p>Un <strong>robot humanoide</strong> es un robot construido con la forma del cuerpo humano. Tiene <strong>cabeza</strong> con cámaras y micrófonos, '
            '<strong>torso</strong> donde van la computadora y la batería, <strong>brazos</strong> con manos o pinzas y, en la mayoría de los modelos, '
            '<strong>piernas</strong> para caminar. La idea es que pueda moverse y trabajar en lugares hechos para personas —escaleras, pasillos, mesadas, '
            'estanterías— sin tener que rediseñarlos.</p>'
            '<p>Durante décadas fue un tema de laboratorio. Desde 2023, con la llegada de modelos comerciales como el <a href="/unitree-g1/">Unitree G1</a> y '
            'los avances en inteligencia artificial, el humanoide empezó a venderse a empresas, universidades y particulares, también en Argentina.</p>')),
        seccion(duo(prosa(
            '<h2>Cómo funciona un robot humanoide</h2>'
            '<h3>Cuerpo: actuadores y estructura</h3>'
            '<p>Cada articulación tiene un <strong>actuador</strong> —motor, reductora y sensor de posición— que la mueve con precisión. Un humanoide completo '
            'tiene entre 20 y 40 articulaciones. Los actuadores son la pieza más cara y la que más se desgasta.</p>'
            '<h3>Sentidos: cámaras, LiDAR y sensores</h3>'
            '<p>Cámaras de profundidad, <strong>LiDAR</strong>, sensores de fuerza en pies y manos y una unidad inercial le permiten saber dónde está, qué tiene '
            'adelante y si está por perder el equilibrio.</p>'
            '<h3>Cerebro: control e inteligencia artificial</h3>'
            '<p>Un control de bajo nivel mantiene el equilibrio cientos de veces por segundo. Encima trabaja la <strong>inteligencia artificial</strong>: '
            'visión para reconocer objetos, modelos de lenguaje para conversar y aprendizaje por imitación para incorporar tareas nuevas.</p>'),
            U + 'que-es-un-robot-humanoide.webp', 'Cómo funciona un robot humanoide'), alt=True),
        seccion(prosa(
            '<h2>Diferencia entre un robot humanoide y otros robots</h2>'
            '<ul><li><strong>Robot industrial clásico</strong>: un brazo fijo, muy rápido y preciso, que hace siempre lo mismo dentro de una celda cerrada. '
            'Es lo que se ve en las líneas de pintura y soldadura de las automotrices.</li>'
            '<li><strong>Cobot</strong>: brazo colaborativo que puede trabajar al lado de personas, pero sigue fijo en un puesto.</li>'
            '<li><strong>Robot móvil (AMR)</strong>: plataforma con ruedas que lleva carga por el depósito, pero no puede manipular ni subir escalones.</li>'
            '<li><strong>Robot humanoide</strong>: se desplaza, manipula y usa las mismas herramientas y espacios que una persona. Es menos rápido que un '
            'brazo industrial, pero mucho más versátil.</li></ul>')),
        seccion(prosa(
            '<h2>Robots humanoides en Argentina hoy</h2>'
            '<p>Argentina no fabrica humanoides comerciales, pero tiene una base técnica sólida para usarlos: ingenierías en electrónica, mecatrónica y '
            'computación en la UBA, la UTN, la UNC, la UNLP, la UNR y el ITBA, grupos del CONICET que investigan visión y control, y un sector de software '
            'con fuerte presencia en Buenos Aires, Córdoba, Rosario y Mendoza.</p>'
            '<p>Los primeros usos que vemos en el país son la <strong>investigación universitaria</strong>, la <strong>educación técnica</strong>, las '
            '<strong>ferias y eventos</strong> y los <strong>pilotos industriales</strong> en automotrices, agroindustria y energía. La limitación principal no es '
            'técnica sino económica: todo se importa en dólares, y por eso conviene calcular bien el <a href="/ar/precios/">costo total</a> antes de comprar.</p>'
            '<h3>Sectores argentinos con más potencial</h3><ul>'
            '<li><strong>Automotriz y autopartes</strong> en Córdoba, Santa Fe y Buenos Aires.</li>'
            '<li><strong>Agroindustria y puertos</strong> en el Gran Rosario y la pampa húmeda.</li>'
            '<li><strong>Petróleo y gas</strong> en Vaca Muerta y Neuquén.</li>'
            '<li><strong>Salud</strong> en los hospitales de alta complejidad.</li>'
            '<li><strong>Educación</strong> en escuelas técnicas y universidades.</li></ul>') +
            boton('/ar/tipos/', 'Tipos de robots humanoides'), alt=True),
        preguntas('Preguntas frecuentes', faq),
    ]
    return pagina('que-es', '/que-es/', 'Qué es un Robot Humanoide', 'Qué es un Robot Humanoide',
                  'Qué es un Robot Humanoide: Definición, Cómo Funciona y Usos en Argentina',
                  'Qué es un robot humanoide, cómo funciona, en qué se diferencia de otros robots y cómo se está usando en Argentina en industria, educación y salud.',
                  'Un <strong>robot humanoide</strong> es una máquina con forma de persona que se mueve, percibe y aprende para trabajar en espacios pensados para humanos.',
                  s, faq, hero=U + 'que-es-un-robot-humanoide.webp', focus='qué es un robot humanoide')


def tipos():
    faq = [
        ('¿Qué tipo de robot humanoide conviene a una pyme?', 'Para atención al público y demostraciones, un humanoide de atención al cliente; para tareas de depósito, uno de logística. Antes de comprar conviene un estudio de viabilidad para saber si la tarea se puede automatizar hoy.'),
        ('¿Cuál es el robot humanoide más usado en universidades argentinas?', 'El Unitree G1, por precio, SDK abierto y comunidad. Para escuelas y cursos introductorios se usan modelos educativos más chicos y baratos.'),
        ('¿Sirve un humanoide para el campo?', 'Hoy no para tareas a cielo abierto como cosecha. Sí para galpones de empaque, acopios y plantas agroindustriales, donde el entorno es más controlado.'),
    ]
    s = [
        seccion(prosa(
            '<h2>Tipos de robots humanoides y para qué sirve cada uno</h2>'
            '<p>No existe un humanoide que sirva para todo. Cada tipo está pensado para un entorno y un uso, y elegir mal es la forma más rápida de tener un '
            'equipo de 25.000 dólares apagado en un rincón. Acá los ordenamos según cómo se usan en Argentina.</p>') +
            tarjetas(TIPOS_AR)),
        seccion(prosa(
            '<h2>Qué tipo de humanoide elegir según tu sector</h2>'
            '<h3>Industria automotriz y metalmecánica</h3><p>Humanoides <a href="/robot-industrial/">industriales</a> para abastecimiento de línea y '
            'manipulación. Encajan en plantas de Córdoba, Santa Fe y el conurbano bonaerense que no pueden reconvertir toda la línea.</p>'
            '<h3>Agroindustria, puertos y empaque</h3><p>Humanoides de <a href="/robots-de-logistica-y-almacen/">logística</a> e '
            '<a href="/robots-de-inspeccion-industrial/">inspección</a> para acopios, plantas de crushing del Gran Rosario y empaques de fruta del Alto Valle.</p>'
            '<h3>Energía y minería</h3><p>Humanoides de inspección para Vaca Muerta, refinerías y proyectos de litio en la Puna, donde la seguridad del personal es prioridad.</p>'
            '<h3>Salud</h3><p><a href="/robots-medicos/">Robots médicos</a> y de <a href="/robots-de-rehabilitacion/">rehabilitación</a> para hospitales y '
            'centros de kinesiología.</p>'
            '<h3>Educación</h3><p><a href="/robots-educativos/">Robots educativos</a> para escuelas técnicas y de <a href="/robots-de-investigacion/">investigación</a> '
            'para universidades y CONICET.</p>'
            '<h3>Comercio, servicios y eventos</h3><p>Humanoides de <a href="/robots-de-atencion-al-cliente/">atención al cliente</a> y '
            '<a href="/robots-para-eventos/">para eventos</a> en bancos, shoppings, concesionarias y ferias.</p>') +
            boton('/ar/precios/', 'Ver precios en Argentina'), alt=True),
        preguntas('Preguntas frecuentes sobre tipos de robots humanoides', faq),
    ]
    return pagina('tipos', '/tipos/', 'Tipos de Robots Humanoides', 'Tipos de Robots Humanoides',
                  'Tipos de Robots Humanoides y Usos en Argentina por Sector',
                  'Tipos de robots humanoides: industriales, de logística, inspección, atención al cliente, educativos y más. Cuál conviene según tu sector en Argentina.',
                  'Industriales, de logística, de inspección, educativos, médicos y de atención al público: qué <strong>tipo de robot humanoide</strong> conviene según tu sector.',
                  s, faq, focus='tipos de robots humanoides')


def precios():
    faq = [
        ('¿Cuál es el robot humanoide más barato en Argentina?', 'Los educativos chicos, desde unos 1.500 USD puestos en el país. Entre los humanoides de tamaño casi humano, el Unitree R1 es el más accesible: unos 5.900 USD en fábrica.'),
        ('¿Cuánto cuesta el Unitree G1 en Argentina?', 'Unos 16.000 USD en fábrica la versión básica. Puesto en Argentina, con flete, derechos, IVA, percepciones y despachante, la cuenta termina entre 23.000 y 28.000 USD. Las versiones EDU con manos diestras cuestan bastante más.'),
        ('¿Conviene traerlo por courier?', 'Solo si el valor del envío entra en el límite del régimen de courier vigente, que hoy es de 3.000 USD por envío. Eso deja afuera a la mayoría de los humanoides de tamaño completo, que van por importación formal con despachante.'),
        ('¿Las percepciones se recuperan?', 'Las percepciones de IVA y Ganancias que cobra la aduana son pagos a cuenta: una empresa inscripta las computa en sus declaraciones juradas. Un particular puede computar las de Ganancias si presenta esa declaración. Consultalo con tu contador.'),
        ('¿Hay alquiler de robots humanoides en Argentina?', 'Sí. Alquilamos humanoides para eventos por día, con técnico incluido, y para pruebas piloto por semanas o meses. El precio depende de la fecha, la ciudad y el modelo.'),
    ]
    s = [
        seccion(prosa(
            '<h2>Precios de robots humanoides en Argentina, modelo por modelo</h2>'
            '<p>Esta tabla compara el <strong>precio de fábrica</strong> de los humanoides que hoy se pueden comprar con una <strong>estimación del costo puesto en '
            'Argentina</strong>, con flete, impuestos y despacho incluidos. Es una referencia para presupuestar: el número final lo da la cotización del día.</p>') +
            tabla(['Modelo', 'Precio en fábrica', 'Puesto en Argentina (estimado)', '¿Se puede importar?'], [
                ['Noetix Bumi', 'menos de 1.400 USD', 'a confirmar', 'Anunciado, sin stock verificado'],
                ['Unitree R1', 'unos 5.900 USD', '8.500 – 10.500 USD', 'Sí'],
                ['Booster K1', 'consultar', 'a cotizar', 'Sí, bajo pedido'],
                ['Unitree G1', 'unos 16.000 USD', '23.000 – 28.000 USD', 'Sí, el más importado'],
                ['1X NEO', '20.000 USD o 499 USD/mes', 'no disponible', 'Solo Estados Unidos por ahora'],
                ['Tesla Optimus', 'no comercializado', 'no disponible', 'No'],
                ['Figure 03', 'no comercializado', 'no disponible', 'No'],
                ['Boston Dynamics Atlas', 'no se vende suelto', 'no disponible', 'No'],
            ], 'Valores orientativos de octubre de 2026, en dólares estadounidenses. Cambian con el tipo de cambio, el flete y la normativa aduanera.')),
        seccion(prosa(
            '<h2>Por qué un robot humanoide cuesta más en Argentina</h2>'
            '<p>Entre los 16.000 USD que marca Unitree para el G1 y lo que termina pagando una empresa argentina hay una diferencia grande. No es margen: es lo que '
            'cuesta traerlo. Estas son las partidas que se suman sobre el precio de fábrica:</p>' + COSTO_TOTAL +
            '<p>En total, el costo puesto en Argentina suele quedar <strong>entre un 40% y un 70% por encima del precio de fábrica</strong>. Una parte '
            '—las percepciones y, para empresas, el IVA— se recupera después como crédito fiscal, por eso conviene mirar el costo neto con tu contador.</p>'), alt=True),
        seccion(prosa(
            '<h2>Courier o importación formal</h2>'
            '<h3>Régimen de courier</h3><p>Sirve para envíos chicos: hoy el límite es de <strong>3.000 USD por envío</strong>. Un humanoide educativo o un '
            'repuesto entran; un G1 completo, no.</p>'
            '<h3>Importación formal con despachante</h3><p>Es la vía para cualquier humanoide de tamaño completo. Requiere un importador inscripto ante ARCA '
            '—tu empresa o nosotros— y un <strong>despachante de aduana</strong> que clasifique el equipo, liquide los tributos y lo libere. Es más trámite, '
            'pero el robot llega con factura, garantía y documentación en regla.</p>') +
            boton('/ar/comprar/', 'Cómo comprar paso a paso')),
        seccion(prosa(
            '<h2>Alquiler: la alternativa a comprar</h2>'
            '<p>Si el uso es puntual o querés probar antes de invertir, el <a href="/alquiler-de-robots-humanoides/">alquiler</a> evita inmovilizar dólares. '
            'Trabajamos dos modalidades:</p><ul>'
            '<li><strong>Eventos</strong>: por día, con técnico, guion de interacción y traslado. Ideal para ferias, lanzamientos y congresos.</li>'
            '<li><strong>Piloto</strong>: por semanas o meses, para probar el robot en tu operación real antes de decidir la compra.</li></ul>'), alt=True),
        seccion(prosa(
            '<h2>Costos que no aparecen en el precio</h2><ul>'
            '<li><strong>Capacitación</strong> del equipo que lo va a operar. Sin esto, el robot termina apagado.</li>'
            '<li><strong>Programación</strong> de la tarea concreta, que casi nunca viene resuelta de fábrica.</li>'
            '<li><strong>Repuestos</strong>, sobre todo actuadores: conviene tener stock porque importarlos de urgencia es caro y lento.</li>'
            '<li><strong>Mantenimiento</strong> preventivo según horas de uso.</li>'
            '<li><strong>Seguro</strong> del equipo, que en Argentina conviene contratar desde que sale de fábrica.</li></ul>'
            '<h3>Plazos de entrega reales</h3><ul>'
            '<li><strong>Modelos en stock en fábrica, por avión</strong>: de 4 a 6 semanas hasta tu ciudad.</li>'
            '<li><strong>Unitree G1 por encargo</strong>: unos 60 días de fabricación más el envío.</li>'
            '<li><strong>Por barco</strong>: sumá entre 6 y 8 semanas de tránsito, a cambio de un flete más barato.</li>'
            '<li><strong>Aduana</strong>: de unos días a varias semanas según el canal que asigne ARCA.</li></ul>') +
            boton('/ar/contacto/', 'Pedir presupuesto cerrado')),
        preguntas('Preguntas frecuentes sobre precios en Argentina', faq, alt=True),
    ]
    return pagina('precios', '/precios/', 'Precio de un Robot Humanoide en Argentina', 'Precio de un Robot Humanoide en Argentina',
                  'Precio de un Robot Humanoide en Argentina 2026 - Tabla en Dólares',
                  'Cuánto cuesta un robot humanoide en Argentina: precios en dólares de fábrica y puestos en el país, costos de importación, courier y alquiler.',
                  'El precio de fábrica es solo el principio. Acá tenés cuánto cuesta un <strong>robot humanoide puesto en Argentina</strong>, con flete, impuestos y despacho.',
                  s, faq, focus='precio robot humanoide Argentina')


def comprar():
    faq = [
        ('¿Necesito ser importador para comprar un robot humanoide?', 'No. Si comprás a través nuestro, nosotros hacemos la importación y te facturamos el robot puesto en Argentina. Si tu empresa ya está inscripta como importadora, también podemos hacer la operación a su nombre.'),
        ('¿Puedo comprarlo en Mercado Libre?', 'Muchas publicaciones de «robot humanoide» son juguetes o kits educativos. Si aparece un humanoide de tamaño completo, verificá quién lo importó, si tiene factura, garantía y soporte, y si los repuestos están disponibles en el país.'),
        ('¿Y si lo compro directo en AliExpress o en la web del fabricante?', 'Se puede, pero un humanoide completo supera el límite del courier y termina en importación formal igual. Además, sin un representante local la garantía implica mandar el equipo de vuelta a China.'),
        ('¿Qué documentación recibo?', 'Factura, despacho de importación, manual, garantía y la configuración inicial del robot. Para empresas, todo lo necesario para registrarlo como bien de uso.'),
    ]
    s = [
        seccion(duo(prosa(
            '<h2>Comprar un robot humanoide desde Argentina</h2>'
            '<p>Comprar un <strong>robot humanoide en Argentina</strong> implica casi siempre importarlo. No es complicado si se hace en orden, pero tiene '
            'decisiones que conviene tomar antes de pagar: qué modelo, por qué vía entra al país, quién lo despacha y quién da soporte después.</p>'
            '<h3>Las tres formas de comprar</h3><ul>'
            '<li><strong>Llave en mano con nosotros</strong>: elegimos el modelo con vos, lo importamos y te lo entregamos funcionando. Pagás un precio cerrado.</li>'
            '<li><strong>Importación a nombre de tu empresa</strong>: si ya sos importador inscripto, coordinamos proveedor, flete y despachante y la operación queda a tu nombre.</li>'
            '<li><strong>Courier</strong>: solo para modelos chicos o repuestos que entran en el límite de 3.000 USD por envío.</li></ul>'),
            U + 'comprar-robot-humanoides.webp', 'Comprar un robot humanoide desde Argentina')),
        seccion(prosa(
            '<h2>Paso a paso</h2><ol>'
            '<li><strong>Definí la tarea.</strong> Qué tiene que hacer el robot, dónde y cuántas horas por día. Con eso descartamos la mitad de los modelos.</li>'
            '<li><strong>Elegí el modelo.</strong> Te proponemos dos o tres opciones con precio puesto en Argentina. Ver <a href="/ar/tipos/">tipos</a> y <a href="/marcas/">marcas</a>.</li>'
            '<li><strong>Presupuesto cerrado.</strong> Robot, accesorios, flete, derechos, tasa de estadística, IVA, percepciones, despachante y entrega.</li>'
            '<li><strong>Seña y pedido a fábrica.</strong> Con la seña confirmamos el pedido y el plazo de fabricación.</li>'
            '<li><strong>Flete y despacho.</strong> El robot viaja asegurado; el <a href="/importacion-y-gestion-aduanera/">despacho</a> lo hace un despachante ante ARCA.</li>'
            '<li><strong>Entrega y puesta en marcha.</strong> Lo llevamos a tu ciudad, lo configuramos y capacitamos a quien lo va a usar.</li>'
            '<li><strong>Soporte.</strong> Asistencia remota, actualizaciones y <a href="/mantenimiento-y-reparacion-de-robot/">mantenimiento</a>.</li></ol>') +
            boton('/ar/contacto/', 'Empezar con una consulta'), alt=True),
        seccion(prosa(
            '<h2>Antes de comprar: lista de control</h2><ul>'
            '<li><strong>Energía</strong>: la mayoría de los humanoides chinos trabajan con 220 V y 50 Hz, como la red argentina. Verificamos cargador y enchufe.</li>'
            '<li><strong>Espacio</strong>: piso firme, sin desniveles grandes y con lugar para la estación de carga.</li>'
            '<li><strong>Conectividad</strong>: wifi estable si el robot usa servicios en la nube o control remoto.</li>'
            '<li><strong>Repuestos</strong>: preguntá qué stock local hay de actuadores, baterías y manos.</li>'
            '<li><strong>Software</strong>: si vas a programarlo, confirmá que el SDK y la documentación estén disponibles para tu versión.</li>'
            '<li><strong>Seguridad</strong>: si va a trabajar cerca de personas, definí zonas y protocolos antes de que llegue.</li></ul>'
            '<h3>Cuánto vas a pagar</h3><p>El detalle de cada costo y los precios por modelo están en <a href="/ar/precios/">precios en Argentina</a>.</p>')),
        seccion(prosa(
            '<h2>Comprar en tu ciudad</h2><p>Entregamos en todo el país. Guías por ciudad:</p>' + lista_ciudades()), alt=True),
        preguntas('Preguntas frecuentes sobre comprar un robot humanoide', faq),
    ]
    return pagina('comprar', '/comprar/', 'Comprar un Robot Humanoide en Argentina', 'Comprar un Robot Humanoide en Argentina',
                  'Comprar un Robot Humanoide en Argentina - Guía de Importación',
                  'Cómo comprar un robot humanoide desde Argentina: llave en mano, a nombre de tu empresa o por courier. Paso a paso, costos, plazos y qué revisar.',
                  'Cómo comprar e <strong>importar un robot humanoide</strong> desde Argentina sin sorpresas: vías, pasos, costos y qué revisar antes de pagar.',
                  s, faq, cta={'url': '/ar/contacto/', 'texto': 'Pedir presupuesto'}, focus='comprar robot humanoide Argentina')


def servicios():
    items = [
        ('venta-de-robots-humanoides', 'Venta de Robots Humanoides', 'Asesoramiento, elección del modelo y venta con precio cerrado puesto en Argentina.'),
        ('importacion-y-gestion-aduanera', 'Importación y Gestión Aduanera', 'Flete, seguro y despacho con despachante ante ARCA. Clasificación arancelaria y liquidación de tributos.'),
        ('programacion-de-robot-humanoides', 'Programación de Robots Humanoides', 'Desarrollo de la tarea concreta con el SDK del fabricante: navegación, manipulación, voz e integración.'),
        ('mantenimiento-y-reparacion-de-robot', 'Mantenimiento y Reparación', 'Soporte remoto, mantenimiento preventivo y gestión de repuestos originales para no depender de mandar el equipo a fábrica.'),
        ('alquiler-de-robots-humanoides', 'Alquiler de Robots Humanoides', 'Pruebas piloto por semanas o meses para validar el robot en tu operación antes de comprar.'),
        ('alquiler-para-eventos', 'Alquiler para Eventos', 'Humanoides para ferias, congresos y lanzamientos en todo el país, con técnico y guion.'),
        ('implementacion-de-robot-en-empresas-y-negocios', 'Implementación en Empresas', 'Integración con tus procesos, zonas de seguridad, capacitación del personal y medición de resultados.'),
        ('estudio-de-viabilidad-y-roi', 'Estudio de Viabilidad y ROI', 'Antes de invertir en dólares: si la tarea se puede automatizar hoy y en cuánto tiempo se paga el robot.'),
        ('renting-y-robot-como-servicio', 'Leasing y Robot como Servicio', 'Cuota mensual, leasing o pago por uso: qué existe de verdad en el país y qué mirar en el contrato.'),
        ('marcado-ce-y-normativa', 'Normativa y Certificaciones', 'Seguridad eléctrica, ENACOM, ANMAT, ART y datos personales: qué se activa según el equipo y el uso.'),
        ('formacion-y-cursos', 'Formación y Cursos', 'Capacitación online en horario de Argentina o presencial en tu empresa o universidad.'),
    ]
    s = [
        seccion(prosa(
            '<h2>Servicios para robots humanoides en Argentina</h2>'
            '<p>Un humanoide no termina en la compra. En Argentina, además, el servicio pesa más que en otros países: los repuestos tardan en llegar, el soporte '
            'del fabricante está del otro lado del mundo y cada importación tiene su trámite. Por eso cubrimos todo el ciclo, desde la elección hasta el mantenimiento.</p>') +
            tarjetas(items)),
        seccion(prosa(
            '<h2>Cómo trabajamos con empresas argentinas</h2><ol>'
            '<li><strong>Diagnóstico</strong>: visitamos o hacemos una videollamada para entender la tarea.</li>'
            '<li><strong>Propuesta</strong>: modelo, programación necesaria, capacitación y costo total en dólares.</li>'
            '<li><strong>Piloto</strong> cuando tiene sentido, con un equipo alquilado.</li>'
            '<li><strong>Implementación</strong>: importación, instalación, programación y capacitación.</li>'
            '<li><strong>Acompañamiento</strong>: soporte y mejoras a medida que el equipo aprende a usar el robot.</li></ol>'
            '<h3>Normativa y seguridad</h3><p>Antes de importar verificamos si el equipo requiere certificaciones o intervenciones de organismos argentinos '
            'y si su posición arancelaria tiene licencias o requisitos especiales. Para equipos que van a trabajar con personas definimos protocolos de seguridad '
            'en el lugar de trabajo.</p>') +
            boton('/ar/contacto/', 'Consultar un servicio'), alt=True),
    ]
    return pagina('servicios', '/servicios/', 'Servicios para Robots Humanoides en Argentina', 'Servicios para Robots Humanoides en Argentina',
                  'Servicios para Robots Humanoides en Argentina - Importación, Programación y Soporte',
                  'Venta, importación con despachante, programación, mantenimiento, alquiler y capacitación en robots humanoides para empresas e instituciones de Argentina.',
                  'Venta, <strong>importación</strong>, programación, mantenimiento y alquiler de robots humanoides para empresas e instituciones de toda Argentina.',
                  s, focus='servicios robots humanoides Argentina')


def cursos():
    items = [
        ('introduccion-a-la-robotica-humanoide', 'Introducción a la Robótica Humanoide', 'Para arrancar de cero: cómo funciona un humanoide, qué puede hacer hoy y cómo se opera con seguridad.'),
        ('programacion-con-sdk', 'Programación con SDK', 'Python y ROS 2 sobre el SDK del fabricante: movimiento, sensores y primeras tareas autónomas.'),
        ('operacion-y-mantenimiento', 'Operación y Mantenimiento', 'Para quien va a usar el robot todos los días: puesta en marcha, rutinas, fallas comunes y cuidado de baterías y actuadores.'),
        ('robotica-para-centros-educativos', 'Robótica para Centros Educativos', 'Para docentes de escuelas técnicas e institutos: cómo armar clases y proyectos con un humanoide.'),
        ('formacion-para-equipos-tecnicos', 'Formación para Equipos Técnicos', 'Programa a medida para el equipo de mantenimiento o ingeniería de tu empresa.'),
        ('vision-artificial-y-percepcion', 'Visión Artificial y Percepción', 'Cámaras de profundidad, LiDAR y modelos de visión para que el robot entienda su entorno.'),
        ('aprendizaje-por-imitacion', 'Aprendizaje por Imitación', 'Cómo enseñarle una tarea al robot mostrándosela, con teleoperación y datos de demostración.'),
        ('simulacion-antes-del-despliegue', 'Simulación antes del Despliegue', 'Probar en simulador antes de tocar el robot real: menos riesgo y menos horas de máquina.'),
        ('seguridad-y-robotica-colaborativa', 'Seguridad y Robótica Colaborativa', 'Zonas, protocolos y buenas prácticas para trabajar al lado de un humanoide.'),
        ('interaccion-por-voz-y-lenguaje', 'Voz y Lenguaje en Español Rioplatense', 'Reconocimiento con acento local, voseo y modelos de lenguaje con límites.'),
        ('manipulacion-y-agarre', 'Manipulación y Agarre', 'Pinzas, manos y control de fuerza con objetos reales.'),
        ('certificacion-profesional', 'Certificación Profesional', 'Recorrido completo con evaluación y proyecto final.'),
    ]
    faq = [
        ('¿Los cursos son en horario de Argentina?', 'Sí. Las clases online en vivo se dan en horario argentino y quedan grabadas para repasar.'),
        ('¿Necesito tener un robot para hacer el curso?', 'No para los cursos introductorios y de programación: trabajamos con simulador y demostraciones en vivo. Para operación y mantenimiento lo ideal es hacerlo sobre tu propio equipo.'),
        ('¿Dan cursos presenciales?', 'Sí, para grupos de empresas, universidades y escuelas técnicas en Buenos Aires, Córdoba, Rosario y otras ciudades, con el robot en la sala.'),
        ('¿Entregan certificado?', 'Sí, cada curso entrega un certificado de aprobación con la carga horaria y los contenidos.'),
    ]
    s = [
        seccion(prosa(
            '<h2>Cursos de robótica humanoide para Argentina</h2>'
            '<p>Un humanoide sin gente capacitada termina apagado. Nuestros <strong>cursos de robótica humanoide</strong> son prácticos y cortos, pensados para '
            'quien lo va a usar o programar. Se dictan <strong>online en vivo en horario de Argentina</strong> o presenciales para grupos de empresas, '
            'universidades y escuelas técnicas.</p>') + tarjetas(items)),
        seccion(prosa(
            '<h2>Para quién son</h2><ul>'
            '<li><strong>Empresas</strong> que incorporan un humanoide y necesitan que su equipo lo opere y mantenga.</li>'
            '<li><strong>Universidades e institutos</strong> que quieren sumar humanoides a sus carreras de electrónica, mecatrónica o computación.</li>'
            '<li><strong>Escuelas técnicas</strong> que buscan proyectos de robótica con equipos reales.</li>'
            '<li><strong>Profesionales y estudiantes</strong> que quieren especializarse en una tecnología con poca oferta de formación en el país.</li></ul>'
            '<h3>Dónde más formarte en Argentina</h3><p>Las carreras de ingeniería electrónica, mecatrónica y computación de la UBA, la UTN, la UNC, la UNLP, '
            'la UNR, la UNCuyo y el ITBA son la base. Nuestros cursos complementan esa formación con la práctica específica sobre humanoides. En cada '
            '<a href="/ar/">guía de ciudad</a> detallamos la oferta local.</p>') +
            boton('/ar/contacto/', 'Consultar fechas'), alt=True),
        preguntas('Preguntas frecuentes sobre los cursos', faq),
    ]
    return pagina('cursos', '/cursos/', 'Cursos de Robótica Humanoide en Argentina', 'Cursos de Robótica Humanoide en Argentina',
                  'Cursos de Robótica Humanoide en Argentina - Online y Presenciales',
                  'Cursos de robótica humanoide en Argentina: introducción, programación con SDK y ROS 2, operación y mantenimiento. Online en horario argentino o presenciales.',
                  '<strong>Cursos de robótica humanoide</strong> online en horario de Argentina o presenciales para empresas, universidades y escuelas técnicas.',
                  s, faq, focus='cursos robótica humanoide Argentina')


def contacto():
    s = [
        seccion(
            '<div class="contacto-datos"><div class="dato"><h3>Email</h3><p><a href="mailto:Contacto@robothumanoide.org">Contacto@robothumanoide.org</a></p></div>'
            '<div class="dato"><h3>Cobertura</h3><p>Todo el país: Buenos Aires, Córdoba, Rosario, Mendoza y el resto de las provincias.</p></div></div>'
            '<div class="contacto-cara"><div class="prosa"><h2>Escribinos</h2>'
            '<p>Cuanto más concreto seas, más útil va a ser la respuesta. Nos sirve saber <strong>para qué tarea</strong> lo necesitás, <strong>en qué ciudad</strong> '
            'va a trabajar, <strong>si comprás como empresa o particular</strong> y <strong>qué presupuesto en dólares</strong> manejás.</p>'
            '<h3>Qué pasa después</h3><ul>'
            '<li>Revisamos si hoy existe un robot que haga lo que necesitás. A veces la respuesta honesta es que todavía no.</li>'
            '<li>Si existe, te decimos qué modelos encajan y cuánto cuestan <strong>puestos en Argentina</strong>, con importación incluida.</li>'
            '<li>Te avisamos de los costos que no aparecen en el precio: flete, aduana, capacitación y mantenimiento.</li></ul></div>'
            '<div>{FORMULARIO}</div></div>'),
    ]
    return pagina('contacto', '/contacto/', 'Contacto - Robot Humanoide Argentina', 'Contacto',
                  'Contacto - Comprar o Alquilar un Robot Humanoide en Argentina',
                  'Consultanos para comprar, importar o alquilar un robot humanoide en Argentina. Te decimos qué modelo encaja, cuánto cuesta puesto en el país y en qué plazo.',
                  'Vendemos, importamos, alquilamos y damos soporte a <strong>robots humanoides</strong> en toda Argentina. Contanos qué necesitás.',
                  s, focus='contacto robot humanoide Argentina')


def main():
    os.makedirs(DESTINO, exist_ok=True)
    for f in (home, que_es, tipos, precios, comprar, servicios, cursos, contacto):
        p = f()
        with open(os.path.join(DESTINO, p['slug'] + '.json'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(p, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print(p['url'])


if __name__ == '__main__':
    main()
