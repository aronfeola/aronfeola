#!/usr/bin/env python3
"""Baja una tipografía de Google Fonts a estilos/_fuentes/ para que los estilos se
vean igual en cualquier compu, sin internet.

    python scripts/bajar_fuente.py "Anton"
    python scripts/bajar_fuente.py "Montserrat" 400 700
    python scripts/bajar_fuente.py "Playfair Display" 400 700 italic

Al final imprime el @font-face para pegar en la plantilla.html del estilo.
"""

import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "estilos" / "_fuentes"
# Sin un navegador en el User-Agent, Google devuelve archivos .ttf.
CABECERAS = {"User-Agent": "curl/8"}


def pedir(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=CABECERAS), timeout=30).read()


def css_de(familia, pesos, cursiva):
    nombre = urllib.parse.quote_plus(familia)
    if pesos:
        ital = 1 if cursiva else 0
        tuplas = ";".join(f"{ital},{p}" for p in sorted(pesos, key=int))
        url = f"https://fonts.googleapis.com/css2?family={nombre}:ital,wght@{tuplas}"
    else:
        url = f"https://fonts.googleapis.com/css2?family={nombre}"
    return pedir(url).decode()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    familia = args[0]
    pesos = [a for a in args[1:] if a.isdigit()]
    cursiva = "italic" in args

    try:
        css = css_de(familia, pesos, cursiva)
    except urllib.error.HTTPError:
        # Esa familia no tiene los pesos o la cursiva pedidos: se baja lo que tenga.
        print(f"'{familia}' no tiene esos pesos o la cursiva; bajo lo que ofrece.")
        try:
            css = css_de(familia, [], False)
        except urllib.error.HTTPError:
            print(f"No encontré la familia '{familia}' en Google Fonts. Revisá el nombre.")
            sys.exit(1)

    DESTINO.mkdir(parents=True, exist_ok=True)
    reglas = []
    vistos = set()
    for bloque in re.findall(r"@font-face\s*\{[^}]*\}", css):
        estilo = re.search(r"font-style:\s*(\w+)", bloque).group(1)
        peso = re.search(r"font-weight:\s*(\d+)", bloque).group(1)
        url = re.search(r"url\(([^)]+)\)", bloque).group(1)
        if (estilo, peso) in vistos:
            continue
        vistos.add((estilo, peso))
        archivo = f"{familia.replace(' ', '')}-{peso}{'-italic' if estilo == 'italic' else ''}.ttf"
        (DESTINO / archivo).write_bytes(pedir(url))
        print(f"✓ {archivo}")
        reglas.append(
            f"@font-face {{ font-family: '{familia}'; font-weight: {peso}; font-style: {estilo}; "
            f"src: url('../_fuentes/{archivo}'); }}"
        )

    print("\nPegá esto en la plantilla.html del estilo:\n")
    print("\n".join(reglas))


if __name__ == "__main__":
    main()
