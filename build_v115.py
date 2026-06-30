#!/usr/bin/env python3
"""
HVG Inhotim — revisão v115: clerestório, guarda-corpos e mobiliário/louças do BP.

1. Clerestório: banda de vidro do topo do Térreo (3,55) até sob o beiral (3,95),
   no perímetro — o "vidro acima do forro até o beiral".
2. Guarda-corpos envidraçados (IfcRailing) no perímetro do Térreo (h=1,10 m).
3. Mobiliário (camada MOB, 420 blocos) -> IfcFurniture.
4. Louças sanitárias (camada Loiças, 169) -> IfcSanitaryTerminal.

Entrada : HVG_MASTER_v114_FACHADAS.ifc  +  bp_furniture.json
Saída   : HVG_MASTER_v115_ACABAMENTOS.ifc
"""
import json
import numpy as np
import ifcopenshell
import ifcopenshell.guid

SRC = "HVG_MASTER_v114_FACHADAS.ifc"
OUT = "HVG_MASTER_v115_ACABAMENTOS.ifc"
FUR = json.load(open("/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad/bp_furniture.json", encoding="utf-8"))

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType == "Model")
GX0, GX1, GY0, GY1 = 135.65, 194.35, 216.5, 273.5
FZ = {"Subsolo": ("BP-Subsolo", -3.0), "Terreo": ("BP-Terreo", 0.0)}


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


MAT = {}
def material(n):
    if n not in MAT:
        MAT[n] = next((m for m in f.by_type("IfcMaterial") if m.Name == n), None) or f.create_entity("IfcMaterial", Name=n)
    return MAT[n]
def assoc(els, n):
    if els: f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER, RelatedObjects=list(els), RelatingMaterial=material(n))
def contain(els, st):
    if els: f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(), OwnerHistory=OWNER, RelatedElements=list(els), RelatingStructure=st)


def vbox(cls, name, cx, cy, base_z, dx, dy, dz, st, off, ptype=None, refdir=None):
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=float(dx), YDim=float(dy))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=float(dz))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX, RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    a2 = f.create_entity("IfcAxis2Placement3D", Location=Pt([cx - off[0], cy - off[1], base_z - off[2]]),
                         Axis=Dir([0, 0, 1]), RefDirection=Dir(refdir or [1, 0, 0]))
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement, RelativePlacement=a2)
    kw = dict(GlobalId=gid(), OwnerHistory=OWNER, Name=name, ObjectPlacement=pl, Representation=prod)
    if ptype is not None: kw["PredefinedType"] = ptype
    return f.create_entity(cls, **kw)


def perimeter_band(name, cls, z0, dz, st, off, mat, ptype=None, inset=0.0):
    """Quatro elementos no perímetro (faixas finas verticais)."""
    els = []
    x0, x1, y0, y1 = GX0 + inset, GX1 - inset, GY0 + inset, GY1 - inset
    specs = [((x0 + x1) / 2, y0, x1 - x0, 0.04, [1, 0, 0]),
             ((x0 + x1) / 2, y1, x1 - x0, 0.04, [1, 0, 0]),
             (x0, (y0 + y1) / 2, y1 - y0, 0.04, [0, 1, 0]),
             (x1, (y0 + y1) / 2, y1 - y0, 0.04, [0, 1, 0])]
    for cx, cy, ln, th, rd in specs:
        els.append(vbox(cls, name, cx, cy, z0, ln, th, dz, st, off, ptype, rd))
    contain(els, st); assoc(els, mat)
    return els


def main():
    ster = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Terreo")
    offt = storey_off(ster)

    # 1. clerestório (3.55 -> 3.95, sob o beiral)
    cl = perimeter_band("Clerestorio-Vidro", "IfcPlate", 3.55, 0.40, ster, offt,
                        "Vidro Laminado Fachada", "SHEET", inset=0.05)
    # 2. guarda-corpos envidraçados (h=1.10, no piso do Terreo)
    gc = perimeter_band("Guarda-Corpo-Vidro", "IfcRailing", 0.0, 1.10, ster, offt,
                        "Vidro Temperado Guarda-Corpo", None, inset=0.20)

    # 3. mobiliário + 4. louças
    nf = ns = 0
    for fl, fd in FUR.items():
        if fl not in FZ: continue
        stn, bz = FZ[fl]
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == stn)
        off = storey_off(st)
        furn = []
        for x, y, nm in fd["furniture"]:
            big = "banco" in nm.lower()
            dx, dy, dz = (1.6, 0.45, 0.45) if big else (0.5, 0.5, 0.45)
            furn.append(vbox("IfcFurniture", f"Mob-{nm}", x, y, bz + 0.0, dx, dy, dz, st, off))
        contain(furn, st); assoc(furn, "Mobiliario Generico")
        san = []
        for x, y in fd["sanitary"]:
            san.append(vbox("IfcSanitaryTerminal", "Louca-Sanitaria", x, y, bz, 0.45, 0.6, 0.4, st, off, "WCSEAT"))
        contain(san, st); assoc(san, "Louca Ceramica Sanitaria")
        nf += len(furn); ns += len(san)
        print(f"{fl}: {len(furn)} moveis, {len(san)} loucas")

    f.write(OUT)
    print(f"Clerestorio: {len(cl)} | Guarda-corpos: {len(gc)} | Mobiliario: {nf} | Loucas: {ns}")
    print("Escrito:", OUT)


if __name__ == "__main__":
    main()
