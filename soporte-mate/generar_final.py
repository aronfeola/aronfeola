"""Set FINAL del soporte de mate CLEAMS (caja A + ganchos + topes).
Cambios frente a v2-v5:
- El riel recto se reemplaza por una cuña a 45° (tipo french cleat): el peso traba la caja contra el gancho
  y no puede salirse hacia adelante. Se imprime sin soportes.
- Gancho con pie en cuña, tira 40x18 y cabeza cuadrada (apoya plana en la cama).
- Estimador de peso corregido (antes contaba los huecos de los bolsillos como material).
"""
import json, sys
import numpy as np
import manifold3d as m3
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from generar_v2 import (poly_to_cs, extrude, cyl, rrect, logo_2d, to_trimesh, A_POCKETS, A_BOMB, scaled,
                        FLUTE_R, FLUTE_PITCH, FLUTE_DEPTH, SEG, LOGO_Z, RIGHT_MARGIN)

OUT = "/home/user/aronfeola/soporte-mate/final"
WALL, FLOOR = 4.0, 5.0
CLEAT_D, CLEAT_H, CLEAT_TOP = 8.8, 24.0, 14.0      # profundidad, alto de la cuña y material por encima
PLATE_BACK = 12.0
LOGO_RELIEF = 0.8
FLUTES = False                                       # exterior liso
DENS = 1.27                                          # PETG g/cm3

def prism_yz(pts, W):
    """Polígono en (y,z) extruido W a lo largo de X, centrado en X."""
    m = extrude(Polygon(pts), W, 0.0).transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])
    return m.translate([-W/2, 0, 0])

def grams(man, walls=1.6, infill=0.10, skin=1.0, step=1.0):
    """Peso impreso: perímetros sólidos + pieles sólidas (toda zona sin material a 'skin' mm arriba o abajo) + relleno."""
    bb = man.bounding_box(); z0, z1 = bb[2], bb[5]; vol = 0.0
    for z in np.arange(z0 + step/2, z1, step):
        cs = man.slice(z); a = cs.area()
        inner = cs.offset(-walls, m3.JoinType.Round)
        for zz in (z + skin, z - skin):
            inner = inner ^ man.slice(zz) if z0 < zz < z1 else m3.CrossSection()
        ai = inner.area()
        vol += ((a - ai) + ai * infill) * step
    return vol / 1000.0 * DENS

def build_box(pockets, bombilla):
    CORNER = 12.0
    shapes, depths = [], []
    for p in pockets:
        shapes.append(Point(p["x"], p["y"]).buffer(p["d"]/2, resolution=SEG//4)); depths.append(p["depth"])
    bx, by, bw, bl, bdepth = bombilla
    shapes.append(rrect(bx, by, bw, bl, bw/2 - 0.01)); depths.append(bdepth)
    H = max(depths) + FLOOR
    x0, y0, x1, y1 = unary_union(shapes).bounds
    x0 -= WALL; x1 += WALL; y0 -= WALL + PLATE_BACK; y1 += WALL
    outline = box(x0 + CORNER, y0, x1 - CORNER, y1).union(box(x0, y0, x1, y1 - CORNER)).union(unary_union(
        [Point(x0 + CORNER, y1 - CORNER).buffer(CORNER, resolution=16), Point(x1 - CORNER, y1 - CORNER).buffer(CORNER, resolution=16)]))
    body = extrude(outline, H)
    ext = outline.exterior; L = ext.length; n = int(L // FLUTE_PITCH); flutes = None
    for i in range(n):
        d = i * L / n; pt = ext.interpolate(d)
        if pt.y < y0 + 0.5: continue
        a = ext.interpolate((d - 0.5) % L); b = ext.interpolate((d + 0.5) % L)
        nrm = np.array([b.y - a.y, -(b.x - a.x)]); nrm /= np.linalg.norm(nrm)
        if outline.contains(Point(pt.x + nrm[0]*0.6, pt.y + nrm[1]*0.6)): nrm = -nrm
        c = m3.Manifold.cylinder(H - 6.0, FLUTE_R, FLUTE_R, 20).translate(
            [pt.x + nrm[0]*(FLUTE_R - FLUTE_DEPTH), pt.y + nrm[1]*(FLUTE_R - FLUTE_DEPTH), 3.0])
        flutes = c if flutes is None else flutes + c
    if FLUTES: body = body - flutes
    for shp, dep in zip(shapes, depths):
        body = body - extrude(shp, dep + 5, H - dep)
        c = shp.centroid
        body = body - cyl(4.0 if shp.area > 1000 else 2.5, H - dep + 2, c.x, c.y, -1)
    # cuña a 45° en la espalda: techo bajo en la cara, alto en el fondo
    zt = H - CLEAT_TOP; zb = zt - CLEAT_H
    cav = prism_yz([(y0 - 1, zb), (y0 + CLEAT_D, zb), (y0 + CLEAT_D, zt), (y0 - 1, zt - CLEAT_D - 1)], x1 - x0 + 4)
    body = body - cav.translate([(x0 + x1)/2, 0, 0])
    # logo en relieve, abajo a la derecha visto de frente (espejado en X para leerse bien)
    lg = affinity.scale(logo_2d(), -1, 1, origin=(0, 0)); lw = lg.bounds[2] - lg.bounds[0]
    lg = affinity.translate(lg, x0 + CORNER + RIGHT_MARGIN + lw, LOGO_Z)
    body = body + extrude(lg, LOGO_RELIEF + 0.6, 0).rotate([90, 0, 0]).translate([0, y1 + LOGO_RELIEF, 0])
    return body.translate([-(x0 + x1)/2, -(y0 + y1)/2, 0]), H

HW, HT, HL, ARM, GUS = 40.0, 18.0, 130.0, 46.0, 16.0   # GUS <= ARM-HT-10.5 para no tapar el poste
def foot_pts(clear_d, h):
    Df = CLEAT_D - clear_d
    return [(0.5, 0), (-Df, 0), (-Df, h), (0.5, h - Df - 0.5)]

def hanger():
    strap = m3.Manifold.cube([HW, HT, HL]).translate([-HW/2, 0, 0])
    arm = m3.Manifold.cube([HW, ARM, HT]).translate([-HW/2, 0, HL - HT])
    gus = prism_yz([(HT, HL - HT), (HT, HL - HT - GUS), (HT + GUS, HL - HT)], HW)
    head = m3.Manifold.cube([HW, HW, HT]).translate([-HW/2, ARM - HW/2, HL - HT])
    foot = prism_yz(foot_pts(0.5, CLEAT_H - 1.2), HW)
    hole = cyl(8.5, HT + 2, 0, ARM, HL - HT - 1, 72)     # se resta al final: el brazo no debe tapar el agujero
    return strap + arm + gus + head + foot - hole

def as_printed(man):
    h = man.rotate([0, 90, 0]); bb = h.bounding_box()
    return h.translate([-bb[0], -bb[1], -bb[2]])

def tope():
    return as_printed(prism_yz(foot_pts(0.25, CLEAT_H - 0.4), 12.0))

if __name__ == "__main__":
    K = 0.68
    pk, bb = scaled(A_POCKETS, A_BOMB, K)
    boxm, H = build_box(pk, bb)
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        for w in (1.6, 2.0, 2.4):
            print("perimetros mm", w, {i: round(grams(boxm, walls=w, infill=i, skin=1.2)) for i in (0.08, 0.10, 0.12, 0.15)}, flush=True)
        sys.exit()
    res = {}
    for name, man, kw in (("caja_A", boxm, dict(walls=2.0, infill=0.08, skin=1.2)),
                          ("gancho_x2", as_printed(hanger()), dict(walls=2.4, infill=0.40)),
                          ("tope_riel_x4", tope(), dict(walls=1.6, infill=0.40))):
        tm = to_trimesh(man)
        assert tm.is_watertight and len(tm.split(only_watertight=False)) == 1, name
        tm.export(f"{OUT}/{name}.stl")
        res[name] = dict(bbox=[round(float(v), 1) for v in tm.bounds[1] - tm.bounds[0]], g=round(grams(man, **kw)), **kw)
        print(name, res[name], flush=True)
    json.dump(res, open(f"{OUT}/_pesos.json", "w"), indent=1)
