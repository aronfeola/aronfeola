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
    shapes, heights = [], []
    for p in pockets:
        shapes.append(Point(p["x"], p["y"]).buffer(p["d"]/2, resolution=SEG//4))
        heights.append(p["depth"] + FLOOR)
    bx, by, bw, bl, bdepth = bombilla
    bshape = rrect(bx, by, bw, bl, bw/2 - 0.01)
    shapes.append(bshape); heights.append(bdepth + FLOOR)
    lobes = [s.buffer(WALL, join_style=1, resolution=24) for s in shapes]
    # webs: solid bridges between neighbouring pockets so the body is always one piece
    from shapely.geometry import LineString
    webs, web_h = [], []
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            if shapes[i].distance(shapes[j]) <= 12.0:
                wi = shapes[i].bounds[2] - shapes[i].bounds[0]; wj = shapes[j].bounds[2] - shapes[j].bounds[0]
                w = min(max(min(wi, wj) * 0.8, 24.0), 60.0)
                ci, cj = shapes[i].centroid, shapes[j].centroid
                webs.append(LineString([ci, cj]).buffer(w / 2, cap_style=2))
                web_h.append(min(heights[i], heights[j]))
    lobes = lobes + webs
    heights = heights + web_h
    outline = unary_union(lobes)
    xmin, ymin, xmax, ymax = outline.bounds
    Hmax = max(heights)

    body = None
    for lobe, h in zip(lobes, heights):
        part = extrude(lobe, h)
        body = part if body is None else body + part
    # flat back plate BEHIND the lobes (so the rail never breaks into a pocket) + fill between back row and plate
    PLATE_BACK = LIP + CHAN + 3.2            # 12.0 mm behind the outline's rearmost point
    y_plate = ymin - PLATE_BACK
    back = box(xmin + 8, y_plate, xmax - 8, ymin + WALL)
    hull = unary_union([back, outline]).convex_hull.intersection(box(xmin - 1, y_plate - 1, xmax + 1, ymin + 48))
    back2d = unary_union([back, hull])
    # extrude the back fill per zone height (so it never roofs over a lower pocket)
    for lobe, h in zip(lobes, heights):
        lx0, _, lx1, _ = lobe.bounds
        piece = back2d.intersection(box(lx0, y_plate - 1, lx1, ymin + 48))
        if not piece.is_empty and piece.area > 1:
            body = body + extrude(piece, h)
    # the plate itself runs full width at full height (continuous rail)
    body = body + extrude(back, Hmax)
    full2d = unary_union([outline, back2d])
    ymin = y_plate

    # zone height lookup for a point on the outline (for clean rims)
    def zone_h(x, y):
        pt = Point(x, y)
        hs = [h for lobe, h in zip(lobes, heights) if lobe.distance(pt) < 0.3]
        return max(hs) if hs else Hmax

    # flutes on every outer wall except the flat back face
    ext = full2d.exterior if full2d.geom_type == "Polygon" else max(full2d.geoms, key=lambda g: g.area).exterior
    L = ext.length; n = int(L // FLUTE_PITCH)
    flutes = None
    for i in range(n):
        d = i * L / n
        pt = ext.interpolate(d)
        if pt.y < ymin + 0.5: continue
        a = ext.interpolate((d - 0.5) % L); b = ext.interpolate((d + 0.5) % L)
        nrm = np.array([b.y - a.y, -(b.x - a.x)]); nrm /= np.linalg.norm(nrm)
        if full2d.contains(Point(pt.x + nrm[0]*0.6, pt.y + nrm[1]*0.6)): nrm = -nrm
        cx, cy = pt.x + nrm[0]*(FLUTE_R - FLUTE_DEPTH), pt.y + nrm[1]*(FLUTE_R - FLUTE_DEPTH)
        top = zone_h(pt.x, pt.y) - 3.0
        c = m3.Manifold.cylinder(top - 3.0, FLUTE_R, FLUTE_R, 20).translate([cx, cy, 3.0])
        flutes = c if flutes is None else flutes + c
    body = body - flutes

    # pockets + drain holes
    for p in pockets:
        body = body - cyl(p["d"]/2, p["depth"] + 5, p["x"], p["y"], FLOOR)
        body = body - cyl(4.0, FLOOR + 2, p["x"], p["y"], -1)
    body = body - extrude(bshape, bdepth + 5, FLOOR)
    body = body - cyl(2.5, FLOOR + 2, bx, by, -1)

    # T-rail across the back face: open at both ends, hangers slide in from the side
    z0 = Hmax - 14 - RAIL_H
    opening = m3.Manifold.cube([xmax - xmin + 4, LIP + 1, RAIL_H]).translate([xmin - 2, ymin - 1, z0])
    channel = m3.Manifold.cube([xmax - xmin + 4, CHAN, RAIL_H]).translate([xmin - 2, ymin + LIP, z0])
    body = body - opening - channel

    body = body.translate([-(xmin + xmax)/2, -(ymin + ymax)/2, 0])
    return body, full2d, Hmax, dict(rail_z=z0)

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
    dict(kind="yerbero", x= 50.0, y=-5.0,  d=106.0, depth=85.0),
    dict(kind="mate",    x=-22.0, y=96.0,  d=88.0,  depth=70.0),
]
A_bomb = (34.0, 92.0, 16.0, 34.0, 95.0)
# Model B: 2 termos back; front: yerbero + mate + bombilla
B_pockets = [
    dict(kind="termo",   x=-51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="termo",   x= 51.5, y=0.0,    d=96.0,  depth=115.0),
    dict(kind="yerbero", x=-47.0, y=104.0, d=106.0, depth=85.0),
    dict(kind="mate",    x= 55.0, y=97.0,   d=88.0,  depth=70.0),
]
B_bomb = (111.0, 100.0, 16.0, 34.0, 95.0)

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
