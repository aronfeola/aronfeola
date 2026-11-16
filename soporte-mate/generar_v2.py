"""Soporte para kit de mate, versión 2.
Paredes gruesas, logo CLEAMS en relieve abajo a la derecha (vista de frente), variante rectangular y redonda.
Genera STL watertight de una sola pieza y estima el peso impreso (PETG, 4 perímetros, 10 % gyroid)."""
import json, sys
import numpy as np
import manifold3d as m3
from shapely import affinity
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import trimesh

OUT = "/home/user/aronfeola/soporte-mate"
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
WALL = 4.0
FLOOR = 5.0
BACK_T = 12.0
LIP, CHAN, RAIL_H = 3.4, 5.4, 24.0
FLUTE_R, FLUTE_PITCH, FLUTE_DEPTH = 2.2, 6.0, 1.0
SEG = 96
PERIM_MM, INFILL = 1.6, 0.10
LOGO_H, LOGO_RELIEF = 12.0, 1.2
LOGO_Z = 9.0            # altura de la base del logo
RIGHT_MARGIN = 8.0      # margen del logo al borde derecho visto de frente

def poly_to_cs(poly):
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    rings = []
    for p in polys:
        rings.append(np.array(p.exterior.coords[:-1], dtype=np.float64))
        for i in p.interiors:
            rings.append(np.array(i.coords[:-1], dtype=np.float64))
    return m3.CrossSection(rings, m3.FillRule.EvenOdd)

def extrude(poly, h, z0=0.0):
    return poly_to_cs(poly).extrude(h).translate([0, 0, z0])

def cyl(r, h, x, y, z0=0.0, seg=SEG):
    return m3.Manifold.cylinder(h, r, r, seg).translate([x, y, z0])

def rrect(cx, cy, w, h, r):
    return box(cx - w/2 + r, cy - h/2 + r, cx + w/2 - r, cy + h/2 - r).buffer(r, join_style=1, resolution=16)

def logo_2d():
    """CLEAMS como polígono 2D, altura de letra LOGO_H, leyendo de izquierda a derecha en el plano XY."""
    tp = TextPath((0, 0), "CLEAMS", size=100, prop=FontProperties(fname=FONT))
    shape = Polygon()
    for ring in tp.to_polygons(closed_only=True):
        if len(ring) >= 3:
            shape = shape.symmetric_difference(Polygon(ring).buffer(0))
    minx, miny, maxx, maxy = shape.bounds
    s = LOGO_H / (maxy - miny)
    shape = affinity.scale(shape, s, s, origin=(0, 0))
    minx, miny, maxx, maxy = shape.bounds
    return affinity.translate(shape, -minx, -miny)

def build(pockets, bombilla, round_r=None):
    CORNER = 12.0
    shapes, depths = [], []
    for p in pockets:
        shapes.append(Point(p["x"], p["y"]).buffer(p["d"]/2, resolution=SEG//4)); depths.append(p["depth"])
    bx, by, bw, bl, bdepth = bombilla
    shapes.append(rrect(bx, by, bw, bl, bw/2 - 0.01)); depths.append(bdepth)
    H = max(depths) + FLOOR
    x0, y0, x1, y1 = unary_union(shapes).bounds
    PLATE_BACK = LIP + CHAN + 3.2
    x0 -= WALL; x1 += WALL; y0 -= WALL + PLATE_BACK; y1 += WALL
    if round_r:
        R = round_r
        outline = box(x0 + R, y0 + R, x1 - R, y1 - R).buffer(R, resolution=24)
        front_flat_x0 = x0 + R
    else:
        outline = box(x0 + CORNER, y0, x1 - CORNER, y1).union(box(x0, y0, x1, y1 - CORNER)).union(
            unary_union([Point(x0 + CORNER, y1 - CORNER).buffer(CORNER, resolution=16),
                         Point(x1 - CORNER, y1 - CORNER).buffer(CORNER, resolution=16)]))
        front_flat_x0 = x0 + CORNER
    full2d = outline
    body = extrude(outline, H)

    ext = full2d.exterior
    L = ext.length; n = int(L // FLUTE_PITCH)
    flutes = None
    for i in range(n):
        d = i * L / n
        pt = ext.interpolate(d)
        if pt.y < y0 + 0.5: continue
        a = ext.interpolate((d - 0.5) % L); b = ext.interpolate((d + 0.5) % L)
        nrm = np.array([b.y - a.y, -(b.x - a.x)]); nrm /= np.linalg.norm(nrm)
        if full2d.contains(Point(pt.x + nrm[0]*0.6, pt.y + nrm[1]*0.6)): nrm = -nrm
        cx, cy = pt.x + nrm[0]*(FLUTE_R - FLUTE_DEPTH), pt.y + nrm[1]*(FLUTE_R - FLUTE_DEPTH)
        c = m3.Manifold.cylinder(H - 6.0, FLUTE_R, FLUTE_R, 20).translate([cx, cy, 3.0])
        flutes = c if flutes is None else flutes + c
    body = body - flutes

    for shp, dep in zip(shapes, depths):
        body = body - extrude(shp, dep + 5, H - dep)
        c = shp.centroid
        body = body - cyl(4.0 if dep > 80 or shp.area > 1000 else 2.5, H - dep + 2, c.x, c.y, -1)

    z0 = H - 14 - RAIL_H
    opening = m3.Manifold.cube([x1 - x0 + 4, LIP + 1, RAIL_H]).translate([x0 - 2, y0 - 1, z0])
    channel = m3.Manifold.cube([x1 - x0 + 4, CHAN, RAIL_H]).translate([x0 - 2, y0 + LIP, z0])
    body = body - opening - channel

    # Logo: vista de frente = mirando hacia -Y desde el lado del mate (y mayor). Su derecha es -X.
    # Por eso espejamos el texto en X: así se lee bien de frente y queda a la derecha.
    lg = affinity.scale(logo_2d(), -1, 1, origin=(0, 0))       # x en [-lw, 0]
    lw = lg.bounds[2] - lg.bounds[0]
    x_start = front_flat_x0 + RIGHT_MARGIN                       # borde izquierdo del logo (en X)
    lg = affinity.translate(lg, x_start + lw, LOGO_Z)           # ahora x en [x_start, x_start+lw]
    if round_r:
        lg = lg  # mismo lugar: queda dentro de la parte plana del frente
    logo = extrude(lg, LOGO_RELIEF + 0.6, 0).rotate([90, 0, 0])   # texto en XZ, saliente hacia -Y
    logo = logo.translate([0, y1 + LOGO_RELIEF, 0])               # y en [y1-0.6, y1+LOGO_RELIEF]
    body = body + logo

    body = body.translate([-(x0 + x1)/2, -(y0 + y1)/2, 0])
    return body, full2d, H, dict(rail_z=z0, logo_x=[round(x_start - (x0+x1)/2, 1), round(x_start + lw - (x0+x1)/2, 1)])

def hanger(L=130.0, W=30.0, T=12.0):
    """Gancho para apoyacabezas: tira 30x12x130, brazo de 46 mm, anilla cerrada (OD 30, ID 17) para el poste,
    refuerzo triangular en la unión tira-brazo y pie en T que entra en el riel."""
    strap = m3.Manifold.cube([W, T, L]).translate([-W/2, 0, 0])
    arm = m3.Manifold.cube([W, 46.0, T]).translate([-W/2, 0, L - T])
    gusset = m3.Manifold.cube([W, 14.0, 14.0]).translate([-W/2, 0, L - T - 14.0])
    ring = cyl(W/2, T, 0, 46.0, L - T, 64) - cyl(8.5, T + 2, 0, 46.0, L - T - 1, 64)
    stem = m3.Manifold.cube([W, LIP + 0.3, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3), 0.0])
    foot = m3.Manifold.cube([W, CHAN - 0.4, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3) - (CHAN - 0.4), 0.0])
    return strap + arm + gusset + ring + stem + foot

def hanger_print():
    h = hanger().rotate([0, 90, 0])
    bb = h.bounding_box()
    return h.translate([-bb[0], -bb[1], -bb[2]])

def to_trimesh(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=False)

def printed_grams(man, walls_mm=PERIM_MM, infill=INFILL, skin=1.2, step=1.0, density=1.25):
    from shapely.geometry import Polygon as SPoly
    bb = man.bounding_box(); zmin, zmax = bb[2], bb[5]
    vol = 0.0
    for z in np.arange(zmin + step/2, zmax, step):
        rings = man.slice(z).to_polygons()
        polys = unary_union([SPoly(r) for r in rings if len(r) >= 3]).buffer(0)
        area = polys.area
        core = polys.buffer(-walls_mm).area
        if z < zmin + skin or z > zmax - skin: vol += area * step
        else: vol += ((area - core) + core * infill) * step
    return vol / 1000.0 * density * 1.03

A_POCKETS = [
    dict(kind="termo",   x=-54.0, y=0.0,   d=96.0,  depth=115.0),
    dict(kind="yerbero", x= 51.0, y=5.0,   d=106.0, depth=85.0),
    dict(kind="mate",    x=-40.0, y=95.0,  d=88.0,  depth=70.0),
]
A_BOMB = (30.0, 104.0, 16.0, 34.0, 95.0)
B_POCKETS = [
    dict(kind="termo",   x=-51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="termo",   x= 51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="yerbero", x=-46.5, y=104.0,  d=106.0, depth=85.0),
    dict(kind="mate",    x= 46.0, y=95.0,   d=88.0,  depth=70.0),
]
B_BOMB = (104.0, 106.0, 16.0, 34.0, 95.0)

def scaled(pockets, bomb, k):
    pk = [dict(p, depth=round(p["depth"] * k, 1)) for p in pockets]
    return pk, (bomb[0], bomb[1], bomb[2], bomb[3], round(bomb[4] * k, 1))

if __name__ == "__main__":
    KA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.68
    KB = float(sys.argv[2]) if len(sys.argv) > 2 else 0.59
    ROUND_R = 40.0
    results = {}
    for name, pk, bb, rr in (
        ("rectangular_A_1termo_1mate_1yerbero", A_POCKETS, A_BOMB, None),
        ("rectangular_B_2termos_1mate_1yerbero", B_POCKETS, B_BOMB, None),
        ("redondeado_A_1termo_1mate_1yerbero", A_POCKETS, A_BOMB, ROUND_R),
        ("redondeado_B_2termos_1mate_1yerbero", B_POCKETS, B_BOMB, ROUND_R),
    ):
        K = KA if "_A_" in name else KB
        pk2, bb2 = scaled(pk, bb, K)
        body, full2d, Hmax, info = build(pk2, bb2, rr)
        tm = to_trimesh(body)
        assert tm.is_watertight, name
        assert len(tm.split(only_watertight=False)) == 1, name + " no es una sola pieza"
        tm.export(f"{OUT}/{name}.stl")
        g = printed_grams(body)
        ext = tm.bounds[1] - tm.bounds[0]
        results[name] = dict(bbox_mm=[round(float(v), 1) for v in ext], printed_g=round(g), **info)
        print(name, results[name], flush=True)
    hp = hanger_print()
    hg = to_trimesh(hp)
    assert hg.is_watertight
    hg.export(f"{OUT}/gancho_v2_imprimir_x2.stl")
    results["gancho_each_g"] = round(printed_grams(hp))
    print("gancho", results["gancho_each_g"], [round(float(v),1) for v in hg.bounds[1]-hg.bounds[0]])
    json.dump(results, open(f"{OUT}/_estimaciones_v2.json", "w"), indent=1)
