#!/usr/bin/env python3
"""
HVG Inhotim — revisão v112: paredes de compartimentação (divisórias) internas
do Bloco Principal, traçadas da planta oficial.

Extrai as linhas das camadas de parede (Alvenaria/PAR/PAR1) da planta 031,
de-rotaciona o edifício (48°) e mapeia 1:1 para o footprint calibrado, criando
as paredes internas reais de cada pavimento como IfcWall. Reposiciona os
ambientes (IfcSpace) pelo MESMO transform, alinhando-os às divisórias.

Entrada : HVG_MASTER_v110_BP_CALIBRADO.ifc  +  bp_floor_data.json
Saída   : HVG_MASTER_v112_DIVISORIAS.ifc
"""
import json
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v110_BP_CALIBRADO.ifc"
OUT = "HVG_MASTER_v112_DIVISORIAS.ifc"
DATA = json.load(open("/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad/bp_floor_data.json", encoding="utf-8"))

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")

FLOORS = {"Subsolo": ("BP-Subsolo", -3.0, 2.80), "Terreo": ("BP-Terreo", 0.0, 2.84)}
THICK = 0.15


def gid():
    return ifcopenshell.guid.new()


def Pt(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def Dir(v):
    return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def storey_off(st):
    o = np.zeros(3); p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location:
            o = o + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return o


MAT = {}
def material(name):
    if name not in MAT:
        MAT[name] = next((m for m in f.by_type("IfcMaterial") if m.Name == name), None) \
                    or f.create_entity("IfcMaterial", Name=name)
    return MAT[name]


def assoc(elems, name):
    if elems:
        f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatedObjects=list(elems), RelatingMaterial=material(name))


def make_wall(p0, p1, h, st, off, base_z):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.hypot(d[0], d[1]))
    if L < 0.15:
        return None
    u = d / L
    mid = (p0 + p1) / 2
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=L, YDim=THICK)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=float(h))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                            Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    loc = [mid[0] - off[0], mid[1] - off[1], base_z - off[2]]
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt(loc), Axis=Dir([0, 0, 1]),
                             RefDirection=Dir([u[0], u[1], 0])))
    return f.create_entity("IfcWall", GlobalId=gid(), OwnerHistory=OWNER,
                           Name="Parede-Divisoria-Alvenaria", ObjectPlacement=pl,
                           Representation=prod, PredefinedType="PARTITIONING")


def make_space(name, long_name, area, cx, cy, st, off, base_z, h):
    side = float(np.clip(np.sqrt(area), 1.5, 11.0))
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=side, YDim=side)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=float(h))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                            Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    loc = [cx - off[0], cy - off[1], base_z - off[2]]
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D", Location=Pt(loc)))
    sp = f.create_entity("IfcSpace", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                         LongName=long_name, ObjectPlacement=pl, Representation=prod,
                         CompositionType="ELEMENT", PredefinedType="INTERNAL")
    q = f.create_entity("IfcQuantityArea", Name="GrossFloorArea", AreaValue=float(area))
    eq = f.create_entity("IfcElementQuantity", GlobalId=gid(), OwnerHistory=OWNER,
                         Name="Qto_SpaceBaseQuantities", Quantities=[q])
    f.create_entity("IfcRelDefinesByProperties", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=[sp], RelatingPropertyDefinition=eq)
    return sp


def main():
    # remove espaços genéricos antigos do BP
    old = []
    for sp in f.by_type("IfcSpace"):
        par = sp.Decomposes[0].RelatingObject if sp.Decomposes else None
        if par and par.Name in ("BP-Subsolo", "BP-Terreo", "BP-Cobertura"):
            old.append(sp)
    for sp in old:
        ifcopenshell.api.run("root.remove_product", f, product=sp)
    print("espaços genéricos removidos:", len(old))

    tot_w = tot_s = 0
    for fl, fd in DATA.items():
        if fl not in FLOORS:
            continue
        stn, base_z, h = FLOORS[fl]
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == stn)
        off = storey_off(st)
        walls = []
        for w in fd["walls"]:
            wl = make_wall(w[:2], w[2:], h, st, off, base_z)
            if wl:
                walls.append(wl)
        if walls:
            f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                            OwnerHistory=OWNER, RelatedElements=walls, RelatingStructure=st)
            assoc(walls, "Alvenaria Bloco Cerâmico Rebocado")
        spaces = []
        for nm, ar, cx, cy in fd["rooms"]:
            spaces.append(make_space(f"{fl[:3].upper()}-{nm[:18]}", nm, ar, cx, cy, st, off, base_z, h))
        if spaces:
            f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                            RelatingObject=st, RelatedObjects=spaces)
        tot_w += len(walls); tot_s += len(spaces)
        print(f"{fl}: {len(walls)} paredes-divisoria, {len(spaces)} ambientes")
    f.write(OUT)
    print(f"Total: {tot_w} paredes + {tot_s} espacos | escrito {OUT}")


if __name__ == "__main__":
    main()
