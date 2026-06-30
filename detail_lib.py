"""Biblioteca de detalhamento: extrai paredes de um DWG/JSON (LibreDWG) e mapeia
para o footprint de um edifício no modelo IFC, criando IfcWall de divisória."""
import sys, math
import numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from load_dwgjson import load


def laymap_of(objs):
    m = {}
    for o in objs:
        if o.get("entity") == "LAYER" or o.get("object") == "LAYER":
            h = o.get("handle")
            if isinstance(h, list) and len(h) >= 3:
                m[h[2]] = o.get("name")
    return m


def wall_segments(path, wall_layers):
    d = load(path); objs = d["OBJECTS"]; lm = laymap_of(objs)
    def ln(o):
        l = o.get("layer")
        return lm.get(l[2]) if isinstance(l, list) and len(l) >= 3 else None
    seg = []
    for o in objs:
        if ln(o) not in wall_layers:
            continue
        e = o.get("entity")
        if e == "LINE":
            a, b = o.get("start"), o.get("end")
            if a and b:
                seg.append((a[0], a[1], b[0], b[1]))
        elif e == "LWPOLYLINE":
            p = o.get("points") or []
            for i in range(len(p) - 1):
                seg.append((p[i][0], p[i][1], p[i + 1][0], p[i + 1][1]))
    return np.array(seg)


def dominant_angle(seg):
    d = seg[:, 2:] - seg[:, :2]
    L = np.hypot(d[:, 0], d[:, 1])
    ang = (np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 90)
    h, edg = np.histogram(ang, bins=90, range=(0, 90), weights=L)
    return edg[np.argmax(h)]


def map_to_footprint(seg, bbox, inset=0.4):
    """Mapeia segmentos do plano para o footprint (x0,x1,y0,y1) do modelo:
    de-rotação pelo ângulo dominante, alinhamento de eixos longos, escala e
    translação. Retorna lista de (x0,y0,x1,y1) em coords do modelo."""
    x0, x1, y0, y1 = bbox
    x0 += inset; x1 -= inset; y0 += inset; y1 -= inset
    th = math.radians(dominant_angle(seg))
    R = np.array([[math.cos(-th), -math.sin(-th)], [math.sin(-th), math.cos(-th)]])
    pts = np.vstack([seg[:, :2], seg[:, 2:]])
    c = pts.mean(0)
    rot = (R @ (pts - c).T).T
    rmn, rmx = rot.min(0), rot.max(0)
    Ex, Ey = (rmx - rmn)
    Wx, Wy = (x1 - x0), (y1 - y0)
    swap = (Ex >= Ey) != (Wx >= Wy)

    def tf(P):
        q = (R @ (np.array(P) - c)) - rmn          # 0..E
        if swap:
            q = np.array([q[1], q[0]]); ex, ey = Ey, Ex
        else:
            ex, ey = Ex, Ey
        u = q[0] / ex; v = q[1] / ey
        return np.array([x0 + u * Wx, y0 + v * Wy])
    out = []
    for s in seg:
        a = tf(s[:2]); b = tf(s[2:])
        out.append([round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3)])
    return out
