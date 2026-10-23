#!/usr/bin/env python3
"""Texto por capítulos de El libro de la salsa (César Miguel Rondón, edición actualizada; ePub de Epublibre).

Uso: python3 -I tools/split.py <dir_xhtml> <dir_salida>

Lee directamente los XHTML del ePub. El libro tiene cuatro partes («Salsa cero» a «Salsa tres») y una coda,
con apartados de muy distinta longitud; cada fichero de datos cubre uno o varios apartados:
1 = prefacios y prólogo de Padura; 2 = años cincuenta; 3 = años sesenta; 4 = es la cosa; 5 = el sonido de
Nueva York; 6 = nuestra cosa latina (la banda, las voces, la película); 7 = la cosa en montuno; 8 = el boom
y las Estrellas de Fania; 9 = las otras estrellas; 10 = entre lo típico y lo moderno; 11 = Puerto Rico;
12 = las charangas; 13 = un compositor y un cantante; 14 = el caso venezolano; 15 = la otra cosa y
tradición y vanguardia; 16 = Quisqueya; 17 = los líderes; 18 = un compositor cantante y todas las salsas;
19 = coda y un cuarto de siglo después; 20 = la rumba sin fin; 21 = discografía básica.
Las cabeceras salen como «## …»; cada letra de canción (una tabla, a veces a dos columnas: coro y
pregón) se une en una sola línea: versos con « / » y columnas, leídas una tras otra, con « // ». Escribe <dir>/NN.txt y <dir>/book.json (párrafos
{ch, sec, segs: [[pág, texto]]}, el formato de tools/refs.py). El ePub no trae paginación impresa: la
página se estima a 300 palabras por página desde el primer prefacio.
"""
import html
import json
import re
import sys
from pathlib import Path

WORDS_PER_PAGE = 300
FILES = {
    1: ['prefacio_coda', 'prefacio_2004', 'prologo'], 2: ['salsa0', 'anoscincuenta'], 3: ['anosesenta'],
    4: ['salsa1', 'eslacosa'], 5: ['elsonidodeNuevaYork'], 6: ['nuestracosalatina', 'labanda', 'lasvoces', 'lapelicula'],
    7: ['salsa2', 'lacosaenmontuno'], 8: ['elboom', 'lasestrelladelafania'], 9: ['lasotrasestrellas'],
    10: ['entrelotipicoylomoderno'], 11: ['puertorico'], 12: ['lascharangas'], 13: ['uncompositoryuncantante'],
    14: ['elcasovenezolano'], 15: ['salsa3', 'laotracosa', 'tradicionyvanguardia'], 16: ['quisqueya'],
    17: ['loslideres'], 18: ['uncompositorcantante', 'todaslassalsas'], 19: ['coda', 'uncuartodesiglodespues'],
    20: ['larumbasinfin'], 21: ['discografiabasica'],
}
BLOCK = re.compile(r'<table>(.*?)</table>|<(p|h[1-6])\b([^>]*)>(.*?)</\2>', re.S)


def clean(s):
    s = re.sub(r'<sup[^>]*>.*?</sup>', '', s, flags=re.S)
    s = html.unescape(re.sub(r'<[^>]+>', '', s)).replace('⁠', '')
    return re.sub(r'\s+', ' ', s).strip()


def main(src, out):
    src, out = Path(src), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paras, words = [], 0
    for ch, names in FILES.items():
        sec, text = None, []
        for name in names:
            doc = (src / f'{name}.xhtml').read_text()
            for m in BLOCK.finditer(doc[doc.index('<body'):]):
                table, tag, attrs, inner = m.groups()
                if table is not None:
                    rows = [[clean(c) for c in re.findall(r'<td\b[^>]*>(.*?)</td>', r, re.S)] for r in re.findall(r'<tr\b[^>]*>(.*?)</tr>', table, re.S)]
                    cols = [[r[i] for r in rows if i < len(r) and r[i]] for i in range(max(map(len, rows), default=0))]
                    line = ' // '.join(' / '.join(c) for c in cols if c)
                else:
                    line = clean(inner)
                if not line:
                    continue
                if tag and tag != 'p':
                    sec = line
                    text.append(f'## {line}')
                    continue
                page = words // WORDS_PER_PAGE + 1
                paras.append({'ch': ch, 'sec': sec, 'segs': [[page, line]]})
                text.append(f'[pág. ≈{page}] {line}')
                words += len(line.split())
        (out / f'{ch:02d}.txt').write_text('\n\n'.join(text) + '\n')
        print(f'cap. {ch}: {sum(len(p["segs"][0][1].split()) for p in paras if p["ch"] == ch)} palabras')
    (out / 'book.json').write_text(json.dumps(paras, ensure_ascii=False))


if __name__ == '__main__':
    main(*sys.argv[1:])
