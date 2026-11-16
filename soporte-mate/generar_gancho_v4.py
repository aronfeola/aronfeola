"""Gancho v4 reforzado: tira 34x14x130, refuerzo de 22 mm, anilla con pared de 8 mm. Misma orientación de impresión (de canto).
Compara el módulo de sección con la versión 3."""
import json
import numpy as np
import manifold3d as m3
from shapely.geometry import Polygon
from generar_v2 import OUT, extrude, cyl, to_trimesh, printed_grams, LIP, CHAN, RAIL_H
from generar_v3_accesorios import tri_gusset_yz

W, T, L, ARM = 34.0, 14.0, 130.0, 46.0
GUS = 22.0
RING_OD, RING_ID = W, 17.0

def hanger_v4():
    strap = m3.Manifold.cube([W, T, L]).translate([-W/2, 0, 0])
    arm = m3.Manifold.cube([W, ARM, T]).translate([-W/2, 0, L - T])
    gus = tri_gusset_yz(W, GUS).translate([0, 0, L - T - GUS])
    ring = cyl(RING_OD/2, T, 0, ARM, L - T, 72) - cyl(RING_ID/2, T + 2, 0, ARM, L - T - 1, 72)
    stem = m3.Manifold.cube([W, LIP + 0.3, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3), 0.0])
    foot = m3.Manifold.cube([W, CHAN - 0.4, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3) - (CHAN - 0.4), 0.0])
    return strap + arm + gus + ring + stem + foot

def hanger_v4_print():
    h = hanger_v4().rotate([0, 90, 0])
    bb = h.bounding_box()
    return h.translate([-bb[0], -bb[1], -bb[2]])

if __name__ == "__main__":
    man = hanger_v4_print()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/gancho_v4_imprimir_x2.stl")
    sec_v3 = 30*12**2/6; sec_v4 = W*T**2/6
    out = dict(printed_g_each=round(printed_grams(man)), section_modulus_v3_mm3=round(sec_v3),
               section_modulus_v4_mm3=round(sec_v4), gain=round(sec_v4/sec_v3, 2),
               bending_stress_5g_MPa=round(5250/sec_v4, 1))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_gancho_v4.json", "w"), indent=1)
