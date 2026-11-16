"""Verificación de medidas del set final por tres métodos independientes. Sale con error si algo no cierra."""
import itertools, numpy as np, trimesh, manifold3d as m3
import generar_final as g
from generar_v2 import scaled, A_POCKETS, A_BOMB, cyl
from generar_tapa_nervada_v7 import tapa
from generar_retenedor_mate import retenedor
from generar_v3_accesorios import adaptador_termo_chico

def load(path):
    t = trimesh.load(path); t.merge_vertices()
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32), tri_verts=np.asarray(t.faces, dtype=np.uint32)))

pk, bb = scaled(A_POCKETS, A_BOMB, 0.68)
H = max([p["depth"] for p in pk] + [bb[4]]) + g.FLOOR
xs = [p["x"]-p["d"]/2 for p in pk]+[bb[0]-bb[2]/2]; xe = [p["x"]+p["d"]/2 for p in pk]+[bb[0]+bb[2]/2]
ys = [p["y"]-p["d"]/2 for p in pk]+[bb[1]-bb[3]/2]; ye = [p["y"]+p["d"]/2 for p in pk]+[bb[1]+bb[3]/2]
x0 = min(xs)-g.WALL; x1 = max(xe)+g.WALL; y0 = min(ys)-g.WALL-g.PLATE_BACK; y1 = max(ye)+g.WALL
ox, oy = (x0+x1)/2, (y0+y1)/2
box = load("final/caja_A.stl"); bad = []
def chk(ok, msg):
    print(("  OK   " if ok else "  FALLA ") + msg)
    if not ok: bad.append(msg)

print("MÉTODO 1: contornos del STL exportado")
b = box.bounding_box(); ext = [b[3]-b[0], b[4]-b[1], b[5]-b[2]]
chk(abs(ext[0]-214.0) < 0.05 and abs(ext[1]-(207.0+g.LOGO_RELIEF)) < 0.05 and abs(ext[2]-H) < 0.05, f"exterior {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} mm (incluye 0,8 de logo)")
for p in pk:
    for z in (H-2.0, H-p["depth"]+3.0):
        rings = box.slice(z).to_polygons(); c = np.array([p["x"]-ox, p["y"]-oy]); best = None
        for r in rings:
            r = np.asarray(r); rad = np.hypot(*(r-c).T)
            if abs(r.mean(0)-c).max() < 1.0 and rad.max() < 80: best = (2*rad.min(), 2*rad.max())
        chk(best is not None and abs(best[1]-p["d"]) < 0.05 and p["d"]-best[0] < 0.15, f"{p['kind']} a z={z:.1f}: Ø medido {best[0]:.2f} a {best[1]:.2f} (diseño {p['d']})")

print("MÉTODO 2: profundidad con aguja de sondeo")
def depth(x, y):
    needle = cyl(1.0, H+2, x-ox, y-oy, -1, 32); a = np.pi*1.0**2*np.cos(np.pi/32)  # área del polígono ~
    a = cyl(1.0, 1.0, 0, 0, 0, 32).volume()
    return H - (box ^ needle).volume()/a
for p in pk:
    d = depth(p["x"]+15, p["y"]+9); chk(abs(d-p["depth"]) < 0.05, f"{p['kind']}: profundidad {d:.2f} (diseño {p['depth']}), piso {H-d:.2f} mm")
d = depth(bb[0], bb[1]+8); chk(abs(d-bb[4]) < 0.05, f"bombilla: profundidad {d:.2f} (diseño {bb[4]})")

print("MÉTODO 3: calibres pasa / no pasa e interferencias con los accesorios")
for p in pk:
    go = (box ^ cyl(p["d"]/2-0.2, p["depth"]-0.2, p["x"]-ox, p["y"]-oy, H-p["depth"]+0.1, 128)).volume()
    nogo = (box ^ cyl(p["d"]/2+0.3, 5, p["x"]-ox, p["y"]-oy, H-6, 128)).volume()
    chk(go < 0.5 and nogo > 50, f"{p['kind']}: calibre Ø{p['d']-0.4} entra (choque {go:.1f} mm3), Ø{p['d']+0.6} no entra")
mate = [p for p in pk if p["kind"] == "mate"][0]; termo = [p for p in pk if p["kind"] == "termo"][0]
t = load("final/tapa_mate.stl").translate([mate["x"]-ox, mate["y"]-oy, H-41.0])
chk((box ^ t).volume() < 0.5 and 41.0 <= mate["depth"], f"tapa: sin choque, tapón 41 en bolsillo de {mate['depth']}")
r = load("final/retenedor_mate.stl").translate([mate["x"]-ox, mate["y"]-oy, H-mate["depth"]])
chk((box ^ r).volume() < 0.5 and 44.0 <= mate["depth"], f"retenedor: sin choque, alto 44 en bolsillo de {mate['depth']}")
a = load("final/adaptador_termo_chico.stl").translate([termo["x"]-ox, termo["y"]-oy, H-termo["depth"]])
chk((box ^ a).volume() < 0.5 and 60.0 <= termo["depth"], f"adaptador: sin choque, alto 60 en bolsillo de {termo['depth']}")
yb = b[1]; zt = H-g.CLEAT_TOP; hf = g.CLEAT_H-1.2
hook = load("final/gancho_x2.stl"); hb = hook.bounding_box()
chk(abs(hb[5]-hb[2]-40) < 0.05 and abs(hb[3]-hb[0]-130) < 0.05, f"gancho exportado: {hb[3]-hb[0]:.1f} x {hb[4]-hb[1]:.1f} x {hb[5]-hb[2]:.1f} mm")
for xh in (-60, 60):
    h = g.hanger().mirror([0, 1, 0]).translate([xh, yb, zt-hf-0.6])
    chk((box ^ h).volume() < 0.5 and (box ^ h.translate([0, -3, 0])).volume() > 100 and (box ^ h.translate([0, -3, -5])).volume() > 100,
        f"gancho en x={xh}: asienta sin choque y queda retenido al tirar y al levantar")
tp = g.prism_yz(g.foot_pts(0.25, g.CLEAT_H-0.4), 12.0).mirror([0, 1, 0]).translate([100, yb, zt-g.CLEAT_H+0.1])
chk((box ^ tp).volume() < 0.5, "tope: entra en la cuña (holgura 0,25 mm)")
hole = (g.hanger() ^ cyl(8.4, 200, 0, g.ARM, -20, 64)).volume()
chk(hole < 0.5, "gancho: un poste de Ø16,8 pasa de punta a punta sin tocar nada")
for p, q in itertools.combinations(pk, 2):
    w = np.hypot(p["x"]-q["x"], p["y"]-q["y"])-p["d"]/2-q["d"]/2
    chk(w >= 3.99, f"pared entre {p['kind']} y {q['kind']}: {w:.2f} mm")
chk(g.WALL+g.PLATE_BACK-g.CLEAT_D >= 7, f"pared entre la cuña y el termo: {g.WALL+g.PLATE_BACK-g.CLEAT_D:.1f} mm")
chk(ext[0] <= 220 and ext[1] <= 220, "entra en cama de 220 x 220")
print("\nRESULTADO:", "TODO OK" if not bad else f"{len(bad)} FALLAS"); raise SystemExit(1 if bad else 0)
