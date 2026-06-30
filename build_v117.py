#!/usr/bin/env python3
"""
HVG Inhotim — revisão v117: divisórias dos blocos de apartamentos A e B.

Extrai a planta-tipo do Térreo (camada Par1) dos DWG 07 (Bloco A, 18 aptos) e
08 (Bloco B, 24 aptos), localizada pelo rótulo "PLANTA TÉRREO", e replica o
layout de divisórias nos 12 blocos A + 4 blocos B do modelo, mapeando ao
footprint de cada bloco. Apartamentos compactos (estúdios ~19–33 m²: quarto/
estar + I.S. + varanda), portanto poucas paredes por unidade.

Entrada : HVG_MASTER_v116_OUTROS_EDIF.ifc
Saída   : HVG_MASTER_v117_APARTAMENTOS.ifc
"""
import re, sys
import numpy as np
import ifcopenshell
import ifcopenshell.guid
sys.path.insert(0, "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from load_dwgjson import load
from detail_lib import laymap_of, map_to_footprint

SRC = "HVG_MASTER_v116_OUTROS_EDIF.ifc"
OUT = "HVG_MASTER_v117_APARTAMENTOS.ifc"
SC = "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
THICK = 0.13
H = 2.80

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType == "Model")


def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def storey_off(st):
    o = np.zeros(3); p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location: o = o + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return o


def material(n):
    return next((m for m in f.by_type("IfcMaterial") if m.Name == n), None) or f.create_entity("IfcMaterial", Name=n)


def terreo_walls(path):
    """Par1 do plano do Térreo, localizado pelo rótulo 'PLANTA TÉRREO'."""
    d = load(path); objs = d["OBJECTS"]; lm = laymap_of(objs)
    def ln(o):
        l = o.get("layer"); return lm.get(l[2]) if isinstance(l, list) and len(l) >= 3 else None
    lx = ly = None
    for o in objs:
        if o.get("entity") in ("TEXT", "MTEXT"):
            tv = (o.get("text_value") or o.get("text") or "")
            if re.search(r't[eé]rreo', tv, re.I) and re.search(r'planta', tv, re.I):
                ip = o.get("ins_pt")
                if ip: lx, ly = ip[0], ip[1]; break
    seg = []
    for o in objs:
        if ln(o) != "Par1": continue
        e = o.get("entity")
        if e == "LINE":
            a, b = o.get("start"), o.get("end")
            if a and b: seg.append((a[0], a[1], b[0], b[1]))
        elif e == "LWPOLYLINE":
            p = o.get("points") or []
            for i in range(len(p) - 1): seg.append((p[i][0], p[i][1], p[i + 1][0], p[i + 1][1]))
    seg = np.array(seg)
    if lx is not None:
        mid = np.c_[(seg[:, 0] + seg[:, 2]) / 2, (seg[:, 1] + seg[:, 3]) / 2]
        m = (np.abs(mid[:, 0] - lx) < 35) & (mid[:, 1] > ly - 1) & (mid[:, 1] < ly + 26)
        seg = seg[m]
    return seg


def make_wall(p0, p1, st, off):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.hypot(d[0], d[1]))
    if L < 0.2: return None
    u = d / L; mid = (p0 + p1) / 2
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=L, YDim=THICK)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=H)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX, RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt([mid[0] - off[0], mid[1] - off[1], 0.0 - off[2]]),
                             Axis=Dir([0, 0, 1]), RefDirection=Dir([u[0], u[1], 0])))
    return f.create_entity("IfcWall", GlobalId=gid(), OwnerHistory=OWNER,
                           Name="Parede-Divisoria-Apto", ObjectPlacement=pl,
                           Representation=prod, PredefinedType="PARTITIONING")


import json
BLOCKS = json.load(open(f"{SC}/apt_blocks.json"))


def main():
    segA = terreo_walls(f"{SC}/bld_aptA.json")
    segB = terreo_walls(f"{SC}/bld_aptB.json")
    print(f"planta-tipo: A {len(segA)} segs, B {len(segB)} segs")
    mat = material("Alvenaria Bloco Cerâmico Rebocado (Apto)")
    tot = 0
    for name, info in BLOCKS.items():
        seg = segA if name.startswith("Bloco-A") else segB
        if not len(seg): continue
        bbox = info["bbox"]
        mapped = map_to_footprint(seg, tuple(bbox), inset=0.3)
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == info["terreo"])
        off = storey_off(st)
        walls = [w for w in (make_wall(m[:2], m[2:], st, off) for m in mapped) if w]
        f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedElements=walls, RelatingStructure=st)
        f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedObjects=walls, RelatingMaterial=mat)
        tot += len(walls)
    print(f"Total divisorias de apartamentos: {tot} ({len(BLOCKS)} blocos)")
    f.write(OUT)
    print("Escrito:", OUT)


if __name__ == "__main__":
    main()
