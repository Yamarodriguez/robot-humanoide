# Adapta un texto de la versión española al español rioplatense para /ar/.
# 1) FRASES: lo que no vale en Argentina (euros, CE, España) se reescribe.
# 2) Voseo y vocabulario.
# 3) Lo que aún hable de España o de euros se descarta (es_de_espana).
import re

S = r'(?:</?strong>)*'

FRASES = [
    ('Marcado CE y Normativa para Robots', 'Normativa y Certificaciones para Robots'),
    # --- normativa
    ('requiere marcado CE si comparte espacio con operarios', 'requiere análisis de riesgos si comparte espacio con operarios'),
    ('necesita evaluación de riesgos y marcado CE', 'necesita análisis de riesgos y aviso a Higiene y Seguridad'),
    ('categoría especial del RGPD, con requisitos reforzados', 'datos sensibles para la Ley 25.326, con requisitos reforzados'),
    ('Son categoría especial en RGPD', 'Son datos sensibles para la Ley 25.326'),
    ('es categoría especial en RGPD', 'es dato sensible para la Ley 25.326'),
    ('deja claro que el marcado CE del fabricante no basta al integrar el robot', 'deja claro que la documentación del fabricante no alcanza al integrar el robot'),
    ('Certificación ATEX', 'Certificación para atmósferas explosivas'),
    ('certificación ATEX', 'certificación para atmósferas explosivas'),
    ('en atmósferas explosivas.', 'en refinerías y plantas químicas.'),
    ('pero comprueba antes', 'pero comprobá antes'),
    # --- Unitree G1
    ('el G1 cuesta unos 16.000 dólares en fábrica y 24.900 € con distribuidor en España', 'el G1 cuesta unos 16.000 dólares en fábrica y entre 23.000 y 28.000 puesto en Argentina'),
    ('en España se vende por 24.900 € a través de distribuidor', 'puesto en Argentina se estima entre 23.000 y 28.000 USD'),
    ('La diferencia son aranceles, IVA, transporte, garantía y soporte local', 'La diferencia son derechos, IVA, percepciones, flete y soporte'),
    ('unos 16.000 $ en fábrica, 24.900 € en España', 'unos 16.000 USD en fábrica, 23.000 a 28.000 USD puesto en Argentina'),
    ('del precio final en España', 'del precio final en Argentina'),
    ('16.000 $ en China no son 16.000 $ en tu puerta', '16.000 USD en China no son 16.000 USD en tu puerta'),
    ('Con aranceles, IVA y transporte, la cifra realista en España ronda los 24.900 €', 'Con derechos, IVA, percepciones y flete, la cifra realista en Argentina va de 23.000 a 28.000 USD'),
    ('Los distribuidores españoles trabajan con unos 60 días por riguroso orden de encargo', 'La fabricación por encargo ronda los 60 días, a los que se suman flete y aduana'),
    ('Comprar en AliExpress sale más barato y te deja sin garantía ni servicio técnico local', 'Comprar directo en una plataforma puede salir más barato y te deja sin garantía ni servicio técnico cercano'),
    ('un Unitree G1 por 24.900 €', 'un Unitree G1 por unos 16.000 USD en fábrica'),
    # --- Unitree R1, Booster, Bumi
    ('se mueven entre los 4.000 y los 8.900 €', 'arrancan en unos 5.900 USD en fábrica'),
    ('desde unos 3.700 €', 'desde unos 5.900 USD en fábrica'),
    ('Cuesta unos 3.700 € en fábrica y se vende directamente en AliExpress España. Por canal europeo con garantía, el R1 Basic aparece en torno a 8.853 €', 'Cuesta unos 5.900 USD en fábrica. Puesto en Argentina, con flete, impuestos y despacho, se estima entre 8.500 y 10.500 USD'),
    ('en fábrica en fábrica', 'en fábrica'),
    ('el mismo robot cuesta el doble según por dónde entre', 'el mismo robot cambia mucho de precio según por dónde entre'),
    ('AliExpress barato pero sin garantía', 'más barato en plataforma, pero sin garantía'),
    ('sin gastar 25.000 €', 'sin gastar 25.000 USD'),
    ('comprar en AliExpress sale más barato pero te deja sin garantía europea', 'comprar directo en una plataforma puede salir más barato pero te deja sin garantía local'),
    ('Comprar en AliExpress sale más barato y te deja sin red', 'Comprar directo en una plataforma te deja sin red'),
    ('Sin garantía europea, sin servicio técnico y con la aduana a tu cargo', 'Sin garantía local, sin servicio técnico y con la aduana a tu cargo'),
    ('bípedos</strong> más económicos de Europa', 'bípedos</strong> más económicos del mercado'),
    ('más económicos de Europa', 'más económicos del mercado'),
    ('más económicos del mercado europeo', 'más económicos del mercado'),
    ('edición GEEK por 6.646 €', 'edición GEEK de entrada, a cotizar puesta en Argentina'),
    ('A partir de varias unidades baja a 6.314 €, interesante para un aula completa', 'Por varias unidades suele haber mejor precio, interesante para un aula completa'),
    ('desde 6.646 €', 'de gama de entrada'),
    (', unos 1.200 €', ', menos de 1.400 USD'),
    (': unos 1.200 €', ': menos de 1.400 USD'),
    ('entre 20.000 y 30.000 €, y el G1 se mueve entre 16.000 y 30.000 según canal', 'entre 20.000 y 30.000 USD, y el G1 parte de 16.000 en fábrica'),
    ('sin distribución confirmada en España', 'sin distribución confirmada en Argentina'),
    ('no hay distribución confirmada en España', 'no hay distribución confirmada en Argentina'),
    ('que sí se pueden comprar en Europa', 'que sí se pueden importar'),
    # --- otras marcas
    ('Confirma cuál tiene para España o Argentina', 'Confirmá qué registro tiene en ANMAT'),
    ('Destaca por estar listado en una gran cadena española, algo poco habitual en el sector', 'Se destaca por estar listado en cadenas de electrónica de Europa, algo poco habitual en el sector'),
    ('compruébalo con tus derechos como comprador en España', 'comprobá cuál te cubre comprando desde Argentina'),
    ('Verifica recambios y marcado CE en Europa', 'Verificá repuestos y documentación para importar'),
    ('Proyectos europeos', 'Proyectos internacionales'),
    ('Fabricante y soporte en España; confirma alcance', 'Fabricante que responde en español; confirmá el alcance en Argentina'),
    ('que prefieren proveedor europeo', 'que prefieren un proveedor de habla hispana'),
    ('Usarlo en fábrica no significa venderlo en España', 'Usarlo en fábrica no significa venderlo en Argentina'),
    ('No incluye transporte, impuestos ni soporte europeo', 'No incluye flete, impuestos ni soporte en Argentina'),
    ('Equipos europeos', 'Equipos universitarios'),
    ('Comprueba servicio técnico europeo', 'Comprobá qué servicio técnico tenés desde Argentina'),
    ('que ya aparece en tiendas españolas', 'que ya aparece en tiendas europeas'),
    ('más barato, unos 1.200 €', 'más barato, menos de 1.400 USD'),
    ('Humanoide completo por 24.900 € en España, unos 16.000 dólares en fábrica', 'Humanoide completo por unos 16.000 dólares en fábrica, entre 23.000 y 28.000 puesto en Argentina'),
    ('Desarrollo y soporte desde Europa, sin la fricción aduanera de una importación extracomunitaria', 'Desarrollo y soporte desde Alemania; desde Argentina se importa como cualquier equipo extrazona'),
    ('Se vende en AliExpress España y ronda los 4.000 € de fábrica', 'Ronda los 5.900 USD de fábrica y entre 8.500 y 10.500 puesto en Argentina'),
    # --- comunes
    ('en España y Argentina', 'en Argentina'),
    ('fuera de España y Argentina', 'fuera de Argentina'),
    ('Transporte, aranceles y formación suman', 'Flete, derechos de importación y capacitación suman'),
    ('desde los <strong>1.200 €</strong> del Noetix Bumi hasta los <strong>24.900 €</strong> del Unitree G1 en España', 'desde menos de <strong>1.400 USD</strong> en origen del Noetix Bumi hasta los <strong>23.000 a 28.000 USD</strong> del Unitree G1 puesto en Argentina'),
    ('entre 1.200 y 8.900 €', 'el Unitree R1, entre 8.500 y 10.500 USD puesto en Argentina'),
    ('en torno a 24.900 € el Unitree G1', 'el Unitree G1, entre 23.000 y 28.000 USD puesto en Argentina'),
    ('desde unos 219 € al mes con mantenimiento incluido; ', 'a cotizar según plazo y modelo; como referencia internacional, '),
    ('desde unos 219 € al mes', 'a cotizar según plazo y modelo'),
    ('Desde unos 4.000 euros en los modelos de entrada hasta 24.900 euros el Unitree G1 con distribuidor en España', 'Desde unos 8.500 dólares en modelos de entrada puestos en Argentina hasta 23.000 a 28.000 el Unitree G1'),
    ('por debajo de los 20.000 euros', 'por debajo de los 20.000 dólares'),
    ('los 50.000 euros', 'los 50.000 dólares'),
    ('por menos de 5.000.', 'por unos 5.900 en fábrica.'),
    ('$1,000 USD', '1.000 USD'), ('$50,000 USD', '50.000 USD'),
    ('499 $/mes', '499 USD/mes'), ('8.500 $/mes', '8.500 USD/mes'),
    ('Contáctanos y te asesoramos.?', 'Escribinos y te asesoramos.'),
    ('incluye aranceles, transporte e instalación', 'incluye flete, derechos de importación e instalación'),
    ('Ver Mas', 'Ver más'), ('Tipos de robot - ver mas', 'Ver todos los tipos'), ('Mas Servicios', 'Más servicios'),
    ('Si necesitas un robot ahora', 'Si necesitás un robot ahora'),
    ('máster', 'maestría'),
]

IMP = {
    'Pide': 'Pedí', 'Define': 'Definí', 'Elige': 'Elegí', 'Compara': 'Compará', 'Comprueba': 'Comprobá', 'Mira': 'Mirá',
    'Calcula': 'Calculá', 'Confirma': 'Confirmá', 'Consulta': 'Consultá', 'Desconfía': 'Desconfiá', 'Decide': 'Decidí',
    'Empieza': 'Empezá', 'Exige': 'Exigí', 'Pregunta': 'Preguntá', 'Presupuesta': 'Presupuestá', 'Prueba': 'Probá',
    'Revisa': 'Revisá', 'Solicita': 'Solicitá', 'Verifica': 'Verificá', 'Cuenta': 'Contá', 'Recuerda': 'Recordá',
    'Distingue': 'Distinguí', 'Trata': 'Tratá', 'Prioriza': 'Priorizá', 'Descubre': 'Descubrí', 'Encuentra': 'Encontrá',
    'Conoce': 'Conocé', 'Acota': 'Acotá', 'Valora': 'Evaluá', 'Separa': 'Separá', 'Ten': 'Tené', 'Reserva': 'Reservá',
    'Trae': 'Traé', 'Contáctanos': 'Escribinos', 'Dinos': 'Decinos', 'Fórmate': 'Formate', 'Ponte': 'Ponete',
    'Pregúntalo': 'Preguntalo', 'Compruébalo': 'Comprobalo', 'Exígela': 'Exigila', 'Tenlo': 'Tenelo',
    'Pruébala': 'Probala', 'Pruébalo': 'Probalo', 'Resuélvelo': 'Resolvelo', 'Trátalo': 'Tratalo',
    'Consúltalo': 'Consultalo', 'Presupuéstalos': 'Presupuestalos', 'Cuéntalo': 'Contalo', 'Hazla': 'Hacela',
    'Indica': 'Indicá', 'Parte': 'Partí', 'Aprende primero': 'Aprendé primero', 'Plantéate': 'Planteate', 'Súmale': 'Sumale',
    'Contempla': 'Contemplá', 'Busca': 'Buscá', 'Asegura': 'Asegurá', 'Planifica': 'Planificá',
}
# En mayúscula y a principio de frase también pueden ser 3.ª persona o sustantivo.
NO_INICIO = {'Reserva': 'con ', 'Prueba': '(?:siempre|en|la) ', 'Trae': 'tu ', 'Decide': '(?:según|entre|cómo) ',
             'Parte': 'de ', 'Cuenta': '(?:con|el) ', 'Empieza': '(?:por|en) ', 'Recuerda': 'que ', 'Busca': 'un '}
VERBOS = {
    'tienes': 'tenés', 'puedes': 'podés', 'quieres': 'querés', 'necesitas': 'necesitás', 'compras': 'comprás',
    'usas': 'usás', 'buscas': 'buscás', 'dependes': 'dependés', 'asumes': 'asumís', 'integras': 'integrás',
    'traes': 'traés', 'prefieres': 'preferís', 'compites': 'competís', 'tardas': 'tardás', 'pagas': 'pagás',
    'superas': 'superás', 'debes': 'debés', 'sabes': 'sabés', 'eres': 'sos', 'haces': 'hacés', 'puedas': 'puedas',
    'contigo': 'con vos', 'para ti': 'para vos', 'tú': 'vos', 'ganas menos': 'ganás menos',
}
VOCAB = [
    ('ordenador', 'computadora'), ('vídeo', 'video'), ('recambio', 'repuesto'), ('costes', 'costos'), ('coste', 'costo'),
    ('estand', 'stand'), ('profesorado', 'cuerpo docente'), ('centros educativos', 'escuelas e institutos'),
    ('centro educativo', 'instituto educativo'), ('móviles inteligentes', 'celulares'), ('teléfono móvil', 'celular'),
    ('hostelería', 'gastronomía'), ('sanitario', 'de salud'), ('asequible', 'accesible'), ('asequibles', 'accesibles'),
    ('asistencia sanitaria', 'atención de la salud'), ('coches', 'autos'), ('coche', 'auto'), ('vale la pena', 'conviene'),
    ('residencias de mayores', 'residencias para adultos mayores'), ('personas mayores', 'adultos mayores'),
    ('a día de hoy', 'al día de hoy'), ('robot camarero', 'robot mozo'), ('Robot Camarero', 'Robot Mozo'),
    ('robots camarero', 'robots mozo'), ('al camarero', 'al mozo'), ('camareros', 'mozos'), ('camarero', 'mozo'),
    ('renting', 'leasing'), ('Renting', 'Leasing'), ('nave industrial', 'planta industrial'), ('fallos', 'fallas'),
    ('formación', 'capacitación'), ('Formación', 'Capacitación'), ('en Europa', 'en el exterior'),
]

PROHIBIDO = re.compile(r'€|\beuros?\b|Españ|español(?:a|as|es)\b|\bCE\b|RGPD|AliExpress|\bUE\b|Unión Europea|comunitari|\bFP\b|FUNDAE|MediaMarkt|AEPD|Ley 5/2014|\bDUA\b|\bEORI\b|europeo|marcado', re.I)
PROHIBIDO_CS = re.compile(r'\bCE\b|\bUE\b|\bFP\b')


def es_de_espana(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    for p in (r'€', r'\b[Ee]uros?\b', 'Españ', r'\bespañol(?:a|as|es)\b', r'\bCE\b', 'RGPD', 'AliExpress', r'\bUE\b', 'Unión Europea',
              'comunitari', r'\bFP\b', 'FUNDAE', 'MediaMarkt', 'Ley 5/2014', r'\bDUA\b', 'EORI', r'\beurope[oa]s?\b', 'ATEX'):
        if re.search(p, t):
            return True
    return False


def _imperativo(m):
    intro, resto = m.group(1), m.group(2)
    for k, v in IMP.items():
        resto = re.sub(rf'(?<=[,;] )({S}){k.lower()}\b', lambda x: x.group(1) + v.lower(), resto)
        resto = re.sub(rf'(?<= [yo] )({S}){k.lower()}\b(?! de )', lambda x: x.group(1) + v.lower(), resto)
    return intro + resto


def argentino(t):
    for a, b in FRASES:
        t = t.replace(a, b)
    # Imperativos dentro de «Antes de…, pide», «Con…, mira», «Si…, usa»
    t = re.sub(r'((?:^|[.>] ?)(?:Antes|Con|Al|Para|Si|Entre|En un|Sin)\b)((?:(?!</p>|</li>|\. ).)*)', _imperativo, t)
    t = re.sub(r'(; )(pide|comprueba|compara|usa|confirma|solicita|consulta)\b',
               lambda m: m[1] + {'usa': 'usá'}.get(m[2], IMP.get(m[2].capitalize(), m[2]).lower()), t)
    t = re.sub(r'(define primero la tarea, )elige( .*?, )pide( .*? y )comprueba', r'definí primero la tarea, elegí\2pedí\3comprobá', t)
    for k, v in IMP.items():
        sig = NO_INICIO.get(k)
        patron = rf'((?:^|[.>:?!] ?|— ?){S}){k}\b' + (f'(?={S} {sig})' if sig else '')
        t = re.sub(patron, lambda m: m.group(1) + v, t)
    for k in ('pregúntalo', 'compruébalo', 'exígela', 'tenlo', 'pruébala', 'pruébalo', 'resuélvelo', 'trátalo', 'consúltalo',
              'presupuéstalos', 'cuéntalo', 'hazla', 'contáctanos', 'dinos', 'ponte', 'plantéate', 'súmale'):
        t = re.sub(rf'\b{k}\b', IMP[k.capitalize()].lower(), t)
    t = re.sub(r'\bdescubre cómo\b', 'descubrí cómo', t)
    t = re.sub(r'\bve directo\b', 'andá directo', t)
    t = re.sub(r'\bapuntarte\b', 'anotarte', t)
    for k, v in VERBOS.items():
        t = re.sub(rf'\b{k}\b', v, t)
        t = re.sub(rf'\b{k.capitalize()}\b', v.capitalize(), t)
    # Vocabulario solo en el texto visible: ni rutas ni identificadores.
    partes = re.split(r'(<[^>]+>|\]\([^)]*\))', t)
    for i in range(0, len(partes), 2):
        for a, b in VOCAB:
            partes[i] = re.sub(rf'\b{a}(s?)\b', rf'{b}\1', partes[i]) if a[-1] != 's' else re.sub(rf'\b{a}\b', b, partes[i])
            if a[0].islower():
                partes[i] = re.sub(rf'\b{a.capitalize()}(s?)\b', rf'{b.capitalize()}\1', partes[i])
    t = ''.join(partes)
    t = t.replace('computadora embarcad', 'computadora embarcad')
    for a, b in (('el computadora', 'la computadora'), ('un computadora', 'una computadora'), ('Los fallas', 'Las fallas'),
                 ('los fallas', 'las fallas'), ('fallas habituales', 'fallas habituales'), ('del cuerpo docente', 'del cuerpo docente'),
                 ('para salud de salud', 'para salud'), ('Robots Mozo', 'Robots Mozo')):
        t = t.replace(a, b)
    return t


def depurar(html):
    """Quita los <li>, <p>, filas o frases que sigan siendo de España."""
    quitado = []

    def f(m):
        if es_de_espana(m.group(0)):
            # Primero intenta salvar el resto del párrafo frase a frase.
            etiq = m.group(1)
            frases = re.split(r'(?<=[.!?]) (?=[A-ZÁÉÍÓÚ¿<])', m.group(2))
            ok = [x for x in frases if not es_de_espana(x)]
            quitado.extend(x for x in frases if es_de_espana(x))
            texto = ' '.join(ok)
            bien = texto.count('<strong>') == texto.count('</strong>')
            return f'<{etiq}>{texto}</{etiq}>' if bien and re.sub(r'<[^>]+>|\W', '', texto) else ''
        return m.group(0)
    html = re.sub(r'<(p|li)>(.*?)</\1>', f, html, flags=re.S)
    html = re.sub(r'<(?:ul|ol)></(?:ul|ol)>', '', html)
    return html, quitado
