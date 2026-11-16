"""Versión 3: ganchos reforzados, tapa para el lugar del mate, adaptador para termos chicos y topes del riel.
Reutiliza las funciones de generar_v2.py. Todas las piezas son watertight y de una sola pieza."""
import json
import numpy as np
import manifold3d as m3
from shapely.geometry import Polygon
from generar_v2 import (OUT, poly_to_cs, extrude, cyl, to_trimesh, printed_grams,
                        LIP, CHAN, RAIL_H, SEG)

def tri_gusset_yz(W, s):
    """Refuerzo triangular entre tira y brazo. Triángulo en (y,z) con catetos s, extruido W en X (centrado)."""
    # poly en (u=y, v=z), extruido en w. Mapeo: X=w, Y=u, Z=v
    tri = Polygon([(0, 0), (s, 0), (0, s)])
    m = extrude(tri, W, 0.0)
    m = m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])
    return m.translate([-W/2, 0, 0])

def hanger_v3(L=130.0, W=30.0, T=12.0, arm=46.0):
    """Gancho reforzado: tira 30x12x130, brazo de 46, refuerzo triangular de 16 mm en la unión,
    anilla con pared de 6.5 mm (ID 17) y pie en T con tope que entra en el riel."""
    strap = m3.Manifold.cube([W, T, L]).translate([-W/2, 0, 0])
    armm = m3.Manifold.cube([W, arm, T]).translate([-W/2, 0, L - T])
    gus = tri_gusset_yz(W, 16.0).translate([0, 0, L - T - 16.0 + 0.0])
    ring = cyl(W/2, T, 0, arm, L - T, 72) - cyl(8.5, T + 2, 0, arm, L - T - 1, 72)
    stem = m3.Manifold.cube([W, LIP + 0.3, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3), 0.0])
    foot = m3.Manifold.cube([W, CHAN - 0.4, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3) - (CHAN - 0.4), 0.0])
    return strap + armm + gus + ring + stem + foot

def hanger_v3_print():
    h = hanger_v3().rotate([0, 90, 0])
    bb = h.bounding_box()
    return h.translate([-bb[0], -bb[1], -bb[2]])

def tapa_mate(d=88.0, clear=0.6, plug_h=9.0, flange_t=3.0):
    """Tapa que entra en el bolsillo del mate: tapón de Ø d-2*clear con reborde superior y muesca para el dedo."""
    r = d/2 - clear
    plug = cyl(r, plug_h, 0, 0, 0, SEG)
    flange = cyl(d/2 + 2.0, flange_t, 0, 0, plug_h - flange_t, SEG)
    tab = m3.Manifold.cube([16.0, 10.0, flange_t + 2]).translate([-8, d/2 - 2, plug_h - flange_t - 1])
    lid = plug + flange - cyl(7.0, 4, 0, d/2 + 2.0 - 0.0, plug_h - 1, 40).translate([0, 0, 0])
    lid = plug + flange
    # muesca para el dedo en el borde del reborde
    notch = m3.Manifold.cube([18.0, 8.0, flange_t + 1]).translate([-9, d/2 - 1.0, plug_h - flange_t - 0.5])
    return lid - notch

def adaptador_termo_chico(d_pocket=96.0, clear=0.9, h=60.0, floor=5.0):
    """Manga que entra en el bolsillo de termo grande y centra un termo chico (Ø 70 a 72 mm).
    Cuatro costillas de 3 mm salen de la pared interior. Fondo con orificio de drenaje."""
    R = d_pocket/2 - clear          # radio exterior
    ri = 39.0                       # radio interior de la pared
    body = cyl(R, h, 0, 0, 0, SEG) - cyl(ri, h + 2, 0, 0, floor, SEG)
    ribs = None
    for k in range(4):
        ang = k * 90.0 + 45.0
        rib = m3.Manifold.cube([4.0, 6.0, h - floor]).translate([ri - 3.0, -3.0, floor])
        rib = rib.rotate([0, 0, ang])
        ribs = rib if ribs is None else ribs + rib
    body = body + ribs - cyl(4.0, floor + 2, 0, 0, -1, 32)
    return body

def tope_riel(length=12.0):
    """Tope que se coloca en el extremo del riel para que el gancho no se deslice hacia afuera.
    Va dentro del canal de 5,4 mm, con 0,3 mm de holgura para entrar a presión."""
    return m3.Manifold.cube([length, CHAN - 0.3, RAIL_H - 1.2]).translate([0, 0, 0])

if __name__ == "__main__":
    res = {}
    pieces = [
        ("gancho_v3_imprimir_x2", hanger_v3_print()),
        ("tapa_mate", tapa_mate()),
        ("adaptador_termo_chico", adaptador_termo_chico()),
        ("tope_riel_imprimir_x4", tope_riel()),
    ]
    for name, man in pieces:
        tm = to_trimesh(man)
        assert tm.is_watertight, name
        assert len(tm.split(only_watertight=False)) == 1, name + " no es una sola pieza"
        tm.export(f"{OUT}/{name}.stl")
        g = printed_grams(man)
        res[name] = dict(bbox_mm=[round(float(v), 1) for v in tm.bounds[1] - tm.bounds[0]], printed_g=round(g))
        print(name, res[name], flush=True)
    json.dump(res, open(f"{OUT}/_estimaciones_v3.json", "w"), indent=1)
