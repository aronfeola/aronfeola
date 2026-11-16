"""Gancho v5 (el más potente): tira 40x18x130, refuerzo de 26 mm, anilla de 40 mm de OD y 17 de ID.
Módulo de sección de la tira 2,4 veces el de la v3. Imprimir de canto, 40 % gyroid, 6 perímetros."""
import json
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, LIP, CHAN, RAIL_H
from generar_v3_accesorios import tri_gusset_yz
import manifold3d as m3

W, T, L, ARM, GUS = 40.0, 18.0, 130.0, 46.0, 26.0
def hanger_v5():
    strap = m3.Manifold.cube([W, T, L]).translate([-W/2, 0, 0])
    arm = m3.Manifold.cube([W, ARM, T]).translate([-W/2, 0, L - T])
    gus = tri_gusset_yz(W, GUS).translate([0, 0, L - T - GUS])
    ring = cyl(W/2, T, 0, ARM, L - T, 72) - cyl(8.5, T + 2, 0, ARM, L - T - 1, 72)
    stem = m3.Manifold.cube([W, LIP + 0.3, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3), 0.0])
    foot = m3.Manifold.cube([W, CHAN - 0.4, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3) - (CHAN - 0.4), 0.0])
    return strap + arm + gus + ring + stem + foot
if __name__ == "__main__":
    h = hanger_v5().rotate([0, 90, 0]); bb = h.bounding_box()
    h = h.translate([-bb[0], -bb[1], -bb[2]])
    tm = to_trimesh(h); assert tm.is_watertight and len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/gancho_v5_potente_imprimir_x2.stl")
    Z = W*T*T/6
    out = dict(printed_g_each_40pct=round(printed_grams(h, infill=0.40)), section_v5=round(Z),
               gain_vs_v3=round(Z/720, 2), stress_5g_MPa=round(5250/Z, 1))
    print(out); json.dump(out, open(f"{OUT}/_estimaciones_gancho_v5.json","w"), indent=1)
