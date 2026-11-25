# Capa de refuerzo SEO/AEO: SUMA contenido sin tocar los textos existentes.
# Lee contenido-seo/*.txt y escribe src/data/refuerzo.json, que Base.astro
# pinta por URL (respuesta rápida arriba; H2 y preguntas al final).
#
# También genera public/llms.txt a partir de las mismas respuestas.
# Uso:  python generar_refuerzo.py
#
# Formato:  @/url/   > respuesta corta   ## H2   - viñeta   ? pregunta   = respuesta
# ciudades.txt:  slug|H2|párrafo|pregunta|respuesta
import json
import os
import re

from argentino import argentino, es_de_espana

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(RAIZ, 'contenido-seo')
DOMINIO = 'https://robothumanoide.org'


def leer(nombre):
    with open(os.path.join(ORIGEN, nombre), encoding='utf-8') as f:
        return f.read()


def en_linea(t):
    t = re.sub(r'\*\*(\[.+?\]\(.+?\)|.+?)\*\*', r'<strong>\1</strong>', t)
    return re.sub(r'\[([^\]]+)\]\((/[^)]*)\)', r'<a href="\2">\1</a>', t)


def main():
    datos = {}
    for nombre in ('paginas.txt', 'fichas.txt', 'marcas-nuevas.txt'):
        for trozo in re.split(r'^@', leer(nombre), flags=re.M)[1:]:
            url, *lineas = trozo.strip().split('\n')
            p = datos[url] = {'secciones': [], 'faq': []}
            for l in filter(None, (x.strip() for x in lineas)):
                if l.startswith('> '):
                    p['respuesta'] = l[2:]
                elif l.startswith('## '):
                    p['secciones'].append({'h2': l[3:], 'html': ''})
                elif l.startswith('- '):
                    p['secciones'][-1]['html'] += f'<li>{en_linea(l[2:])}</li>'
                elif l.startswith('? '):
                    p['faq'].append({'pregunta': l[2:], 'respuesta': ''})
                elif l.startswith('= '):
                    p['faq'][-1]['respuesta'] = l[2:]
                else:
                    p['secciones'][-1]['html'] += f'<p>{en_linea(l)}</p>'
            for s in p['secciones']:
                s['html'] = re.sub(r'((?:<li>.*?</li>)+)', r'<ul>\1</ul>', s['html'])
    # Fichas argentinas: el mismo refuerzo que España, adaptado. Lo que solo
    # vale en España (leyes, euros, tiendas) no pasa.
    site = json.load(open(os.path.join(RAIZ, 'src', 'data', 'site.json'), encoding='utf-8'))
    fichas_ar = set(re.findall(r'"url": "(/ar/[^"]+)"', json.dumps(site['navegacionAR'])))
    for url in list(datos):
        ar = '/ar' + ('/normativa-y-certificaciones/' if url == '/marcado-ce-y-normativa/' else url)
        if url.startswith('/ar/') or ar not in fichas_ar or ar in datos:
            continue
        p = datos[url]
        cambia = lambda t: re.sub(r'href="/(?!ar/)([a-z0-9-]+)/"', r'href="/ar/\1/"', argentino(t))
        n = {'secciones': [], 'faq': []}
        resp = [x for x in re.split(r'(?<=\.) (?=[A-ZÁÉÍÓÚ])', cambia(p.get('respuesta', ''))) if not es_de_espana(x)]
        if resp:
            n['respuesta'] = ' '.join(resp)
        for s in p['secciones']:
            s = {k: cambia(v) for k, v in s.items()}
            if not es_de_espana(s['h2'] + s['html']):
                n['secciones'].append(s)
        for q in p['faq']:
            q = {k: cambia(v) for k, v in q.items()}
            # Sin sección debajo de la que colgar, la pregunta no se pinta.
            if n['secciones'] and not es_de_espana(q['pregunta'] + q['respuesta']):
                n['faq'].append(q)
        datos[ar] = n
    for l in leer('ciudades.txt').strip().split('\n'):
        slug, h2, texto, q, r = l.split('|')
        datos[f'/{slug}/'] = {'secciones': [{'h2': h2, 'html': f'<p>{texto}</p>'}],
                              'faq': [{'pregunta': q, 'respuesta': r}]}
    with open(os.path.join(RAIZ, 'src', 'data', 'refuerzo.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write('\n')

    out = ['# Robot Humanoide', '', '> Guía y servicios de robots humanoides para España y Argentina: precios, marcas, compra, alquiler, cursos y recambios.', '']
    grupos = [('España', lambda u: not u.startswith('/ar/')), ('Argentina', lambda u: u.startswith('/ar/'))]
    for titulo, cond in grupos:
        out += [f'## {titulo}', '']
        out += [f'- [{DOMINIO}{u}]({DOMINIO}{u}): {p["respuesta"]}' for u, p in datos.items() if cond(u) and p.get('respuesta')]
        out.append('')
    with open(os.path.join(RAIZ, 'public', 'llms.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out))
    print(len(datos), 'páginas reforzadas')


if __name__ == '__main__':
    main()
