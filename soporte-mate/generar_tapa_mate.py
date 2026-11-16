"""Tapa del mate v4: tapón a presión (Ø 87,2 en un hueco de 88) con agarre alto.
Altura por encima de la caja: 140 mm (más que un mate grande). Tapón de 41 mm, que entra en ambos bolsillos."""
import json
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, SEG
import manifold3d as m3

MATE_D = 88.0
CLEAR_RAD = 0.4            # 0,4 mm por lado: ajuste a presión suave
PLUG_R = MATE_D/2 - CLEAR_RAD
PLUG_H = 41.0              # entra en el bolsillo del mate de ambas cajas (41,3 y 47,6 mm)
ROD_R = 18.0
ROD_H = 140.0
KNOB_R = 26.0
KNOB_H = 14.0

def tapa():
    plug = cyl(PLUG_R, PLUG_H, 0, 0, 0, SEG)
    # pequeño chaflán en la base del tapón para que entre sin trabarse
    chamfer = m3.Manifold.cylinder(1.5, PLUG_R - 1.5, PLUG_R, SEG).translate([0, 0, 0])
    rod = cyl(ROD_R, ROD_H, 0, 0, PLUG_H - 1.0, 64)
    knob = cyl(KNOB_R, KNOB_H, 0, 0, PLUG_H + ROD_H - 1.0, 96)
    return plug + rod + knob

if __name__ == "__main__":
    man = tapa()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/tapa_mate_v4.stl")
    g = printed_grams(man)
    bb = tm.bounds[1] - tm.bounds[0]
    out = dict(plug_d=round(2*PLUG_R, 1), hole_d=MATE_D, total_h=round(float(bb[2]), 1),
               above_box_mm=ROD_H + KNOB_H - 1.0, printed_g=round(g))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_tapa_v4.json", "w"), indent=1)
