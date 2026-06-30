#!/usr/bin/env python3
"""
HVG Inhotim — revisão v116: divisórias internas do Centro de Convenções e do
Restaurante da Piscina, traçadas dos DWG oficiais (051 / 06) via LibreDWG.

Para cada edifício: extrai as linhas de parede, mapeia ao footprint do edifício
no modelo (de-rotação + ajuste de eixos + escala) e cria IfcWall PARTITIONING.

Entrada : HVG_MASTER_v115_ACABAMENTOS.ifc
Saída   : HVG_MASTER_v116_OUTROS_EDIF.ifc
"""
import numpy as np
import ifcopenshell
import ifcopenshell.guid
from detail_lib import wall_segments, map_to_footprint

SRC = "HVG_MASTER_v115_ACABAMENTOS.ifc"
OUT = "HVG_MASTER_v116_OUTROS_EDIF.ifc"
SC = "/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"

CONF = [
    dict(name="Centro de Convenções", json=f"{SC}/bld_cc_plantas.json",
         layers={"PAR"}, storey="CC-Terreo",
         bbox=(266.6, 313.4, 261.0, 279.0), base_z=0.0, h=4.0),
    dict(name="Restaurante da Piscina", json=f"{SC}/bld_rp.json",
         layers={"VERM1", "VERM", "Alvenaria"}, storey="RP-Terreo",
         bbox=(52.6, 87.3, 217.7, 232.3), base_z=0.0, h=3.5),
]
THICK = 0.15

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


def make_wall(p0, p1, h, st, off, base_z):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.hypot(d[0], d[1]))
    if L < 0.2:
        return None
    u = d / L; mid = (p0 + p1) / 2
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=L, YDim=THICK)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=float(h))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX, RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt([mid[0] - off[0], mid[1] - off[1], base_z - off[2]]),
                             Axis=Dir([0, 0, 1]), RefDirection=Dir([u[0], u[1], 0])))
    return f.create_entity("IfcWall", GlobalId=gid(), OwnerHistory=OWNER,
                           Name="Parede-Divisoria-Alvenaria", ObjectPlacement=pl,
                           Representation=prod, PredefinedType="PARTITIONING")


def main():
    for cfg in CONF:
        seg = wall_segments(cfg["json"], cfg["layers"])
        mapped = map_to_footprint(seg, cfg["bbox"])
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == cfg["storey"])
        off = storey_off(st)
        walls = [make_wall(w[:2], w[2:], cfg["h"], st, off, cfg["base_z"]) for w in mapped]
        walls = [w for w in walls if w]
        f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedElements=walls, RelatingStructure=st)
        f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedObjects=walls, RelatingMaterial=material("Alvenaria Bloco Cerâmico Rebocado"))
        print(f"{cfg['name']}: {len(walls)} paredes-divisoria ({len(seg)} segmentos do DWG)")
    f.write(OUT)
    print("Escrito:", OUT)


if __name__ == "__main__":
    main()
