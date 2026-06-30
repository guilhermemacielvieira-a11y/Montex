#!/usr/bin/env python3
"""
HVG Inhotim — revisão v111: detalhamento dos pavimentos do Bloco Principal.

Substitui os 16 espaços genéricos do Bloco Principal pelo PROGRAMA REAL de
ambientes lido da planta oficial (031 - Bloco Principal - Plantas.dwg, via
LibreDWG): 32 ambientes no Subsolo (~2.083 m²) e 23 no Térreo (~1.103 m²),
cada um como IfcSpace nomeado, com área em Qto_SpaceBaseQuantities, posicionado
(por mapeamento PCA da planta) dentro do footprint calibrado 58,7×57 m.

Níveis conferidos no corte/fachadas (032): datum 0,00; térreo escalonado
5,00/8,40; cobertura ~11,70; pé-direito ~2,75–2,84 m.

Entrada : HVG_MASTER_v110_BP_CALIBRADO.ifc  +  bp_rooms.json
Saída   : HVG_MASTER_v111_PAVIMENTOS.ifc
"""
import json
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v110_BP_CALIBRADO.ifc"
OUT = "HVG_MASTER_v111_PAVIMENTOS.ifc"
ROOMS = json.load(open("/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad/bp_rooms.json", encoding="utf-8"))

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")

# footprint calibrado
GX0, GX1, GY0, GY1 = 135.65, 194.35, 216.5, 273.5
FLOORS = {"Subsolo": ("BP-Subsolo", -3.0, 2.80), "Terreo": ("BP-Terreo", 0.0, 2.84)}


def gid():
    return ifcopenshell.guid.new()


def Pt(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def storey_off(st):
    o = np.zeros(3); p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location:
            o = o + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return o


def bof(e):
    c = ue.get_container(e)
    while c and not c.is_a("IfcBuilding"):
        c = c.Decomposes[0].RelatingObject if c.Decomposes else None
    return c.Name if c else "?"


def make_space(name, long_name, area, cx, cy, st, off, zf, h):
    side = float(np.clip(np.sqrt(area), 1.5, 12.0))
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=side, YDim=side)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=[0., 0., 1.]),
                            Depth=float(h))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                            Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    loc = [cx - off[0], cy - off[1], zf - off[2]]
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D", Location=Pt(loc)))
    sp = f.create_entity("IfcSpace", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                         LongName=long_name, ObjectPlacement=pl, Representation=prod,
                         CompositionType="ELEMENT", PredefinedType="INTERNAL")
    # Qto area
    q = f.create_entity("IfcQuantityArea", Name="GrossFloorArea", AreaValue=float(area))
    f.create_entity("IfcElementQuantity", GlobalId=gid(), OwnerHistory=OWNER,
                    Name="Qto_SpaceBaseQuantities", Quantities=[q])
    qrel = f.by_type("IfcElementQuantity")[-1]
    f.create_entity("IfcRelDefinesByProperties", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=[sp], RelatingPropertyDefinition=qrel)
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

    total = 0
    for fl, rooms in ROOMS.items():
        if fl not in FLOORS:
            continue
        st_name, zf, h = FLOORS[fl]
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == st_name)
        off = storey_off(st)
        spaces = []
        for r in rooms:
            cx = GX0 + r["u"] * (GX1 - GX0)
            cy = GY0 + r["v"] * (GY1 - GY0)
            sp = make_space(f"{fl[:3].upper()}-{r['name'][:18]}", r["name"], r["area"],
                            cx, cy, st, off, zf, h)
            spaces.append(sp)
        f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                        RelatingObject=st, RelatedObjects=spaces)
        total += len(spaces)
        print(f"{fl}: {len(spaces)} ambientes detalhados (area {sum(r['area'] for r in rooms):.0f} m²)")
    f.write(OUT)
    print("Total espaços:", total, "| escrito:", OUT)


if __name__ == "__main__":
    main()
