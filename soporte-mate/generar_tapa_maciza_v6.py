"""Tapa maciza v6 de encastre a presión, tipo tapa WD-40. Pensada para imprimir al 100 % de relleno.
Tapón de Ø 87,2 con bisel de entrada, reborde de encastre, disco superior de 6 mm y muesca para el dedo."""
import json
import manifold3d as m3
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, SEG

HOLE_D = 88.0
PLUG_R = HOLE_D/2 - 0.4        # 0,4 mm por lado
PLUG_H = 14.0
TOP_R = 46.0
TOP_T = 6.0
BEAD_R = PLUG_R + 0.8
BEAD_H = 2.5
CHAMFER = 2.0

def tapa():
    # tapón con bisel en la punta (entrada suave)
    plug = cyl(PLUG_R, PLUG_H - CHAMFER, 0, 0, CHAMFER, SEG)
    lead = m3.Manifold.cylinder(CHAMFER, PLUG_R - CHAMFER, PLUG_R, SEG).translate([0, 0, 0])
    bead = cyl(BEAD_R, BEAD_H, 0, 0, PLUG_H * 0.45, SEG)
    top = cyl(TOP_R, TOP_T, 0, 0, PLUG_H, SEG)
    notch = m3.Manifold.cube([16.0, 8.0, TOP_T + 1]).translate([-8, TOP_R - 6.0, PLUG_H - 1.0])
    return plug + lead + bead + top - notch

if __name__ == "__main__":
    man = tapa()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/tapa_mate_maciza_v6.stl")
    g100 = printed_grams(man, infill=1.0)
    out = dict(plug_d=round(2*PLUG_R, 1), top_d=2*TOP_R, total_h=PLUG_H + TOP_T,
               printed_g_100pct=round(g100), printed_g_10pct=round(printed_grams(man)))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_tapa_v6.json", "w"), indent=1)
