#!/usr/bin/env python3
"""Ilustraciones vectoriales para las páginas sin fotografía.

No son fotos: son ilustraciones construidas con la paleta del sitio.
Se sustituyen por fotos reales conservando el nombre del archivo,
sin tocar código.

Composición: figura grande y anclada al suelo, texto en bloque
editorial a la izquierda en los formatos apaisados.
"""
import pathlib, math, io, cairosvg
from PIL import Image

MARINO, AZUL, CLARO = '#1c244b', '#467ff7', '#eaeff8'
DEST = pathlib.Path('/home/claude/robothumanoide/public')
FUENTE = 'system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif'


def lienzo(w, h):
    return (
        f'<defs>'
        f'<linearGradient id="f" x1="0" y1="0" x2=".6" y2="1">'
        f'<stop offset="0" stop-color="#26315f"/><stop offset="1" stop-color="#0b1029"/>'
        f'</linearGradient>'
        f'<radialGradient id="halo" cx="62%" cy="46%" r="52%">'
        f'<stop offset="0" stop-color="{AZUL}" stop-opacity=".30"/>'
        f'<stop offset="1" stop-color="{AZUL}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<pattern id="rej" width="72" height="72" patternUnits="userSpaceOnUse">'
        f'<path d="M72 0H0V72" fill="none" stroke="{AZUL}" stroke-opacity=".10"/>'
        f'</pattern>'
        f'<linearGradient id="suelo" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{AZUL}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{AZUL}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{AZUL}" stop-opacity="0"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<rect width="{w}" height="{h}" fill="url(#f)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#rej)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#halo)"/>'
    )


def suelo(cx, y, ancho):
    """Línea de apoyo: ancla la figura y evita que flote."""
    return (f'<rect x="{cx-ancho/2}" y="{y}" width="{ancho}" height="3" fill="url(#suelo)"/>'
            f'<ellipse cx="{cx}" cy="{y+6}" rx="{ancho*0.30}" ry="14" '
            f'fill="#000" opacity=".22"/>')


def robot(cx, base, alt, op=1.0):
    """Humanoide geométrico. cx = eje, base = pies, alt = altura total."""
    u = alt / 560.0          # unidad proporcional
    def U(v): return v * u
    y = base
    g = f'<g opacity="{op}">'
    # piernas
    for l in (-1, 1):
        g += (f'<rect x="{cx + l*U(31) - U(17)}" y="{y - U(196)}" '
              f'width="{U(34)}" height="{U(196)}" rx="{U(17)}" fill="{CLARO}" opacity=".82"/>')
        g += f'<circle cx="{cx + l*U(31)}" cy="{y - U(196)}" r="{U(21)}" fill="{CLARO}" opacity=".9"/>'
    # torso
    g += (f'<rect x="{cx - U(84)}" y="{y - U(390)}" width="{U(168)}" height="{U(200)}" '
          f'rx="{U(46)}" fill="{CLARO}"/>')
    g += (f'<rect x="{cx - U(52)}" y="{y - U(366)}" width="{U(104)}" height="{U(56)}" '
          f'rx="{U(14)}" fill="{MARINO}" opacity=".28"/>')
    g += f'<circle cx="{cx}" cy="{y - U(268)}" r="{U(30)}" fill="{MARINO}"/>'
    g += f'<circle cx="{cx}" cy="{y - U(268)}" r="{U(15)}" fill="{AZUL}"/>'
    # brazos
    for l in (-1, 1):
        g += f'<circle cx="{cx + l*U(102)}" cy="{y - U(360)}" r="{U(30)}" fill="{CLARO}"/>'
        g += (f'<rect x="{cx + l*U(102) - U(16)}" y="{y - U(348)}" '
              f'width="{U(32)}" height="{U(150)}" rx="{U(16)}" fill="{CLARO}" opacity=".88"/>')
        g += f'<circle cx="{cx + l*U(102)}" cy="{y - U(200)}" r="{U(20)}" fill="{CLARO}" opacity=".95"/>'
    # cuello y cabeza
    g += f'<rect x="{cx - U(18)}" y="{y - U(414)}" width="{U(36)}" height="{U(28)}" fill="{CLARO}" opacity=".7"/>'
    g += (f'<rect x="{cx - U(66)}" y="{y - U(530)}" width="{U(132)}" height="{U(120)}" '
          f'rx="{U(44)}" fill="{CLARO}"/>')
    g += (f'<rect x="{cx - U(44)}" y="{y - U(486)}" width="{U(88)}" height="{U(24)}" '
          f'rx="{U(12)}" fill="{MARINO}"/>')
    for l in (-1, 1):
        g += f'<circle cx="{cx + l*U(20)}" cy="{y - U(474)}" r="{U(8)}" fill="{AZUL}"/>'
    g += f'<circle cx="{cx - U(74)}" cy="{y - U(470)}" r="{U(14)}" fill="{CLARO}" opacity=".8"/>'
    g += f'<circle cx="{cx + U(74)}" cy="{y - U(470)}" r="{U(14)}" fill="{CLARO}" opacity=".8"/>'
    return g + '</g>'


def engranaje(cx, cy, r, n=12, color=AZUL, op=.9):
    """Engranaje con dientes trapezoidales de verdad, no una estrella."""
    p = []
    for i in range(n):
        a0 = 2*math.pi*i/n
        pa, pb = 2*math.pi/n*0.22, 2*math.pi/n*0.14
        for ang, rr in ((a0-pa, r*0.80), (a0-pb, r), (a0+pb, r), (a0+pa, r*0.80)):
            p.append(f'{cx+rr*math.cos(ang):.1f},{cy+rr*math.sin(ang):.1f}')
    return (f'<polygon points="{" ".join(p)}" fill="{color}" opacity="{op}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.34:.1f}" fill="#0e1433"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.17:.1f}" fill="{color}" opacity=".7"/>')


def texto_izq(x, y, titulo, sub, tam):
    t = (f'<text x="{x}" y="{y}" font-family="{FUENTE}" font-size="{tam}" font-weight="700" '
         f'fill="#ffffff" letter-spacing="-1.5">{titulo}</text>')
    t += f'<rect x="{x}" y="{y+tam*0.42}" width="86" height="5" rx="2.5" fill="{AZUL}"/>'
    if sub:
        t += (f'<text x="{x}" y="{y + tam*1.18}" font-family="{FUENTE}" '
              f'font-size="{tam*0.42:.0f}" fill="#9db0dd">{sub}</text>')
    return t


def texto_centro(w, y, titulo, sub, tam):
    t = (f'<text x="{w/2}" y="{y}" text-anchor="middle" font-family="{FUENTE}" '
         f'font-size="{tam}" font-weight="700" fill="#ffffff" letter-spacing="-1.5">{titulo}</text>')
    if sub:
        t += (f'<text x="{w/2}" y="{y + tam*0.62}" text-anchor="middle" font-family="{FUENTE}" '
              f'font-size="{tam*0.38:.0f}" fill="#9db0dd">{sub}</text>')
    return t


# ── piezas de escena ──────────────────────────────────────────────
def libro(cx, cy, s=1.0):
    return (f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<path d="M-150 -92 h132 a20 20 0 0 1 18 20 v164 a20 20 0 0 0 -18 -20 h-132 z" fill="{CLARO}"/>'
            f'<path d="M150 -92 h-132 a20 20 0 0 0 -18 20 v164 a20 20 0 0 1 18 -20 h132 z" fill="{CLARO}" opacity=".72"/>'
            + ''.join(f'<rect x="-126" y="{-56+i*30}" width="{92-i*14}" height="9" rx="4.5" '
                      f'fill="{MARINO}" opacity=".5"/>' for i in range(4))
            + ''.join(f'<rect x="34" y="{-56+i*30}" width="{92-i*14}" height="9" rx="4.5" '
                      f'fill="{MARINO}" opacity=".38"/>' for i in range(4))
            + '</g>')


def casa(cx, cy, s=1.0):
    return (f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<path d="M-210 30 L0 -150 L210 30" fill="none" stroke="{AZUL}" '
            f'stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<rect x="-166" y="30" width="332" height="212" rx="10" fill="none" '
            f'stroke="{CLARO}" stroke-width="10" opacity=".55"/>'
            f'</g>')


def pizarra(cx, cy, w, h):
    return (f'<g transform="translate({cx},{cy})">'
            f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="14" fill="#080c26" '
            f'stroke="{AZUL}" stroke-width="4"/>'
            f'<circle cx="{-w/2+90}" cy="{-h/2+92}" r="38" fill="none" stroke="{AZUL}" stroke-width="6"/>'
            f'<path d="M{-w/2+52} {h/2-72} h84 v-58 h72 v-48 h80" fill="none" stroke="{CLARO}" '
            f'stroke-width="6" stroke-linecap="round" opacity=".85"/>'
            + ''.join(f'<rect x="{-w/2+50}" y="{-h/2+160+i*26}" width="{190-i*46}" height="10" '
                      f'rx="5" fill="{CLARO}" opacity="{.42-i*.1}"/>' for i in range(3))
            + '</g>')


def sobre(cx, cy, s=1.0):
    return (f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<rect x="-190" y="-124" width="380" height="248" rx="18" fill="{CLARO}"/>'
            f'<path d="M-190 -108 L0 38 L190 -108" fill="none" stroke="{MARINO}" '
            f'stroke-width="16" stroke-linejoin="round"/>'
            f'<circle cx="164" cy="-96" r="38" fill="{AZUL}"/>'
            f'</g>')


# ── composiciones ─────────────────────────────────────────────────
C = 1280   # tarjetas cuadradas
HW, HH = 1792, 1024   # heroes apaisados

ESCENAS = {
 '/wp-content/uploads/2025/03/robot-educativo.jpeg': (C, C, lambda w, h:
    lienzo(w, h) + libro(w*0.66, 810, .92) + suelo(w*0.42, 990, 760)
    + robot(w*0.42, 985, 700) + texto_centro(w, 1160, 'Robots Educativos', 'Programación y STEM en el aula', 62)),

 '/wp-content/uploads/2025/03/robot-para-el-hogar.jpeg': (C, C, lambda w, h:
    lienzo(w, h) + casa(w/2, 560, 1.05) + suelo(w/2, 990, 820)
    + robot(w/2, 985, 660) + texto_centro(w, 1160, 'Robots para el Hogar', 'Tareas domésticas y asistencia', 58)),

 '/wp-content/uploads/2025/03/cursos-robotica-humanoide.jpeg': (C, C, lambda w, h:
    lienzo(w, h) + pizarra(w*0.66, 620, 480, 340) + suelo(w*0.32, 990, 700)
    + robot(w*0.32, 985, 690) + texto_centro(w, 1160, 'Cursos de Robótica', 'Formación técnica y certificación', 60)),

 '/wp-content/uploads/2026/01/robot-humanoide-santa-fe.webp': (HW, HH, lambda w, h:
    lienzo(w, h)
    + f'<circle cx="{w*0.70}" cy="470" r="330" fill="none" stroke="{AZUL}" stroke-width="3" opacity=".30"/>'
    + f'<circle cx="{w*0.70}" cy="470" r="420" fill="none" stroke="{AZUL}" stroke-width="2" opacity=".16"/>'
    + suelo(w*0.70, 866, 700) + robot(w*0.70, 860, 720)
    + texto_izq(140, 470, 'Robot Humanoide', 'Santa Fe · Argentina', 84)),

 '/img/heroes/tipos-de-robot-humanoide.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + suelo(w*0.66, 866, 900)
    + robot(w*0.50, 860, 480, .42) + robot(w*0.82, 860, 480, .42) + robot(w*0.66, 860, 700)
    + texto_izq(140, 470, 'Tipos de Robot', '15 categorías según su uso', 84)),

 '/img/heroes/marcas-de-robots-humanoides.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + ''.join(
        f'<rect x="{w*0.46 + (i%4)*196}" y="{262 + (i//4)*196}" width="164" height="164" rx="26" '
        f'fill="{CLARO}" opacity="{.22 + .13*((i*3) % 5)}"/>' for i in range(12))
    + texto_izq(140, 470, 'Marcas y Fabricantes', '15 marcas del sector', 78)),

 '/img/heroes/servicios-para-robots-humanoides.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + engranaje(w*0.79, 400, 168, 14) + engranaje(w*0.945, 588, 106, 11, CLARO, .5)
    + suelo(w*0.60, 866, 620) + robot(w*0.60, 860, 690)
    + texto_izq(140, 470, 'Servicios', 'Venta, alquiler, soporte e importación', 84)),

 '/img/heroes/accesorios-y-repuestos-robot-humanoide.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + engranaje(w*0.56, 400, 148, 13)
    + f'<circle cx="{w*0.72}" cy="382" r="118" fill="none" stroke="{CLARO}" stroke-width="18" opacity=".7"/>'
    + f'<circle cx="{w*0.72}" cy="382" r="44" fill="{AZUL}" opacity=".85"/>'
    + f'<rect x="{w*0.82}" y="490" width="290" height="216" rx="22" fill="{CLARO}" opacity=".5"/>'
    + f'<rect x="{w*0.82+34}" y="524" width="222" height="148" rx="12" fill="#0e1433"/>'
    + ''.join(f'<rect x="{w*0.82+62+i*48}" y="556" width="26" height="84" rx="6" fill="{AZUL}" '
              f'opacity=".85"/>' for i in range(4))
    + texto_izq(140, 470, 'Accesorios y Repuestos', 'Actuadores, sensores, manos y baterías', 74)),

 '/img/heroes/contacto-robot-humanoide.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + sobre(w*0.83, 400, 1.0)
    + suelo(w*0.62, 866, 600) + robot(w*0.62, 860, 680)
    + texto_izq(140, 470, 'Contacto', 'España y Argentina', 92)),

 '/img/heroes/sobre-nosotros-robot-humanoide.webp': (HW, HH, lambda w, h:
    lienzo(w, h) + suelo(w*0.68, 866, 940)
    + robot(w*0.53, 860, 560, .55) + robot(w*0.83, 860, 560, .55) + robot(w*0.68, 860, 680)
    + texto_izq(140, 470, 'Sobre Nosotros', 'Especialistas en robótica humanoide', 76)),
}

for ruta, (w, h, escena) in ESCENAS.items():
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}">{escena(w, h)}</svg>')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    im = Image.open(io.BytesIO(png)).convert('RGB')
    destino = DEST / ruta.lstrip('/')
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.suffix in ('.jpg', '.jpeg'):
        im.save(destino, 'JPEG', quality=88, optimize=True, progressive=True)
    else:
        im.save(destino, 'WEBP', quality=84, method=6)
    m = destino.with_suffix('.svg')
    if m.exists():
        m.unlink()
    print(f'  {ruta.rsplit("/", 1)[-1]:<44}{w}x{h:<6}{destino.stat().st_size // 1024:>4} KB')

print(f'\n{len(ESCENAS)} ilustraciones')
