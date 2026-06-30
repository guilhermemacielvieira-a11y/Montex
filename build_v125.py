#!/usr/bin/env python3
"""
HVG Inhotim — revisão v125: recorte poligonal dos ambientes (IfcSpace).

Substitui os IfcSpace quadrados (dimensionados por área) do Bloco Principal
(Subsolo + Térreo) e do SPA (Térreo) por ESPAÇOS COM CONTORNO POLIGONAL REAL,
que tesselam (preenchem sem sobreposição) a placa de cada pavimento.

Método: as paredes isoladas por camada nos DWG NÃO formam células fechadas
(há vãos sistemáticos em portas/encontros — verificado: a placa permanece um
único polígono ao tentar `polygonize`). Em vez de loops de parede frágeis,
particiona-se a placa por **diagrama de Voronoi (Thiessen)** semeado no
centroide real de cada ambiente (posição lida da planta oficial): a fronteira
de Voronoi entre dois ambientes vizinhos aproxima a divisória entre eles.
Cada célula é recortada à placa do pavimento → IfcSpace com
IfcArbitraryClosedProfileDef (polígono real), preservando a área medida da
planilha em Pset_SpaceCommon (GrossPlannedArea).

Entrada : HVG_MASTER_v124_BAR_PISCINA.ifc
Saída   : HVG_MASTER_v125_ESPACOS_POLIGONAIS.ifc
"""
import sys, re, json
import numpy as np
import ifcopenshell, ifcopenshell.guid, ifcopenshell.api
sys.path.insert(0, "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
sys.path.insert(0, "/home/user/Montex")
import shapely
from shapely.geometry import box, Polygon, MultiPoint, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from detail_lib import wall_segments, make_transform
from load_dwgjson import load

SC = "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC = "HVG_MASTER_v124_BAR_PISCINA.ifc"
OUT = "HVG_MASTER_v125_ESPACOS_POLIGONAIS.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType == "Model")


def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])
def Pt2(v): return f.create_entity("IfcCartesianPoint", Coordinates=[float(v[0]), float(v[1])])
def Dir(v): return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def storey_off(st):
    o = np.zeros(3); p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location: o = o + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return o


def voronoi_cells(seeds, foot):
    """seeds: list[(x,y)] (deduplicated/jittered). Returns list of shapely
    Polygon (clipped to foot), aligned with input order."""
    pts = np.asarray(seeds, float)
    seen = {}
    for k in range(len(pts)):
        key = (round(pts[k, 0], 2), round(pts[k, 1], 2))
        if key in seen: pts[k] = pts[k] + np.array([0.09, 0.06]) * seen[key]
        seen[key] = seen.get(key, 0) + 1
    mp = MultiPoint([Point(p) for p in pts])
    regions = shapely.voronoi_polygons(mp, extend_to=foot.buffer(60), only_edges=False)
    cells_raw = list(regions.geoms)
    out = []
    for p in pts:
        pt = Point(p); chosen = None
        for c in cells_raw:
            if c.contains(pt): chosen = c; break
        if chosen is None:
            out.append(None); continue
        clip = chosen.intersection(foot)
        if clip.is_empty:
            out.append(None); continue
        if clip.geom_type == "MultiPolygon":
            clip = max(clip.geoms, key=lambda g: g.area)
        out.append(orient(clip, 1.0))   # CCW
    return out


def make_space(name, long_name, poly, planned_area, st, off, zf, h):
    ring = list(poly.exterior.coords)[:-1]
    pts2 = [Pt2([x - off[0], y - off[1]]) for (x, y) in ring]
    pts2.append(pts2[0])
    pl_curve = f.create_entity("IfcPolyline", Points=pts2)
    prof = f.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=pl_curve)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=float(h))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt([off[0] - off[0], 0.0, zf - off[2]])))
    # placement location: keep polygon in (world - off) plane, frame origin at world(0,0,zf-off2)+off
    pl.RelativePlacement.Location = Pt([0.0, 0.0, zf - off[2]])
    sp = f.create_entity("IfcSpace", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                         LongName=long_name, ObjectPlacement=pl, Representation=prod,
                         CompositionType="ELEMENT", PredefinedType="INTERNAL")
    # quantities: real polygon area + perimeter
    qa = f.create_entity("IfcQuantityArea", Name="GrossFloorArea", AreaValue=float(poly.area))
    qp = f.create_entity("IfcQuantityLength", Name="GrossPerimeter", LengthValue=float(poly.length))
    eq = f.create_entity("IfcElementQuantity", GlobalId=gid(), OwnerHistory=OWNER,
                         Name="Qto_SpaceBaseQuantities", Quantities=[qa, qp])
    f.create_entity("IfcRelDefinesByProperties", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=[sp], RelatingPropertyDefinition=eq)
    # planned area from the project schedule (preserved for traceability)
    if planned_area:
        p1 = f.create_entity("IfcPropertySingleValue", Name="GrossPlannedArea",
                             NominalValue=f.create_entity("IfcAreaMeasure", float(planned_area)))
        pset = f.create_entity("IfcPropertySet", GlobalId=gid(), OwnerHistory=OWNER,
                               Name="Pset_SpaceCommon", HasProperties=[p1])
        f.create_entity("IfcRelDefinesByProperties", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedObjects=[sp], RelatingPropertyDefinition=pset)
    return sp


def replace_storey_spaces(storey_name, seeds, names, areas, foot, zf, h, prefix):
    st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == storey_name)
    off = storey_off(st)
    # remove existing spaces aggregated under this storey
    old = [sp for sp in f.by_type("IfcSpace")
           if sp.Decomposes and sp.Decomposes[0].RelatingObject == st]
    for sp in old:
        ifcopenshell.api.run("root.remove_product", f, product=sp)
    cells = voronoi_cells(seeds, foot)
    spaces = []
    for i, c in enumerate(cells):
        if c is None or c.area < 0.5: continue
        nm = names[i] if names else "Ambiente"
        sp = make_space(f"{prefix}-{nm[:16]}", nm, c, areas[i] if areas else None, st, off, zf, h)
        spaces.append(sp)
    if spaces:
        f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatingObject=st, RelatedObjects=spaces)
    print(f"{storey_name}: removidos {len(old)} | criados {len(spaces)} espaços poligonais"
          f" | cobertura {sum(c.area for c in cells if c):.0f}/{foot.area:.0f} m²")
    return len(spaces)


# ---------------- Bloco Principal ----------------
def bp_seeds():
    ROOMS = json.load(open(f"{SC}/bp_rooms.json", encoding="utf-8"))
    GX0, GX1, GY0, GY1 = 135.65, 194.35, 216.5, 273.5
    foot = box(GX0, GY0, GX1, GY1)
    out = {}
    for fl in ("Subsolo", "Terreo"):
        rooms = ROOMS[fl]
        seeds = [(GX0 + r["u"] * (GX1 - GX0), GY0 + r["v"] * (GY1 - GY0)) for r in rooms]
        out[fl] = (seeds, [r["name"] for r in rooms], [r["area"] for r in rooms], foot)
    return out


# ---------------- SPA ----------------
def spa_seeds():
    BB = (67.7, 92.3, 263.1, 276.9)
    foot = box(BB[0] + 0.3, BB[2] + 0.3, BB[1] - 0.3, BB[3] - 0.3)
    seg = wall_segments(f"{SC}/bld_spa.json", {"ALVENARIA", "PAR1", "PAR", "SPA_ALVENARIA"})
    mid = np.c_[(seg[:, 0] + seg[:, 2]) / 2, (seg[:, 1] + seg[:, 3]) / 2]
    m = (mid[:, 0] > 298) & (mid[:, 0] < 338) & (mid[:, 1] > -276) & (mid[:, 1] < -242)
    tf = make_transform(seg[m], BB, inset=0.3)
    d = load(f"{SC}/bld_spa.json"); objs = d["OBJECTS"]; A = []; N = []
    for o in objs:
        if o.get("entity") in ("TEXT", "MTEXT"):
            tv = (o.get("text_value") or o.get("text") or "")
            tv = re.sub(r'\\[A-Za-z][^;]*;', '', tv).replace('{', '').replace('}', '').replace('\\P', ' ').strip()
            ip = o.get("ins_pt")
            if not (ip and 298 < ip[0] < 338 and -276 < ip[1] < -242): continue
            ma = re.search(r'A\s*=\s*([\d.,]+)\s*m', tv)
            if ma: A.append((float(ma.group(1).replace(',', '.')), ip[0], ip[1]))
            elif re.search(r'[A-Za-zÀ-ÿ]{4,}', tv) and not re.search(r'planta|escala|fach|acabam|granito|porcel|nivel|pavimento', tv, re.I):
                N.append((tv[:24], ip[0], ip[1]))
    seeds = []; names = []; areas = []
    for area, ax, ay in A:
        w = tf([ax, ay]); seeds.append((float(w[0]), float(w[1])))
        nm = "Ambiente"
        if N:
            dn = min(N, key=lambda n: (n[1] - ax) ** 2 + (n[2] - ay) ** 2)
            if (dn[1] - ax) ** 2 + (dn[2] - ay) ** 2 < 16: nm = dn[0]
        names.append(nm); areas.append(area)
    return seeds, names, areas, foot


def main():
    total = 0
    bp = bp_seeds()
    total += replace_storey_spaces("BP-Subsolo", *bp["Subsolo"][:3], bp["Subsolo"][3], -3.0, 2.80, "SUB")
    total += replace_storey_spaces("BP-Terreo", *bp["Terreo"][:3], bp["Terreo"][3], 0.0, 2.84, "TER")
    seeds, names, areas, foot = spa_seeds()
    total += replace_storey_spaces("SPA-Terreo", seeds, names, areas, foot, 0.0, 3.0, "SPA")
    f.write(OUT)
    print(f"Total espaços poligonais: {total} | escrito {OUT}")


if __name__ == "__main__":
    main()
