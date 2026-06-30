#!/usr/bin/env python3
"""
HVG Inhotim — revisão v113: portas (esquadrias) internas do Bloco Principal.

Detecta as portas pela geometria de abertura (arcos da camada ESQUADRIA da
planta 031: centro = dobradiça, raio = largura), mapeia 1:1 ao footprint
calibrado e, para cada porta, encontra a parede-divisória hospedeira (v112),
cria a abertura (IfcOpeningElement, IfcRelVoidsElement) e a IfcDoor que a
preenche (IfcRelFillsElement).

Entrada : HVG_MASTER_v112_DIVISORIAS.ifc  +  bp_doors.json
Saída   : HVG_MASTER_v113_PORTAS.ifc
"""
import json
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v112_DIVISORIAS.ifc"
OUT = "HVG_MASTER_v113_PORTAS.ifc"
DOORS = json.load(open("/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad/bp_doors.json", encoding="utf-8"))

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")
DH = 2.10        # altura de porta
THICK = 0.15
FLOORS = {"Subsolo": "BP-Subsolo", "Terreo": "BP-Terreo"}


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


def wall_geom(w, off):
    """Midpoint (mundo, xy), direção u, comprimento L, e base Z (mundo)."""
    rp = w.ObjectPlacement.RelativePlacement
    loc = np.array(rp.Location.Coordinates)
    M = loc[:2] + off[:2]
    base_z = loc[2] + off[2]
    u = np.array(rp.RefDirection.DirectionRatios[:2]) if rp.RefDirection else np.array([1.0, 0])
    L = w.Representation.Representations[0].Items[0].SweptArea.XDim
    return M, u / (np.linalg.norm(u) or 1), float(L), base_z


def box_solid(w_, d_, h_):
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D", Location=Pt([0, 0])),
                           XDim=float(w_), YDim=float(d_))
    return f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                           Position=f.create_entity("IfcAxis2Placement3D", Location=Pt([0, 0, 0])),
                           ExtrudedDirection=Dir([0, 0, 1]), Depth=float(h_))


def rep(solid):
    sh = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                         RepresentationIdentifier="Body", RepresentationType="SweptSolid",
                         Items=[solid])
    return f.create_entity("IfcProductDefinitionShape", Representations=[sh])


def local_plc(wall, lx):
    """Placement relativo à parede, em (lx, 0, 0) no frame local da parede."""
    return f.create_entity("IfcLocalPlacement", PlacementRelTo=wall.ObjectPlacement,
                           RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                               Location=Pt([lx, 0.0, 0.0])))


def seg_dist(c, M, u, L):
    """Distância do ponto c ao segmento de parede (centro M, dir u, comp L)."""
    t = np.clip(np.dot(c - M, u), -L / 2, L / 2)
    proj = M + t * u
    return np.linalg.norm(c - proj), t


def main():
    walls_by_floor = {}
    for fl, stn in FLOORS.items():
        st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == stn)
        off = storey_off(st)
        ws = []
        for w in f.by_type("IfcWall"):
            if (w.Name or "") != "Parede-Divisoria-Alvenaria":
                continue
            c = ue.get_container(w)
            if not c or c.Name != stn:
                continue
            M, u, L, bz = wall_geom(w, off)
            ws.append((w, M, u, L, bz))
        walls_by_floor[fl] = (st, off, ws)

    total = 0
    for fl, doors in DOORS.items():
        if fl not in FLOORS:
            continue
        st, off, ws = walls_by_floor[fl]
        made = []
        for dx, dy, dw in doors:
            c = np.array([dx, dy])
            best = None
            for (w, M, u, L, bz) in ws:
                if L < dw:
                    continue
                dist, t = seg_dist(c, M, u, L)
                if best is None or dist < best[0]:
                    best = (dist, w, M, u, L, bz, t)
            if best is None or best[0] > 1.5:
                continue
            _, w, M, u, L, bz, t = best
            lx = float(np.clip(t, -L / 2 + dw / 2, L / 2 - dw / 2))
            # abertura que vaza a parede
            opening = f.create_entity("IfcOpeningElement", GlobalId=gid(), OwnerHistory=OWNER,
                                      Name="Vao-Porta", ObjectPlacement=local_plc(w, lx),
                                      Representation=rep(box_solid(dw, THICK + 0.2, DH)),
                                      PredefinedType="OPENING")
            f.create_entity("IfcRelVoidsElement", GlobalId=gid(), OwnerHistory=OWNER,
                            RelatingBuildingElement=w, RelatedOpeningElement=opening)
            # porta que preenche
            door = f.create_entity("IfcDoor", GlobalId=gid(), OwnerHistory=OWNER,
                                   Name=f"Porta-{dw:.2f}x{DH:.2f}", ObjectPlacement=local_plc(w, lx),
                                   Representation=rep(box_solid(dw, 0.05, DH - 0.05)),
                                   OverallHeight=DH, OverallWidth=float(dw),
                                   PredefinedType="DOOR", OperationType="SINGLE_SWING_LEFT")
            f.create_entity("IfcRelFillsElement", GlobalId=gid(), OwnerHistory=OWNER,
                            RelatingOpeningElement=opening, RelatedBuildingElement=door)
            made.append(door)
        if made:
            f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                            OwnerHistory=OWNER, RelatedElements=made, RelatingStructure=st)
        total += len(made)
        print(f"{fl}: {len(made)} portas (de {len(doors)} detectadas)")
    f.write(OUT)
    print(f"Total portas: {total} | escrito {OUT}")


if __name__ == "__main__":
    main()
