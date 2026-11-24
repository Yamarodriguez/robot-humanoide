# Añade marcas y modelos nuevos al sitio (España y la lista que usa /ar/).
# Se puede ejecutar varias veces: no duplica.
#
#   python agregar_marcas.py
#   python generar_fichas_ar.py      (textos argentinos en contenido-ar/marcas.txt)
#   python generar_refuerzo.py       (resumen y preguntas de España)
import json
import os
import re

RAIZ = os.path.dirname(os.path.abspath(__file__))
NOTA = 'Datos consultados en noviembre de 2026. Confirma antes de decidir.'

# slug, nombre, título, descripción, tarjeta, color,
# precio (origen, España, ¿se compra?, plazo), ficha,
# qué es, qué hace, para quién, a tener en cuenta
M = [
 ('agibot-x2', 'AgiBot X2', 'AgiBot X2 - Precio en España, Medidas y Versiones',
  'AgiBot X2 en España: 25.699 € en MediaMarkt, 1,31 m y 35 kg. Diferencias con el X2 Ultra, para qué sirve y qué comprobar.',
  'Humanoide compacto de 1,31 m que ya aparece en tiendas españolas. Pensado para espectáculo, comercio y desarrollo según la versión.', '#f97316',
  ('más de 20.000 $', '25.699 € (MediaMarkt, consultado en 2026)', 'Sí, en tienda online', 'Según existencias'),
  [['Altura', '1,31 m'], ['Peso', '35 kg (39 kg el Ultra)'], ['Grados de libertad', '25 el X2 base, 30 el Ultra'], ['Conectividad', 'Wi-Fi, Bluetooth, USB y RJ45'], ['Autonomía', 'no confirmada']],
  'El <strong>AgiBot X2</strong> es un humanoide compacto de la empresa china AgiBot. Destaca por estar listado en una gran cadena española, algo poco habitual en el sector.',
  'Camina, gesticula y ejecuta rutinas de baile. El fabricante lo orienta a entretenimiento y espacios comerciales; las versiones superiores abren más posibilidades de desarrollo.',
  ['<strong>Comercios y marcas</strong> que buscan una presencia interactiva.', '<strong>Empresas de eventos</strong> que necesitan coreografías.', '<strong>Equipos técnicos</strong>, si la edición incluye acceso al SDK.'],
  ['<strong>Versión.</strong> Base, Lite y Ultra no son iguales; pide la referencia exacta.', '<strong>Garantía.</strong> Un distribuidor indica 8 meses para Lite y 18 para Ultra: compruébalo con tus derechos como comprador en España.', '<strong>Batería.</strong> Pide autonomía por escrito.']),
 ('unitree-h2', 'Unitree H2', 'Unitree H2 - Altura, Peso, Precio y Diferencias con el G1',
  'Unitree H2: humanoide de 1,82 m, 70 kg y 31 grados de libertad. Qué se sabe de su precio y en qué se diferencia del G1.',
  'El humanoide de tamaño adulto de Unitree: 1,82 m, unos 70 kg y 31 grados de libertad. Precio por consulta y entregas por fases.', '#38bdf8',
  ('A consultar; terceros citan desde 29.900 $', 'A consultar', 'Bajo pedido', 'Por fases'),
  [['Altura', '1,82 m'], ['Peso', 'unos 70 kg con batería'], ['Grados de libertad', '31'], ['Piernas', '6 por pierna'], ['Brazos', '7 por brazo'], ['Cintura y cabeza', '3 y 2']],
  'El <strong>Unitree H2</strong> es el hermano de tamaño humano del G1. Su estatura lo acerca a encimeras, puertas y puestos reales, pero también aumenta energía y riesgo al caer.',
  'Baila, camina y mueve el tronco con soltura. La edición EDU se dirige a desarrollo; las demostraciones no equivalen a una tarea de trabajo autónoma.',
  ['<strong>Centros de investigación</strong> que necesitan escala humana.', '<strong>Industria</strong> con un proyecto de integración.', '<strong>Escenarios profesionales</strong> con perímetro.'],
  ['<strong>Precio.</strong> La web oficial remite a ventas y los revendedores publican cifras muy distintas.', '<strong>Seguridad.</strong> Setenta kilos a esa altura exigen soporte y formación.', '<strong>Manos.</strong> Confirma si van incluidas.']),
 ('engineai-pm01', 'EngineAI PM01', 'EngineAI PM01 - Precio, Peso y Edición EDU',
  'EngineAI PM01: humanoide ágil de unos 1,4 m y 40 kg, lanzado por unos 12.000 dólares. Qué comprobar antes de pedirlo.',
  'Humanoide ágil de unos 40 kg, lanzado por 88.000 yuanes. Versión comercial y educativa para desarrollo.', '#22c55e',
  ('88.000 yuanes en el lanzamiento, unos 12.000 $', 'A consultar', 'Bajo pedido', 'A consultar'),
  [['Altura', 'unos 1,38–1,40 m'], ['Peso', '40–42 kg según fuente'], ['Cintura', 'giro de hasta 320°'], ['Ediciones', 'comercial y EDU']],
  'El <strong>EngineAI PM01</strong> es un humanoide de la firma de Shenzhen EngineAI que compite por precio y agilidad con el G1.',
  'Camina con marcha natural y gira ampliamente la cintura. La edición educativa se plantea para experimentar control y comportamiento.',
  ['<strong>Universidades</strong> que comparan plataformas de coste medio.', '<strong>Desarrolladores</strong> de locomoción.', '<strong>Demostraciones</strong> con operador.'],
  ['<strong>Oferta de lanzamiento.</strong> El precio difundido correspondía a 2025; pide uno actual.', '<strong>Soporte.</strong> Verifica recambios y marcado CE en Europa.', '<strong>Comunidad.</strong> Es menor que la de Unitree.']),
 ('engineai-t800', 'EngineAI T800', 'EngineAI T800 - Humanoide de 1,73 m: Precio y Datos',
  'EngineAI T800: humanoide de 1,73 m con batería extraíble y 4 a 5 horas declaradas. Qué se sabe del precio y del uso real.',
  'Humanoide de 1,73 m con batería intercambiable. Lanzado en China desde 180.000 yuanes; precio actual no publicado.', '#ef4444',
  ('180.000 yuanes en el lanzamiento', 'A consultar', 'Bajo pedido', 'A consultar'),
  [['Altura', '1,73 m'], ['Autonomía declarada', '4–5 horas'], ['Batería', 'modular, extraíble, 72 V'], ['Par máximo declarado', '450 Nm'], ['Peso', 'no confirmado']],
  'El <strong>EngineAI T800</strong> es un humanoide de tamaño adulto conocido por sus vídeos de combate. El nombre recuerda al cine; la máquina es una plataforma de robótica.',
  'Realiza movimientos dinámicos con motores de alto par y permite cambiar la batería. Su autonomía procede del fabricante y debe medirse en tu tarea.',
  ['<strong>Laboratorios</strong> de movimiento de alto par.', '<strong>Espectáculos</strong> diseñados por profesionales.', '<strong>Integradores</strong> que negocian con fábrica.'],
  ['<strong>Precio retirado.</strong> La cifra inicial no es una tarifa vigente.', '<strong>Fuerza.</strong> No se usa cerca del público sin barreras.', '<strong>Vídeos.</strong> Pide una prueba sin montaje.']),
 ('pal-robotics-talos', 'PAL Robotics TALOS', 'TALOS de PAL Robotics - Humanoide Fabricado en Barcelona',
  'TALOS, humanoide de investigación de PAL Robotics en Barcelona: 1,75 m, 95 kg, 32 grados de libertad, ROS y 6 kg por brazo.',
  'Humanoide de investigación de la empresa barcelonesa PAL Robotics: 1,75 m, control de par y ROS.', '#eab308',
  ('A consultar', 'A consultar con PAL Robotics', 'Sí, por proyecto', 'A consultar'),
  [['Altura', '1,75 m'], ['Peso', '95–100 kg según fuente'], ['Grados de libertad', '32'], ['Carga', '6 kg por brazo'], ['Software', 'ROS'], ['Fabricante', 'PAL Robotics, Barcelona']],
  '<strong>TALOS</strong> es el humanoide de investigación de PAL Robotics, empresa de Barcelona que desarrolla bípedos desde 2004.',
  'Ofrece control de par en la mayoría de sus articulaciones y modelo de simulación, dos piezas clave para investigar equilibrio, contacto y manipulación.',
  ['<strong>Universidades y centros tecnológicos</strong>.', '<strong>Proyectos europeos</strong> con varios socios.', '<strong>Grupos de control</strong> de cuerpo completo.'],
  ['<strong>Escala.</strong> Necesita espacio y equipo técnico.', '<strong>Presupuesto.</strong> Es una plataforma de investigación, no de consumo.', '<strong>Ventaja.</strong> Fabricante y soporte en España; confirma alcance.']),
 ('pal-robotics-kangaroo', 'PAL Robotics Kangaroo', 'Kangaroo de PAL Robotics - Robot Bípedo Español',
  'Kangaroo, robot bípedo de PAL Robotics: 1,60 m, 40 kg y seis horas declaradas. Para qué sirve y diferencias con TALOS.',
  'Bípedo español para investigar marcha y saltos: 1,60 m, 40 kg y hasta 6 horas de batería declaradas.', '#a855f7',
  ('A consultar', 'A consultar con PAL Robotics', 'Sí, por proyecto', 'A consultar'),
  [['Altura', '1,60 m'], ['Peso', '40 kg'], ['Piernas', '6 grados de libertad cada una'], ['Autonomía declarada', '6 horas'], ['Software', 'Linux y ROS'], ['Versión superior', 'Kangaroo Pro']],
  '<strong>Kangaroo</strong> concentra la ingeniería de PAL Robotics en piernas ligeras para movimiento dinámico. También existe Kangaroo Pro.',
  'Sus actuadores lineales y masa baja en la pierna facilitan investigar marcha, impacto y salto.',
  ['<strong>Laboratorios de locomoción</strong>.', '<strong>Doctorados</strong> en control y aprendizaje.', '<strong>Centros</strong> que prefieren proveedor europeo.'],
  ['<strong>No es un asistente.</strong> El objetivo principal son las piernas.', '<strong>Configuración.</strong> Los datos cambian entre estándar y Pro.', '<strong>TALOS o Kangaroo.</strong> Decide entre cuerpo completo o dinámica.']),
 ('apptronik-apollo', 'Apptronik Apollo', 'Apptronik Apollo - Datos, Mercedes-Benz y Disponibilidad',
  'Apollo de Apptronik: humanoide industrial probado por Mercedes-Benz. Especificaciones difundidas, Apollo 2 y por qué no se vende suelto.',
  'Humanoide industrial estadounidense, en pruebas con Mercedes-Benz. Sin venta abierta al público.', '#64748b',
  ('No publicado', 'No disponible', 'No, proyectos empresariales', 'Sin fecha pública'),
  [['Altura', 'unos 1,73 m'], ['Peso', 'unos 72,5 kg'], ['Carga difundida', '25 kg'], ['Pruebas', 'plantas de Mercedes-Benz'], ['Generación posterior', 'Apollo 2']],
  '<strong>Apollo</strong> es el humanoide industrial de Apptronik, empresa de Texas con Mercedes-Benz entre sus inversores.',
  'Se prueba en movimiento de componentes y tareas de planta. Las cifras de la ficha corresponden a la versión divulgada antes de Apollo 2.',
  ['<strong>Grandes fabricantes</strong> con proyecto conjunto.', '<strong>Logística</strong> con volumen y equipo propio.', 'No para particulares ni compra unitaria.'],
  ['<strong>Piloto no es catálogo.</strong> Usarlo en fábrica no significa venderlo en España.', '<strong>Versiones.</strong> No mezcles datos de Apollo y Apollo 2.', '<strong>Alternativa.</strong> Prueba la tarea con un equipo accesible.']),
 ('xpeng-iron', 'XPeng IRON', 'XPeng IRON - Fecha en Europa, Producción y Datos',
  'XPeng IRON: humanoide con 76 grados de libertad anunciados. Producción a finales de 2026, entregas en 2027 y planes para Europa.',
  'El humanoide del fabricante de coches XPeng: 76 grados de libertad anunciados y entregas previstas desde 2027.', '#14b8a6',
  ('No publicado', 'No disponible todavía', 'No', 'Entregas previstas desde 2027'),
  [['Grados de libertad', '76 anunciados'], ['Cómputo', 'tres chips Turing'], ['Producción masiva', 'prevista para finales de 2026'], ['Europa', 'promoción prevista en el segundo semestre de 2027'], ['Precio', 'no publicado']],
  '<strong>IRON</strong> es el humanoide de XPeng, marca china de vehículos eléctricos, que aplica parte de su tecnología de visión y chips.',
  'Se plantea primero en tiendas y campus de la propia compañía, con recepción y tareas acotadas.',
  ['<strong>Empresas</strong> que vigilan el mercado de servicio.', '<strong>Retail</strong> con proyectos a futuro.', 'No para una compra inmediata.'],
  ['<strong>Calendario.</strong> Son planes de la empresa, no una fecha garantizada.', '<strong>Precio.</strong> No existe una tarifa pública fiable.', '<strong>Modelo final.</strong> La unidad comercial puede cambiar.']),
 ('fourier-gr-3', 'Fourier GR-3', 'Fourier GR-3 - Robot de Cuidado: Datos y Precio',
  'Fourier GR-3: humanoide social de 1,65 m y 71 kg con hasta 55 grados de libertad. Diferencias con GR-2 y cautelas.',
  'Humanoide orientado a compañía y cuidado: 1,65 m, 71 kg y acabado blando. Precio por consulta.', '#f472b6',
  ('A consultar', 'A consultar', 'Bajo pedido', 'A consultar'),
  [['Altura', '1,65 m'], ['Peso', '71 kg'], ['Grados de libertad', 'hasta 55'], ['Interacción', 'visión, audio y tacto'], ['Presentación', 'agosto de 2025']],
  'El <strong>Fourier GR-3</strong> es la propuesta social de Fourier, presentada como robot de cuidado con apariencia más cercana que la gama industrial.',
  'Combina visión, voz y tacto para interactuar. «Cuidado» describe su enfoque social y no demuestra una función sanitaria certificada.',
  ['<strong>Investigación</strong> en interacción con personas.', '<strong>Centros de mayores</strong> en piloto supervisado.', '<strong>Museos y recepción</strong>.'],
  ['<strong>Certificación.</strong> Exígela si se usa con fin clínico.', '<strong>Peso.</strong> Setenta y un kilos no son un peluche.', '<strong>Precio.</strong> Las cifras de terceros no están verificadas.']),
 ('limx-oli', 'LimX Oli', 'LimX Oli - Precio, Versiones EDU y Especificaciones',
  'LimX Oli: humanoide modular de 1,65 m, menos de 55 kg y 31 grados de libertad. Versiones Lite, EDU y Super y precio en China.',
  'Humanoide modular de 1,65 m desde 158.000 yuanes en China, con versiones Lite, EDU y Super.', '#84cc16',
  ('158.000 yuanes, unos 21.800 $ en el lanzamiento', 'A consultar', 'Bajo pedido; versión global por confirmar', 'A consultar'),
  [['Altura', '1,65 m'], ['Peso', 'menos de 55 kg con batería'], ['Grados de libertad', '31 sin manos'], ['Versiones', 'Lite, EDU y Super'], ['Diseño', 'modular']],
  '<strong>LimX Oli</strong> es un humanoide de tamaño medio con arquitectura modular, dirigido a quien quiere desarrollar sobre él.',
  'Permite estudiar marcha y movimiento de cuerpo completo y adaptar extremos. Las capacidades abiertas varían por edición.',
  ['<strong>Laboratorios</strong> que necesitan más altura que un G1.', '<strong>Integradores</strong> de manos o sensores.', '<strong>Universidades</strong> con apoyo de importación.'],
  ['<strong>Precio chino.</strong> No incluye transporte, impuestos ni soporte europeo.', '<strong>Edición.</strong> Lite y EDU no dan el mismo acceso.', '<strong>Manos.</strong> Los 31 grados no las cuentan.']),
 ('reachy-2', 'Reachy 2', 'Reachy 2 - Humanoide Abierto Europeo: Precio y Uso',
  'Reachy 2 de Pollen Robotics y Hugging Face: humanoide abierto con ROS 2 y Python, unos 70.000 dólares. Qué incluye y para quién es.',
  'Robot abierto de Pollen Robotics y Hugging Face para manipulación e IA. Sobre 70.000 dólares.', '#fb7185',
  ('unos 70.000 $', 'A consultar', 'Sí, para investigación', 'A consultar'),
  [['Tipo', 'torso con dos brazos y base móvil, según versión'], ['Software', 'ROS 2 y SDK de Python'], ['Código', 'abierto'], ['Origen', 'Pollen Robotics, Francia'], ['Propietario', 'Hugging Face']],
  '<strong>Reachy 2</strong> es un robot humanoide de torso, brazos y base con ruedas creado por la francesa Pollen Robotics, adquirida por Hugging Face.',
  'Está pensado para manipulación, teleoperación y aprendizaje con herramientas abiertas. No camina: usa base móvil o configuración fija.',
  ['<strong>Laboratorios de IA</strong> y manipulación.', '<strong>Universidades</strong> que valoran código abierto.', '<strong>Equipos europeos</strong> de investigación.'],
  ['<strong>Configuración.</strong> Uno o dos brazos y base cambian precio y uso.', '<strong>No es doméstico.</strong> Se orienta a laboratorio.', '<strong>Código abierto</strong> no significa puesta en marcha sin trabajo.']),
 ('reachy-mini', 'Reachy Mini', 'Reachy Mini - Precio, Versiones y Robot de Escritorio con IA',
  'Reachy Mini: robot de escritorio abierto desde 399 dólares más impuestos y envío. Versiones, usos y por qué no es un humanoide completo.',
  'Robot expresivo de escritorio para aprender IA, desde 399 dólares más impuestos y envío. No camina ni tiene brazos.', '#facc15',
  ('399 $ Lite y 499 $ estándar, sin impuestos ni envío', 'Se suman IVA, envío y posibles aranceles', 'Sí, online', 'unos 90 días según el fabricante'),
  [['Formato', 'cabeza expresiva de escritorio'], ['Código', 'abierto'], ['Versiones', 'Lite y estándar'], ['Orientación', 'IA, voz y educación'], ['Estado', 'fase temprana de desarrollo']],
  '<strong>Reachy Mini</strong> es un robot pequeño de Hugging Face y Pollen Robotics. Tiene rasgos expresivos, pero no es un humanoide de cuerpo completo; lo incluimos como puerta de entrada.',
  'Sirve para programar gestos, voz y modelos de IA sin el coste ni el riesgo de un bípedo.',
  ['<strong>Estudiantes y aficionados</strong>.', '<strong>Docentes</strong> de IA y Python.', '<strong>Desarrolladores</strong> que prueban interacción.'],
  ['<strong>Lite.</strong> Comprueba qué ordenador y alimentación necesita.', '<strong>Coste final.</strong> Impuestos y envío van aparte.', '<strong>Límite.</strong> No camina ni manipula objetos.']),
 ('hexagon-aeon', 'Hexagon AEON', 'Hexagon AEON - El Humanoide de BMW en Leipzig',
  'AEON, humanoide industrial de Hexagon probado por BMW en Leipzig. Qué tareas hace, estado en 2026 y disponibilidad.',
  'Humanoide industrial europeo de Hexagon, en uso piloto en la planta de BMW en Leipzig.', '#06b6d4',
  ('No publicado', 'Por proyecto', 'No como venta unitaria', 'Según proyecto'),
  [['Fabricante', 'Hexagon Robotics, Zúrich'], ['Presentación', 'junio de 2025'], ['Planta', 'BMW Leipzig'], ['Tareas', 'baterías y componentes'], ['Otros socios', 'Pilatus y Schaeffler']],
  '<strong>AEON</strong> es el humanoide de Hexagon Robotics, vinculado a un grupo especializado en medición y captura de datos industriales.',
  'BMW lo introdujo en Leipzig para tareas de baterías y componentes. La compañía comunicó en junio de 2026 que ya realizaba tareas de producción.',
  ['<strong>Automoción y aeronáutica</strong>.', '<strong>Plantas</strong> con inspección y datos 3D.', '<strong>Proyectos europeos</strong> con volumen.'],
  ['<strong>Contrato.</strong> No hay precio de catálogo.', '<strong>Seguridad.</strong> La integración pesa tanto como el robot.', '<strong>Resultados.</strong> Pide métricas de tu tarea, no solo del piloto de BMW.']),
 ('engineered-arts-ameca', 'Ameca', 'Ameca de Engineered Arts - Qué Es, Precio y Alquiler',
  'Ameca, robot humanoide de expresiones faciales de Engineered Arts. Qué hace, por qué no camina y qué se sabe de precio y alquiler.',
  'El robot británico conocido por sus expresiones. Pensado para museos, investigación y eventos; no camina.', '#94a3b8',
  ('A consultar; estimaciones externas muy dispares', 'A consultar', 'Por contrato', 'A consultar'),
  [['Fabricante', 'Engineered Arts, Reino Unido'], ['Altura', '1,80–1,87 m según fuente'], ['Peso', 'fuentes contradictorias'], ['Especialidad', 'expresión facial y conversación'], ['Software', 'Tritium']],
  '<strong>Ameca</strong> es un humanoide de interacción famoso por sus gestos faciales. Es más comparable a Sophia que a un robot de almacén.',
  'Mira, gesticula y conversa al conectarse con modelos de lenguaje. Se instala en un punto y no se usa para cargar o caminar.',
  ['<strong>Museos y centros de ciencia</strong>.', '<strong>Congresos</strong> con presupuesto técnico.', '<strong>Investigación</strong> de comunicación.'],
  ['<strong>No es consciente.</strong> Sus gestos no prueban emociones.', '<strong>Precio.</strong> No hay tarifa oficial verificable.', '<strong>Instalación.</strong> Requiere transporte y soporte especializado.']),
 ('kepler-k2', 'Kepler K2 Bumblebee', 'Kepler K2 Bumblebee - Humanoide Industrial: Precio y Datos',
  'Kepler K2 Bumblebee: humanoide industrial de 1,75 m y 75 kg con un precio base comunicado de 30.000 dólares en 2025.',
  'Humanoide industrial de 1,75 m y 75 kg. Precio base comunicado de 30.000 dólares en 2025.', '#f59e0b',
  ('30.000 $ comunicado en 2025', 'A consultar', 'Bajo pedido', 'A consultar'),
  [['Altura', '1,75 m'], ['Peso', '75 kg'], ['Manos', '11 grados de libertad cada una'], ['Tacto', '25 puntos de fuerza por dedo'], ['Uso', 'industrial']],
  'El <strong>Kepler K2 «Bumblebee»</strong> es un humanoide de orientación industrial de la china Kepler Robotics.',
  'Combina cuerpo de tamaño adulto y manos con sensores de fuerza para estudiar manipulación en planta.',
  ['<strong>Integradores industriales</strong>.', '<strong>Centros tecnológicos</strong>.', '<strong>Fábricas</strong> con piloto acotado.'],
  ['<strong>Precio de 2025.</strong> Pide versión, manos y cotización vigentes.', '<strong>Soporte.</strong> Comprueba servicio técnico europeo.', '<strong>Carga.</strong> Exige una prueba con tu pieza.']),
]


def ruta(*p):
    return os.path.join(RAIZ, *p)


def leer(*p):
    with open(ruta(*p), encoding='utf-8') as f:
        return json.load(f)


def guardar(datos, *p):
    with open(ruta(*p), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write('\n')


def lista(xs):
    return '<ul>' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'


def main():
    det = leer('src', 'data', 'marcas-detalle.json')
    pag = leer('src', 'content', 'pages', 'marcas.json')
    ind = leer('src', 'data', 'indice-tarjetas.json')
    site = leer('src', 'data', 'site.json')
    with open(ruta('public', 'img', 'marcas', 'noetix-bumi.svg'), encoding='utf-8') as f:
        base = f.read()
    tarjetas = ''
    for s, n, t, d, card, color, pr, ficha, que, hace, para, cuenta in M:
        det[s] = {'h1': n, 'metaTitulo': t, 'metaDescripcion': d,
                  'queEs': f'<p>{que}</p>', 'queHace': f'<p>{hace}</p>',
                  'paraQuien': lista(para), 'aTenerEnCuenta': lista(cuenta),
                  'precio': dict(zip(('fabrica', 'espana', 'disponible', 'entrega'), pr)),
                  'ficha': ficha, 'nota': NOTA}
        with open(ruta('public', 'img', 'marcas', s + '.svg'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(base.replace('Noetix Bumi', n).replace('#a3e635', color).replace('#1f4a45', '#26315f').replace('#07110f', '#0b1029'))
        if f'id="{s}"' not in pag['html']:
            tarjetas += (f'<article class="tarjeta" id="{s}"><figure><img src="/img/marcas/{s}.svg" alt="Robot humanoide {n}" '
                         f'width="800" height="600" loading="lazy" decoding="async"></figure><div class="tarjeta__texto">'
                         f'<h3><a href="/{s}/">{n}</a></h3><p>{card}</p></div></article>')
        if not any(x['url'] == f'/{s}/' for x in ind['/marcas/']):
            ind['/marcas/'].append({'texto': n, 'url': f'/{s}/'})
        for nav, pre in (('navegacion', '/'), ('navegacionAR', '/ar/')):
            m = next(x for x in site[nav] if x.get('url') in ('/marcas/', '/ar/marcas/'))
            m['columnaUnica'] = True  # 30 modelos: en columnas desborda
            if not any(h['url'] == f'{pre}{s}/' for h in m['hijos']):
                m['hijos'].append({'texto': n, 'url': f'{pre}{s}/'})
    # Al final de la primera rejilla, detrás de la última tarjeta actual.
    corte = re.compile(r'</article>(?=</div></div></section>)').search(pag['html'], pag['html'].index('id="noetix-bumi"')).end()
    pag['html'] = pag['html'][:corte] + tarjetas + pag['html'][corte:]
    guardar(det, 'src', 'data', 'marcas-detalle.json')
    guardar(pag, 'src', 'content', 'pages', 'marcas.json')
    guardar(ind, 'src', 'data', 'indice-tarjetas.json')
    guardar(site, 'src', 'data', 'site.json')
    print(len(M), 'modelos')


if __name__ == '__main__':
    main()
