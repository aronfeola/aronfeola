"""Retenedor del mate v4: manga que entra en el bolsillo de 88 mm, con labio superior que impide que el mate se levante
al inclinarse el auto, y cuatro costillas internas que lo centran y lo sujetan. Supone un mate de Ø ~78 mm (medir el tuyo)."""
import json
import numpy as np
import manifold3d as m3
from generar_v2 import OUT, cyl, to_trimesh, printed_grams, SEG

HOLE_D = 88.0
CLEAR = 0.6
R_OUT = HOLE_D/2 - CLEAR      # 43.4
R_IN = 39.0                   # radio interior (Ø 78)
H = 44.0                      # largo de la manga (entra en ambos bolsillos: 41,3 y 47,6)
FLOOR = 4.0
LIP_IN = 4.0                  # labio que entra hacia el centro en la parte superior
LIP_H = 6.0

def retenedor():
    body = cyl(R_OUT, H, 0, 0, 0, SEG) - cyl(R_IN, H + 2, 0, 0, FLOOR, SEG)
    # labio superior hacia adentro
    lip = cyl(R_IN, LIP_H, 0, 0, H - LIP_H, SEG) - cyl(R_IN - LIP_IN, LIP_H + 2, 0, 0, H - LIP_H - 1, SEG)
    ribs = None
    for k in range(4):
        rib = m3.Manifold.cube([3.0, 6.0, H - FLOOR - 2]).translate([R_IN - 3.0, -3.0, FLOOR])
        rib = rib.rotate([0, 0, k * 90.0 + 45.0])
        ribs = rib if ribs is None else ribs + rib
    return body + lip + ribs - cyl(4.0, FLOOR + 2, 0, 0, -1, 32)

if __name__ == "__main__":
    man = retenedor()
    tm = to_trimesh(man)
    assert tm.is_watertight
    assert len(tm.split(only_watertight=False)) == 1
    tm.export(f"{OUT}/retenedor_mate_v4.stl")
    out = dict(outer_d=round(2*R_OUT, 1), inner_d=round(2*R_IN, 1), height=H, printed_g=round(printed_grams(man)))
    print(out)
    json.dump(out, open(f"{OUT}/_estimaciones_retenedor_mate.json", "w"), indent=1)
