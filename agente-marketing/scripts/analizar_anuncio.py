#!/usr/bin/env python3
"""Mide un anuncio: tamaño, fondo, paleta, márgenes y, de arriba hacia abajo, cada
bloque de texto, foto o caja de color, con su posición, tamaño, color y alineación.

    python scripts/analizar_anuncio.py estilos/mi-estilo/referencia.png

Deja al lado de la imagen:
  analisis.png   la imagen con una grilla del 10% y cada elemento marcado y numerado
  analisis.json  los mismos datos, para usarlos al armar la plantilla

Necesita Pillow y numpy (pip install pillow numpy). Las medidas son aproximadas: sirven
para armar la plantilla; el ajuste fino se hace comparando con comparar.py.
Funciona bien con fondos lisos. Con fondo de foto o degradado da la paleta y la grilla,
y el resto se mide a ojo sobre analisis.png.
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def hx(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def tramos(flags, hueco):
    """Tramos consecutivos de True; une los separados por <= hueco posiciones."""
    out, ini, ult = [], None, None
    for i, f in enumerate(flags):
        if not f:
            continue
        if ini is None:
            ini = i
        elif i - ult - 1 > hueco:
            out.append((ini, ult))
            ini = i
        ult = i
    if ini is not None:
        out.append((ini, ult))
    return out


def racha_max(fila):
    """Largo de la raya continua más larga de True en una fila."""
    d = np.diff(np.concatenate([[0], fila.astype(np.int8), [0]]))
    ini, fin = np.where(d == 1)[0], np.where(d == -1)[0]
    return int((fin - ini).max()) if len(ini) else 0


def color_dominante(pix):
    """Color más frecuente de un conjunto de píxeles (N, 3)."""
    cuant = (pix // 8) * 8 + 4
    vals, cnt = np.unique(cuant, axis=0, return_counts=True)
    c = vals[cnt.argmax()]
    cerca = pix[np.abs(pix - c).max(axis=1) <= 10]
    return cerca.mean(axis=0) if len(cerca) else c


def color_de_tinta(pix, fondo):
    """Color del trazo: los píxeles más lejanos al fondo (el borde suavizado no cuenta)."""
    d = np.abs(pix - fondo).max(axis=1)
    return pix[d >= 0.75 * d.max()].mean(axis=0)


def analizar(ruta):
    im = Image.open(ruta).convert("RGB")
    W, H = im.size
    esc = min(1.0, 600 / W)
    sm = im.resize((max(1, round(W * esc)), max(1, round(H * esc))), Image.LANCZOS)
    a = np.asarray(sm).astype(np.int16)
    h, w, _ = a.shape

    # Paleta general
    q = sm.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[:24]).reshape(-1, 3)
    paleta = [{"color": hx(pal[i]), "pct": round(100 * n / (h * w), 1)} for n, i in sorted(q.getcolors(), reverse=True)]

    # Fondo: el color del borde
    b = max(2, round(0.02 * min(h, w)))
    borde = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3), a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    fondo = color_dominante(borde)
    liso = float((np.abs(borde - fondo).max(axis=1) <= 12).mean())
    if liso >= 0.9:
        tipo_fondo = "sólido"
    else:
        suave = np.abs(np.diff(a[0], axis=0)).mean() + np.abs(np.diff(a[:, 0], axis=0)).mean()
        tipo_fondo = "degradado" if suave < 6 else "foto o textura"
    esquinas = {k: hx(a[sl].reshape(-1, 3).mean(axis=0)) for k, sl in {
        "arriba_izq": (slice(0, b), slice(0, b)), "arriba_der": (slice(0, b), slice(w - b, w)),
        "abajo_izq": (slice(h - b, h), slice(0, b)), "abajo_der": (slice(h - b, h), slice(w - b, w))}.items()}

    res = {
        "archivo": Path(ruta).name, "ancho": W, "alto": H,
        "relacion": f"{W / H:.3f}", "fondo": {"tipo": tipo_fondo, "color": hx(fondo), "esquinas": esquinas},
        "paleta": paleta, "elementos": [], "margenes_pct": None,
    }

    elementos = []
    if tipo_fondo == "sólido":
        mask = np.abs(a - fondo).max(axis=2) > 40
        filas = mask.sum(axis=1) >= 2
        for (y0, y1) in tramos(filas, max(1, round(0.004 * h))):
            cols = mask[y0:y1 + 1].any(axis=0)
            # Un hueco entre palabras de letra grande no separa elementos: el límite crece con la altura de la franja.
            hueco_col = max(round(0.02 * w), min(round(0.5 * (y1 - y0 + 1)), round(0.05 * w)))
            for (c0, c1) in tramos(cols, hueco_col):
                sub = mask[y0:y1 + 1, c0:c1 + 1]
                ys = np.where(sub.any(axis=1))[0]
                yy0, yy1 = y0 + ys[0], y0 + ys[-1]
                sub = mask[yy0:yy1 + 1, c0:c1 + 1]
                caja = a[yy0:yy1 + 1, c0:c1 + 1]
                ancho_c, alto_c = c1 - c0 + 1, yy1 - yy0 + 1
                # En una foto o una caja hay muchas filas con una raya continua casi de lado a lado;
                # en un texto no (las letras dejan huecos).
                llenas = float(np.mean([racha_max(f) >= 0.8 * ancho_c for f in sub]))
                e = {"x0": c0, "y0": yy0, "x1": c1, "y1": yy1}
                if llenas > 0.35 and alto_c > 0.025 * h and ancho_c > 0.05 * w:
                    # Forma rellena: foto o caja de color.
                    tinta = caja[sub]
                    dom = color_dominante(tinta)
                    comparte = float((np.abs(tinta - dom).max(axis=1) <= 14).mean())
                    if comparte > 0.7:
                        e["tipo"] = "caja_de_color"
                        e["relleno"] = hx(dom)
                        e["color_texto_dentro"] = None
                    else:
                        e["tipo"] = "foto"
                        fotos = tramos(sub.any(axis=0), 0)
                        if len(fotos) > 1:
                            e["fotos_en_fila"] = [[round(100 * (c0 + f0) / w, 1), round(100 * (c0 + f1 + 1) / w, 1)] for f0, f1 in fotos]
                    # Esquinas: el borde izquierdo arranca más abajo que el tope del medio.
                    # (Se mide así y no en la fila de arriba, porque un sello encima puede alterarla.)
                    cm = min(ancho_c - 1, int(ancho_c * 0.3))
                    col_medio = np.where(sub[:, max(cm - 1, 0):cm + 2].any(axis=1))[0]
                    col_izq = np.where(sub[:, 0])[0]
                    if not len(col_izq):
                        col_izq = np.where(sub[:, 1])[0]
                    y = float(col_izq[0] - col_medio[0]) if len(col_medio) and len(col_izq) else 0.0
                    # Geometría del arco: en la primera columna (centro a 0,5 px) el borde baja y px => r = y + d + √(2·y·d)
                    r = y + 0.5 + (2 * y * 0.5) ** 0.5 if y > 1 else 0.0
                    e["radio_esquinas_px"] = round(r / esc) if r > 2 else 0
                    if e["tipo"] == "caja_de_color":
                        m = max(int(r) + 2, 3)
                        interior = caja[m:-m, m:-m] if min(caja.shape[:2]) > 2 * m + 2 else None
                        if interior is not None:
                            dif = np.abs(interior - dom).max(axis=2) > 60
                            if dif.any():
                                ys_, xs_ = np.where(dif)
                                e["texto_dentro_ancho_x_alto_px"] = [round((xs_.max() - xs_.min() + 1) / esc), round((ys_.max() - ys_.min() + 1) / esc)]
                                e["color_texto_dentro"] = hx(color_de_tinta(interior[dif], dom))
                    if e["tipo"] == "foto" and len(col_medio):
                        sobresale = col_medio[0]
                        if sobresale > 0.02 * h:
                            e["tope_px"] = round((yy0 + sobresale) / esc)
                            e["sobresale_arriba_px"] = round(sobresale / esc)
                else:
                    e["tipo"] = "texto"
                    e["color"] = hx(color_de_tinta(caja.reshape(-1, 3), fondo))
                elementos.append(e)

        elementos.sort(key=lambda e: (e["y0"], e["x0"]))

        # Juntar líneas de texto seguidas en bloques
        bloques = []
        for e in elementos:
            if e["tipo"] != "texto":
                bloques.append({"tipo": e["tipo"], "elem": [e]})
                continue
            ult = bloques[-1] if bloques else None
            if ult and ult["tipo"] == "texto":
                p = ult["elem"][-1]
                solapa = min(e["x1"], p["x1"]) - max(e["x0"], p["x0"])
                ancho_min = min(e["x1"] - e["x0"], p["x1"] - p["x0"]) or 1
                hueco = e["y0"] - p["y1"]
                alto_min = min(e["y1"] - e["y0"], p["y1"] - p["y0"]) + 1
                if solapa / ancho_min > 0.5 and hueco < 0.9 * alto_min:
                    ult["elem"].append(e)
                    continue
            bloques.append({"tipo": "texto", "elem": [e]})

        for n, bl in enumerate(bloques, 1):
            es = bl["elem"]
            x0, y0 = min(e["x0"] for e in es), min(e["y0"] for e in es)
            x1, y1 = max(e["x1"] for e in es), max(e["y1"] for e in es)
            d = {
                "n": n, "tipo": bl["tipo"],
                "x_pct": [round(100 * x0 / w, 1), round(100 * (x1 + 1) / w, 1)],
                "y_pct": [round(100 * y0 / h, 1), round(100 * (y1 + 1) / h, 1)],
                "caja_px": [round(x0 / esc), round(y0 / esc), round((x1 + 1) / esc), round((y1 + 1) / esc)],
                "ancho_px": round((x1 - x0 + 1) / esc), "alto_px": round((y1 - y0 + 1) / esc),
            }
            if bl["tipo"] == "texto":
                alto_linea = float(np.median([e["y1"] - e["y0"] + 1 for e in es])) / esc
                d.update({"lineas": len(es),
                          "lineas_ancho_x_alto_px": [[round((e["x1"] - e["x0"] + 1) / esc), round((e["y1"] - e["y0"] + 1) / esc)] for e in es],
                          "color": es[0]["color"], "alto_de_linea_px": round(alto_linea),
                          "alto_de_linea_pct_ancho": round(100 * alto_linea / W, 1)})
                if len(es) > 1:
                    paso = float(np.mean([es[i + 1]["y0"] - es[i]["y0"] for i in range(len(es) - 1)])) / esc
                    d["interlineado_px"] = round(paso)
                    d["tamano_letra_estimado_px"] = round(paso / 1.15)
                else:
                    d["tamano_letra_estimado_px"] = round(alto_linea / 0.95)
                cx = [((e["x0"] + e["x1"]) / 2) / w for e in es]
                izq = [e["x0"] / w for e in es]
                der = [e["x1"] / w for e in es]
                if len(es) > 1 and max(cx) - min(cx) < 0.02:
                    d["alineacion"] = "centrada"
                elif max(izq) - min(izq) < 0.015:
                    d["alineacion"] = "izquierda" if len(es) > 1 or abs(cx[0] - 0.5) > 0.03 else "centrada o izquierda (una sola línea)"
                elif max(der) - min(der) < 0.015:
                    d["alineacion"] = "derecha"
                else:
                    d["alineacion"] = "mixta"
            else:
                for k in ("radio_esquinas_px", "relleno", "color_texto_dentro", "texto_dentro_ancho_x_alto_px", "fotos_en_fila", "tope_px", "sobresale_arriba_px"):
                    if k in es[0]:
                        d[k] = es[0][k]
            res["elementos"].append(d)

        if elementos:
            res["margenes_pct"] = {
                "izquierda": round(100 * min(e["x0"] for e in elementos) / w, 1),
                "derecha": round(100 * (w - 1 - max(e["x1"] for e in elementos)) / w, 1),
                "arriba_del_alto": round(100 * min(e["y0"] for e in elementos) / h, 1),
                "abajo_del_alto": round(100 * (h - 1 - max(e["y1"] for e in elementos)) / h, 1),
            }
    return im, res


def dibujar(im, res, salida):
    W, H = im.size
    img = im.convert("RGBA")
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    try:
        fuente = ImageFont.load_default(size=max(14, W // 60))
    except TypeError:
        fuente = ImageFont.load_default()
    for i in range(1, 10):
        d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(128, 128, 128, 90), width=1)
        d.line([(0, H * i / 10), (W, H * i / 10)], fill=(128, 128, 128, 90), width=1)
        d.text((W * i / 10 + 3, 3), f"{i * 10}", fill=(128, 128, 128, 220), font=fuente)
        d.text((3, H * i / 10 + 3), f"{i * 10}", fill=(128, 128, 128, 220), font=fuente)
    colores = {"texto": (230, 40, 40, 255), "foto": (40, 90, 230, 255), "caja_de_color": (30, 170, 70, 255)}
    for e in res["elementos"]:
        x0, y0, x1, y1 = e["caja_px"]
        c = colores.get(e["tipo"], (200, 0, 200, 255))
        d.rectangle([x0, y0, x1, y1], outline=c, width=max(2, W // 400))
        tam = getattr(fuente, "size", 14)
        ancho_et, alto_et = tam * 1.6, tam * 1.3
        # La etiqueta va afuera de la caja (a la izquierda o arriba) para no tapar el contenido.
        ex, ey = (x0 - ancho_et - 3, y0) if x0 > ancho_et + 4 else (x0, max(0, y0 - alto_et - 2))
        d.rectangle([ex, ey, ex + ancho_et, ey + alto_et], fill=c)
        d.text((ex + 4, ey), str(e["n"]), fill=(255, 255, 255, 255), font=fuente)
    Image.alpha_composite(img, capa).convert("RGB").save(salida)


def imprimir(res):
    print(f"Imagen: {res['ancho']} × {res['alto']} px (ancho/alto = {res['relacion']})")
    f = res["fondo"]
    print(f"Fondo: {f['tipo']} {f['color']}" + ("" if f["tipo"] == "sólido" else f"  esquinas: {f['esquinas']}"))
    print("Paleta: " + ", ".join(f"{p['color']} ({p['pct']}%)" for p in res["paleta"]))
    if res["margenes_pct"]:
        m = res["margenes_pct"]
        print(f"Márgenes: izquierda {m['izquierda']}% · derecha {m['derecha']}% del ancho · "
              f"arriba {m['arriba_del_alto']}% · abajo {m['abajo_del_alto']}% del alto")
    if not res["elementos"]:
        print("\nNo pude separar elementos automáticamente (el fondo no es liso). "
              "Mirá analisis.png: tiene una grilla del 10% para medir a ojo.")
        return
    print("\nElementos de arriba hacia abajo:")
    for e in res["elementos"]:
        base = f"{e['n']:>2}. {e['tipo'].upper():<13} x {e['x_pct'][0]}–{e['x_pct'][1]}% · y {e['y_pct'][0]}–{e['y_pct'][1]}% · {e['ancho_px']}×{e['alto_px']} px"
        if e["tipo"] == "texto":
            extra = f" · {e['lineas']} línea(s) · letra ≈ {e['tamano_letra_estimado_px']} px"
            if "interlineado_px" in e:
                extra += f" · interlineado {e['interlineado_px']} px"
            extra += f" · color {e['color']} · {e['alineacion']}"
            if e["lineas"] > 1 or e["ancho_px"] > 0:
                extra += "\n      cada línea (ancho × alto px): " + ", ".join(f"{a}×{b}" for a, b in e["lineas_ancho_x_alto_px"])
        elif e["tipo"] == "caja_de_color":
            extra = f" · relleno {e['relleno']} · esquinas {e['radio_esquinas_px']} px"
            if e.get("texto_dentro_ancho_x_alto_px"):
                extra += f"\n      texto dentro: {e['texto_dentro_ancho_x_alto_px'][0]}×{e['texto_dentro_ancho_x_alto_px'][1]} px, color {e['color_texto_dentro']}"
        else:
            extra = f" · esquinas redondeadas ≈ {e.get('radio_esquinas_px', 0)} px"
            if e.get("sobresale_arriba_px"):
                extra += f" · ¡algo sobresale {e['sobresale_arriba_px']} px por arriba (sello o insignia)! La foto en sí empieza en y = {e['tope_px']} px"
            if e.get("fotos_en_fila"):
                extra += f" · {len(e['fotos_en_fila'])} fotos en fila: {e['fotos_en_fila']}"
        print(base + extra)
    print("\nLas medidas son aproximadas. Mirá analisis.png y ajustá la plantilla con comparar.py.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ruta = Path(sys.argv[1])
    im, res = analizar(ruta)
    dibujar(im, res, ruta.with_name("analisis.png"))
    ruta.with_name("analisis.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    imprimir(res)


if __name__ == "__main__":
    main()
