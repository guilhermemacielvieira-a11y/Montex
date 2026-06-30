#!/usr/bin/env python3
"""
HVG Inhotim — revisão v114: fachadas envidraçadas do Bloco Principal.

As fachadas do Bloco Principal são totalmente envidraçadas (fotos p.5–7;
"Envidraçado" na planta do Térreo). Esta revisão remove as 4 paredes de
perímetro do Térreo e modela as 4 fachadas como IfcCurtainWall, cada uma com:
  - montantes verticais (IfcMember MULLION) alinhados à malha (~4,9 m);
  - travessas (IfcMember TRANSOM) inferior/intermédia/superior;
  - pano de vidro (IfcPlate) — material Vidro Laminado.

Entrada : HVG_MASTER_v113_PORTAS.ifc
Saída   : HVG_MASTER_v114_FACHADAS.ifc
"""
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v113_PORTAS.ifc"
OUT = "HVG_MASTER_v114_FACHADAS.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")

GX0, GX1, GY0, GY1 = 135.65, 194.35, 216.5, 273.5
H = 3.55          # altura do envidraçado (Térreo)
BASE = 0.0
NX = NY = 13      # eixos da malha


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


def bar(cls, name, p0, p1, w, h, off, relto, ptype):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    d = d / L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    ref = np.cross(up, d); ref = ref / np.linalg.norm(ref)
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=float(w), YDim=float(h))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=L)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                            Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=relto,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt((p0 - off).tolist()),
                             Axis=Dir(d.tolist()), RefDirection=Dir(ref.tolist())))
    return f.create_entity(cls, GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                           ObjectPlacement=pl, Representation=prod, PredefinedType=ptype)


def glass_plate(name, mid, u, Lf, off, relto):
    """Pano de vidro: caixa vertical fina (Lf ao longo de u, 0.025 perpendicular)."""
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=float(Lf), YDim=0.025)
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                            ExtrudedDirection=Dir([0, 0, 1]), Depth=H)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                            Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    loc = [mid[0] - off[0], mid[1] - off[1], BASE - off[2]]
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=relto,
                         RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                             Location=Pt(loc), Axis=Dir([0, 0, 1]),
                             RefDirection=Dir([u[0], u[1], 0])))
    return f.create_entity("IfcPlate", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                           ObjectPlacement=pl, Representation=prod, PredefinedType="SHEET")


def facade(name, P0, P1, axis_positions, st, off):
    P0 = np.array(P0, float); P1 = np.array(P1, float)
    d = P1 - P0; Lf = np.linalg.norm(d); u = d / Lf
    mid = (P0 + P1) / 2
    relto = st.ObjectPlacement
    members, plates = [], []
    # montantes verticais na malha
    for t in axis_positions:
        base = P0 + u * t
        members.append(bar("IfcMember", "Montante-Fachada",
                           [base[0], base[1], BASE], [base[0], base[1], BASE + H],
                           0.08, 0.15, off, relto, "MULLION"))
    # montantes nas pontas
    for base in (P0, P1):
        members.append(bar("IfcMember", "Montante-Fachada",
                           [base[0], base[1], BASE], [base[0], base[1], BASE + H],
                           0.08, 0.15, off, relto, "MULLION"))
    # travessas inferior/intermedia/superior
    for zt in (BASE + 0.10, BASE + 1.80, BASE + H - 0.08):
        members.append(bar("IfcMember", "Travessa-Fachada",
                           [P0[0], P0[1], zt], [P1[0], P1[1], zt],
                           0.15, 0.08, off, relto, "MULLION"))
    members = [m for m in members if m]
    plates.append(glass_plate("Pano-Vidro-Fachada", mid, u, Lf - 0.05, off, relto))
    cw = f.create_entity("IfcCurtainWall", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                         ObjectPlacement=f.create_entity("IfcLocalPlacement",
                             RelativePlacement=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0]))),
                         PredefinedType="NOTDEFINED")
    f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatingObject=cw, RelatedObjects=members + plates)
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedElements=[cw], RelatingStructure=st)
    assoc(members, "Alumínio Anodizado Fachada")
    assoc(plates, "Vidro Laminado Fachada")
    return len(members), len(plates)


def main():
    st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Terreo")
    off = storey_off(st)
    # remove as 4 paredes de perimetro do Terreo (Pedra Aparente, Z0..3.55)
    rm = []
    for w in f.by_type("IfcWall"):
        if "Pedra Aparente" not in (w.Name or ""):
            continue
        c = ue.get_container(w)
        if c and c.Name == "BP-Terreo":
            rm.append(w)
    for w in rm:
        ifcopenshell.api.run("root.remove_product", f, product=w)
    print("paredes de perimetro do Terreo removidas:", len(rm))

    xs = np.linspace(GX0, GX1, NX)[1:-1]
    ys = np.linspace(GY0, GY1, NY)[1:-1]
    txs = [x - GX0 for x in xs]      # posições ao longo das fachadas S/N
    tys = [y - GY0 for y in ys]      # ao longo das fachadas O/L
    fac = [
        ("Fachada-1-Sul", [GX0, GY0], [GX1, GY0], txs),
        ("Fachada-2-Norte", [GX0, GY1], [GX1, GY1], txs),
        ("Fachada-3-Oeste", [GX0, GY0], [GX0, GY1], tys),
        ("Fachada-4-Leste", [GX1, GY0], [GX1, GY1], tys),
    ]
    tm = tp = 0
    for name, P0, P1, pos in fac:
        nm, npl = facade(name, P0, P1, pos, st, off)
        tm += nm; tp += npl
        print(f"{name}: {nm} montantes/travessas + {npl} pano de vidro")
    f.write(OUT)
    print(f"Total: 4 IfcCurtainWall, {tm} IfcMember, {tp} IfcPlate | escrito {OUT}")


if __name__ == "__main__":
    main()
