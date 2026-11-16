"""Tapa del mate v5: tapa corta de encastre a presión. Tapón de Ø 87,2 que entra en el hueco de 88 mm
y disco superior de Ø 92 que queda apoyado sobre la caja. Sin barra alta."""
import json
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, SEG
import manifold3d as m3

HOLE_D = 88.0
PLUG_R = HOLE_D/2 - 0.4       # 0,4 mm por lado: encastre a presión
PLUG_H = 10.0                 # tapón que entra en el hueco
TOP_R = 46.0                  # disco de apoyo, Ø 92
TOP_T = 4.0
BEAD_R = PLUG_R + 0.6         # reborde de encastre en la mitad del tapón
BEAD_H = 2.0

def tapa():
    plug = cyl(PLUG_R, PLUG_H, 0, 0, 0, SEG)
    bead = cyl(BEAD_R, BEAD_H, 0, 0, PLUG_H * 0.5, SEG)
    top = cyl(TOP_R, TOP_T, 0, 0, PLUG_H, SEG)
    notch = m3.Manifold.cube([16.0, 8.0, TOP_T + 1]).translate([-8, TOP_R - 6.0, PLUG_H - 0.5])
    return plug + bead + top - notch

if __name__ == "__main__":
    man = tapa()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/tapa_mate_encastre_v5.stl")
    out = dict(plug_d=round(2*PLUG_R, 1), top_d=2*TOP_R, total_h=round(PLUG_H + TOP_T, 1),
               printed_g=round(printed_grams(man)))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_tapa_v5.json", "w"), indent=1)
