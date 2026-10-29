#!/usr/bin/env python3
"""Dice qué tipografía se parece más a una línea de texto de la referencia y con qué
tamaño de letra hay que escribirla.

Cada tipografía tiene una proporción propia entre el ancho y el alto de una línea. Se
mide en la referencia (ancho y alto de la caja de ESA línea, de analizar_anuncio.py) y se
prueba con cada candidata: la que da el alto más parecido es la más probable.

    python scripts/ajustar_fuente.py --texto "REGALOS CON" --ancho 724 --alto 131 \\
        estilos/_fuentes/Anton-400.ttf estilos/_fuentes/Inter-800.ttf

    --texto       el texto de esa línea, tal cual se ve (con mayúsculas si están en mayúsculas)
    --ancho/--alto  px de la caja de esa línea en la referencia
    --espaciado   separación extra entre letras, en px (opcional)

Un error de alto menor al 5% es un buen candidato; menor al 2%, casi seguro. Necesita Pillow.
"""

import argparse
from pathlib import Path

from PIL import ImageFont


def cargar(ruta, tam):
    return ImageFont.truetype(str(ruta), tam)


def medir(ruta, tam, texto, espaciado):
    f = cargar(ruta, tam)
    if espaciado:
        ancho = sum(f.getlength(c) for c in texto) + espaciado * (len(texto) - 1)
        l, t, r, b = f.getbbox(texto)
        return ancho, b - t
    l, t, r, b = f.getbbox(texto)
    return r - l, b - t


def tamano_para_ancho(ruta, texto, ancho, espaciado):
    bajo, alto = 6.0, 900.0
    for _ in range(30):
        medio = (bajo + alto) / 2
        w, _h = medir(ruta, round(medio), texto, espaciado)
        if w < ancho:
            bajo = medio
        else:
            alto = medio
    t = round((bajo + alto) / 2)
    return t, *medir(ruta, t, texto, espaciado)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuentes", nargs="+")
    ap.add_argument("--texto", required=True)
    ap.add_argument("--ancho", type=float, required=True)
    ap.add_argument("--alto", type=float, required=True)
    ap.add_argument("--espaciado", type=float, default=0.0)
    a = ap.parse_args()

    filas = []
    for ruta in a.fuentes:
        try:
            t, w, h = tamano_para_ancho(ruta, a.texto, a.ancho, a.espaciado)
        except OSError as e:
            print(f"No pude abrir {ruta}: {e}")
            continue
        filas.append((abs(h - a.alto) / a.alto * 100, Path(ruta).name, t, h))

    print(f"Referencia: «{a.texto}»  {a.ancho:.0f} × {a.alto:.0f} px\n")
    print(f"{'Tipografía':<28}{'Tamaño de letra':>16}{'Alto que da':>13}{'Error':>9}")
    for err, nombre, t, h in sorted(filas):
        marca = "  ← muy probable" if err < 2 else ("  ← candidata" if err < 5 else "")
        print(f"{nombre:<28}{t:>13} px{h:>10.0f} px{err:>8.1f}%{marca}")
    print("\nOjo: (1) si el texto tiene espaciado entre letras, pasalo con --espaciado; sin eso el "
          "tamaño sale un poco chico. (2) Esto identifica la familia, no el peso: dentro de una "
          "misma familia (ej. Inter 500 vs 800) la proporción casi no cambia; el peso se ve a ojo.")


if __name__ == "__main__":
    main()
