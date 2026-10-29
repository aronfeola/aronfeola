#!/usr/bin/env python3
"""Dice qué tipografía se parece más a una línea de texto de la referencia y con qué
tamaño de letra hay que escribirla.

Cada tipografía tiene proporciones propias. Hay dos formas de medirlas:

  1) Solo con el ancho y el alto de la línea (de analizar_anuncio.py):
       python scripts/ajustar_fuente.py --texto "REGALOS CON" --ancho 724 --alto 131 \\
           estilos/_fuentes/Anton-400.ttf estilos/_fuentes/Bebas*.ttf
     Sirve para letra grande y de formas muy distintas. En letra chica muchas empatan.

  2) Con la imagen (MUCHO más preciso): además compara dónde cae cada palabra dentro de la
     línea, que es muy distinto de una tipografía a otra.
       python scripts/ajustar_fuente.py --texto "This is what gold looks like" \\
           --imagen estilos/mi-estilo/referencia.png --caja 20,140,720,190 estilos/_fuentes/*-400.ttf
     --caja = x0,y0,x1,y1 de un rectángulo que contenga SOLO esa línea (mirá analisis.png).

    --texto       el texto de la línea, tal cual se ve (en mayúsculas si está en mayúsculas)
    --espaciado   separación extra entre letras, en px (opcional)

Un "error" menor al 2% es muy probable; menor al 5%, candidata. No distingue pesos de la misma
familia (Inter 400 vs 500): el peso se ve a ojo. Necesita Pillow y numpy.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFont


def medir(ruta, tam, texto, espaciado):
    f = ImageFont.truetype(str(ruta), tam)
    l, t, r, b = f.getbbox(texto)
    if espaciado:
        return sum(f.getlength(c) for c in texto) + espaciado * (len(texto) - 1), b - t
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
    return (t, *medir(ruta, t, texto, espaciado))


def palabras_de_la_imagen(ruta, caja):
    """Extensión horizontal (x0, x1) de cada palabra en la caja, relativa al inicio de la línea."""
    x0, y0, x1, y1 = caja
    g = np.asarray(Image.open(ruta).convert("L")).astype(int)[y0:y1, x0:x1]
    fondo = np.median(g)
    tinta = np.abs(g - fondo) > 50
    filas = np.where(tinta.any(axis=1))[0]
    cols = np.where(tinta.any(axis=0))[0]
    if not len(cols):
        return None, None
    alto = filas.max() - filas.min() + 1
    hueco = max(2, 0.18 * alto)  # entre palabras el hueco es mayor que entre letras
    tramos, ini, ult = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - ult > hueco:
            tramos.append((ini, ult))
            ini = c
        ult = c
    tramos.append((ini, ult))
    base = tramos[0][0]
    return [(a - base, b - base + 1) for a, b in tramos], int(cols.max() - cols.min() + 1), int(alto)


def palabras_de_la_fuente(ruta, tam, texto):
    f = ImageFont.truetype(str(ruta), tam)
    palabras = texto.split()
    out = []
    for i, w in enumerate(palabras):
        prefijo = " ".join(palabras[:i]) + (" " if i else "")
        base = f.getlength(prefijo)
        l, _t, r, _b = f.getbbox(w)
        out.append((base + l, base + r))
    ini = out[0][0]
    return [(a - ini, b - ini) for a, b in out]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuentes", nargs="+")
    ap.add_argument("--texto", required=True)
    ap.add_argument("--ancho", type=float)
    ap.add_argument("--alto", type=float)
    ap.add_argument("--imagen")
    ap.add_argument("--caja")
    ap.add_argument("--espaciado", type=float, default=0.0)
    a = ap.parse_args()

    palabras_ref = None
    if a.imagen and a.caja:
        caja = [int(v) for v in a.caja.split(",")]
        palabras_ref, a.ancho, a.alto = palabras_de_la_imagen(a.imagen, caja)
        if palabras_ref is None:
            print("No encontré texto en esa caja.")
            return
        if len(palabras_ref) != len(a.texto.split()):
            print(f"Aviso: en la imagen separé {len(palabras_ref)} palabras y el texto tiene "
                  f"{len(a.texto.split())}; comparo solo ancho y alto.")
            palabras_ref = None
    if not a.ancho or not a.alto:
        ap.error("pasá --ancho y --alto, o --imagen y --caja")

    filas = []
    for ruta in a.fuentes:
        try:
            t, w, h = tamano_para_ancho(ruta, a.texto, a.ancho, a.espaciado)
            err_alto = abs(h - a.alto) / a.alto * 100
            err_pal = None
            if palabras_ref:
                pf = palabras_de_la_fuente(ruta, t, a.texto)
                err_pal = float(np.mean([abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(pf, palabras_ref)]) / 2 / a.ancho * 100)
        except OSError as e:
            print(f"No pude abrir {ruta}: {e}")
            continue
        # Con palabras, manda ese error (mucho más específico); si no, el del alto.
        puntaje = err_pal if err_pal is not None else err_alto
        filas.append((puntaje, Path(ruta).name, t, h, err_alto, err_pal))

    print(f"Referencia: «{a.texto}»  {a.ancho:.0f} × {a.alto:.0f} px\n")
    cab = f"{'Tipografía':<28}{'Tamaño':>9}{'Error alto':>12}"
    if palabras_ref:
        cab += f"{'Error palabras':>16}"
    print(cab)
    for puntaje, nombre, t, h, ea, ep in sorted(filas)[:14]:
        marca = "  ← muy probable" if puntaje < 0.8 else ("  ← candidata" if puntaje < 1.6 else "")
        if not palabras_ref:
            marca = "  ← muy probable" if puntaje < 2 else ("  ← candidata" if puntaje < 5 else "")
        linea = f"{nombre:<28}{t:>6} px{ea:>11.1f}%"
        if palabras_ref:
            linea += f"{ep:>15.2f}%"
        print(linea + marca)
    print("\nOjo: (1) si el texto tiene espaciado entre letras, pasalo con --espaciado. (2) Identifica la "
          "familia, no el peso: dentro de una misma familia casi no cambia; el peso se ve a ojo. "
          "(3) Si dos quedan muy cerca, probá ambas en la plantilla y compará.")


if __name__ == "__main__":
    main()
