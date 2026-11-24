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
