import math, json
import numpy as np
import manifold3d as m3
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
import trimesh

OUT = "/home/user/aronfeola/soporte-mate"
WALL = 3.5      # outer wall (fluted; min 2.5 mm at the bottom of a flute)
FLOOR = 4.0
BACK_T = 12.0   # flat back plate holding the T-rail
LIP, CHAN = 3.4, 5.4        # rail: opening lip depth, channel depth
RAIL_H = 24.0               # channel height
FLUTE_R, FLUTE_PITCH, FLUTE_DEPTH = 2.2, 6.0, 1.0
SEG = 96

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

def build(pockets, bombilla):
    """Rectangular block with pockets cut from the top. Rounded vertical corners, fluted sides, flat back with rail."""
    CORNER = 12.0
    shapes, depths = [], []
    for p in pockets:
        shapes.append(Point(p["x"], p["y"]).buffer(p["d"]/2, resolution=SEG//4)); depths.append(p["depth"])
    bx, by, bw, bl, bdepth = bombilla
    bshape = rrect(bx, by, bw, bl, bw/2 - 0.01)
    shapes.append(bshape); depths.append(bdepth)
    H = max(depths) + FLOOR
    allp = unary_union(shapes)
    x0, y0, x1, y1 = allp.bounds
    PLATE_BACK = LIP + CHAN + 3.2
    x0 -= WALL; x1 += WALL; y0 -= WALL + PLATE_BACK; y1 += WALL
    outline = box(x0, y0, x1, y1)
    # round the two front corners and the back corners (smaller radius at the back so the plate stays flat)
    outline = box(x0 + CORNER, y0, x1 - CORNER, y1).union(box(x0, y0, x1, y1 - CORNER)).union(
        unary_union([Point(x0 + CORNER, y1 - CORNER).buffer(CORNER, resolution=16), Point(x1 - CORNER, y1 - CORNER).buffer(CORNER, resolution=16)]))
    full2d = outline
    body = extrude(outline, H)

    # flutes on front and sides (not on the flat back face)
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

    # pockets cut from the top, drain holes through the floor below each
    for shp, dep in zip(shapes, depths):
        body = body - extrude(shp, dep + 5, H - dep)
        c = shp.centroid
        body = body - cyl(4.0 if dep > 80 or shp.area > 1000 else 2.5, H - dep + 2, c.x, c.y, -1)

    z0 = H - 14 - RAIL_H
    opening = m3.Manifold.cube([x1 - x0 + 4, LIP + 1, RAIL_H]).translate([x0 - 2, y0 - 1, z0])
    channel = m3.Manifold.cube([x1 - x0 + 4, CHAN, RAIL_H]).translate([x0 - 2, y0 + LIP, z0])
    body = body - opening - channel
    body = body.translate([-(x0 + x1)/2, -(y0 + y1)/2, 0])
    return body, full2d, H, dict(rail_z=z0)

def hanger(L=130.0):
    """Headrest hanger. Prints standing on its narrow edge (no supports). Strap 25x6, closed ring for the
    post (ID 16, OD 25) on a 46 mm arm, T-foot at the bottom that slides sideways into the body's rail."""
    W, T = 25.0, 6.0
    strap = m3.Manifold.cube([W, T, L]).translate([-W/2, 0, 0])
    arm = m3.Manifold.cube([W, 46.0, T]).translate([-W/2, 0, L - T])
    ring = (cyl(12.5, T, 0, 46.0, L - T, 64) - cyl(8.0, T + 2, 0, 46.0, L - T - 1, 64))
    stem = m3.Manifold.cube([W, LIP + 0.3, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3), 0.0])
    foot = m3.Manifold.cube([W, CHAN - 0.4, RAIL_H - 1.0]).translate([-W/2, -(LIP + 0.3) - (CHAN - 0.4), 0.0])
    return strap + arm + ring + stem + foot

def hanger_print():
    """Hanger rotated to lie on its narrow edge, resting on the bed."""
    h = hanger().rotate([0, 90, 0])
    bb = h.bounding_box()
    return h.translate([-bb[0], -bb[1], -bb[2]])

def to_trimesh(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=False)

def printed_grams(man, walls_mm=1.8, infill=0.20, skin=1.2, step=1.0, density=1.25):
    """Slice the manifold every `step` mm; each slice: perimeters (walls_mm) solid + core at `infill`.
    Bottom/top skins (skin mm) solid."""
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

results = {}
# Model A: 1 termo (back-left) + 1 yerbero (back-right); front: 1 mate + bombilla
A_pockets = [
    dict(kind="termo",   x=-54.0, y=0.0,   d=96.0,  depth=115.0),
    dict(kind="yerbero", x= 51.0, y=5.0,   d=106.0, depth=85.0),
    dict(kind="mate",    x=-40.0, y=95.0,  d=88.0,  depth=70.0),
]
A_bomb = (30.0, 104.0, 16.0, 34.0, 95.0)
B_pockets = [
    dict(kind="termo",   x=-51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="termo",   x= 51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="yerbero", x=-46.5, y=104.0,  d=106.0, depth=85.0),
    dict(kind="mate",    x= 46.0, y=95.0,   d=88.0,  depth=70.0),
]
B_bomb = (104.0, 106.0, 16.0, 34.0, 95.0)

for name, pk, bb in (("modelo_A_1termo_1mate_1yerbero", A_pockets, A_bomb), ("modelo_B_2termos_1mate_1yerbero", B_pockets, B_bomb)):
    body, full2d, Hmax, info = build(pk, bb)
    tm = to_trimesh(body)
    assert tm.is_watertight, name
    assert len(tm.split(only_watertight=False)) == 1, name + ' is not one piece'
    tm.export(f"{OUT}/{name}.stl")
    g = printed_grams(body)
    ext = tm.bounds[1] - tm.bounds[0]
    results[name] = dict(bbox_mm=[round(float(v), 1) for v in ext], solid_cm3=round(tm.volume/1000, 1), printed_g=round(g), faces=len(tm.faces), **info)
    print(name, results[name], flush=True)

hp = hanger_print()
hg_flat = to_trimesh(hp)
assert hg_flat.is_watertight
hg_flat.export(f"{OUT}/gancho_apoyacabezas_imprimir_x2.stl")
results["gancho"] = dict(bbox_mm=[round(float(v), 1) for v in (hg_flat.bounds[1]-hg_flat.bounds[0])], printed_g_each=round(printed_grams(hp)))
print("gancho", results["gancho"])
json.dump(results, open(f"{OUT}/_estimaciones.json", "w"), indent=1)
