"""Tapa nervada v7: tapa maciza que baja hasta el fondo del bolsillo del mate (41 mm, entra en ambos modelos),
con nervaduras verticales en el costado para encastrar a presión y agarrar, y disco superior de Ø 92."""
import json
import math
import manifold3d as m3
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, SEG

HOLE_D = 88.0
R_LAND = HOLE_D/2 - 0.2        # crestas de las nervaduras: 0,2 mm de holgura, ajuste a presión
GROOVE_D = 1.0
N_GROOVES = 36
PLUG_H = 41.0
TOP_R, TOP_T = 46.0, 6.0
CHAMFER = 2.0

def tapa():
    plug = cyl(R_LAND, PLUG_H, 0, 0, 0, SEG)
    for k in range(N_GROOVES):
        a = 2 * math.pi * k / N_GROOVES
        g = m3.Manifold.cube([GROOVE_D*2, 2.0, PLUG_H + 2]).translate([R_LAND - GROOVE_D, -1.0, -1.0])
        plug = plug - g.rotate([0, 0, math.degrees(a)])
    top = cyl(TOP_R, TOP_T, 0, 0, PLUG_H, SEG)
    notch = m3.Manifold.cube([16.0, 8.0, TOP_T + 1]).translate([-8, TOP_R - 6.0, PLUG_H - 1.0])
    return plug + top - notch

if __name__ == "__main__":
    man = tapa()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/tapa_mate_nervada_v7.stl")
    out = dict(land_d=round(2*R_LAND,1), top_d=2*TOP_R, total_h=PLUG_H+TOP_T,
               printed_g_100pct=round(printed_grams(man, infill=1.0)),
               printed_g_40pct=round(printed_grams(man, infill=0.40)))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_tapa_v7.json", "w"), indent=1)
