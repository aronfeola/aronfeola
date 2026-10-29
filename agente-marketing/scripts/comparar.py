#!/usr/bin/env python3
"""Compara la referencia con lo que generó la plantilla y dice dónde se parecen menos.

    python scripts/comparar.py estilos/mi-estilo/referencia.png salida.png [comparacion.png]

Guarda una imagen con 3 paneles: referencia | generado | diferencias (en rojo).
Necesita Pillow y numpy.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    ref = Image.open(sys.argv[1]).convert("RGB")
    gen = Image.open(sys.argv[2]).convert("RGB")
    salida = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(sys.argv[2]).with_name("comparacion.png")

    if gen.size != ref.size:
        print(f"Aviso: tamaños distintos (referencia {ref.size}, generado {gen.size}); ajusto el generado.")
        gen = gen.resize(ref.size, Image.LANCZOS)

    d = np.abs(np.asarray(ref, dtype=np.int16) - np.asarray(gen, dtype=np.int16)).max(axis=2)
    distinto = d > 24
    print(f"Píxeles distintos: {100 * distinto.mean():.2f}%  (0% = idéntico)")

    h = ref.size[1]
    franjas = []
    for i in range(10):
        trozo = distinto[i * h // 10:(i + 1) * h // 10]
        franjas.append((100 * trozo.mean(), i))
    peores = sorted(franjas, reverse=True)[:3]
    print("Franjas con más diferencia (de arriba hacia abajo, en % del alto): " +
          ", ".join(f"{i * 10}–{i * 10 + 10}%: {p:.1f}% distinto" for p, i in sorted(peores, key=lambda t: t[1])))

    rojo = np.zeros((*d.shape, 3), dtype=np.uint8)
    rojo[..., 0] = np.clip(d * 3, 0, 255)
    rojo[..., 1] = rojo[..., 2] = (255 - np.clip(d * 3, 0, 255)) // 4
    paneles = [ref, gen, Image.fromarray(rojo)]
    alto = 800
    paneles = [p.resize((round(p.size[0] * alto / p.size[1]), alto), Image.LANCZOS) for p in paneles]
    lienzo = Image.new("RGB", (sum(p.size[0] for p in paneles) + 20 * 2, alto), (90, 90, 90))
    x = 0
    for p in paneles:
        lienzo.paste(p, (x, 0))
        x += p.size[0] + 20
    lienzo.save(salida)
    print(f"Guardé {salida}")


if __name__ == "__main__":
    main()
