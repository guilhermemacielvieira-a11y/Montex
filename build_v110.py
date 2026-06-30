#!/usr/bin/env python3
"""
HVG Inhotim — construtor da revisão v110 (calibração do Bloco Principal pela
PLANTA OFICIAL e formalização do IfcGrid).

A planta oficial de arquitetura ("031 - Bloco Principal - Plantas.dwg",
extraída via LibreDWG) traz as cotas reais do edifício:
  - footprint do Bloco Principal ≈ 58,7 m (X) × 57,0 m (Y)  — quase quadrado
  - malha estrutural ≈ 4,9 m  (documentada como ~4,97 m)  → ~12 vãos por eixo

O modelo (80×80, 17×17 = 289 pilares a 5 m) estava SUPERDIMENSIONADO, e a v109
(101×63) foi na direção errada. Esta revisão recalibra o bloco pela planta:
  - rebaseia no v108 (planta quadrada original + SPA/cenografia preservados);
  - escala paredes/lajes/terminais/escadas/espaços para 58,7×57 m;
  - RECONSTRÓI a malha de pilares como 13×13 eixos a ~4,9 m (169 pilares);
  - cria o IfcGrid (eixos 1..13 × A..M);
  - regenera a cobertura (hip) e a treliça espacial da recepção.

Entrada : HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc
Saída   : HVG_MASTER_v110_BP_CALIBRADO.ifc
"""
import math
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc"
OUT = "HVG_MASTER_v110_BP_CALIBRADO.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")
SITE = f.by_type("IfcSite")[0]

# ---- alvos da planta oficial ----
CX, CY = 165.0, 245.0
FOOT_X, FOOT_Y = 58.70, 57.00          # footprint real (m)
OLD_FOOT = 79.60                       # extensão atual dos pilares (m)
KX = FOOT_X / OLD_FOOT                  # ~0,737
KY = FOOT_Y / OLD_FOOT                  # ~0,716
NX = NY = 13                            # eixos (12 vãos)
GX0, GX1 = CX - FOOT_X / 2, CX + FOOT_X / 2
GY0, GY1 = CY - FOOT_Y / 2, CY + FOOT_Y / 2


def gid():
    return ifcopenshell.guid.new()


def Pt(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def Dir(v):
    return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def bof(e):
    c = ue.get_container(e)
    while c and not c.is_a("IfcBuilding"):
        c = c.Decomposes[0].RelatingObject if c.Decomposes else None
    return c.Name if c else "?"


def storey_off(st):
    o = np.zeros(3); p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location:
            o = o + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return o


def chain_xy(pl):
    o = np.zeros(2); p = pl
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location:
            c = rp.Location.Coordinates
            o = o + np.array([c[0], c[1]])
        p = p.PlacementRelTo
    return o


def scale_about(xy):
    return np.array([CX + (xy[0] - CX) * KX, CY + (xy[1] - CY) * KY])


def reposition(elem):
    rp = elem.ObjectPlacement.RelativePlacement
    if rp is None or rp.Location is None:
        return False
    o = chain_xy(elem.ObjectPlacement)
    d = scale_about(o) - o
    c = list(rp.Location.Coordinates)
    c[0] += float(d[0]); c[1] += float(d[1])
    rp.Location = Pt(c)
    return True


def scale_rect(sol, fx, fy):
    pa = sol.SweptArea
    if not pa.is_a("IfcRectangleProfileDef"):
        return False
    pos = pa.Position
    ref = pos.RefDirection.DirectionRatios if (pos and pos.RefDirection) else (1.0, 0.0)
    aligned = abs(ref[0]) > 0.99
    pa.XDim = float(pa.XDim * (fx if aligned else fy))
    pa.YDim = float(pa.YDim * (fy if aligned else fx))
    return True


MAT = {}
def material(name):
    if name not in MAT:
        MAT[name] = next((m for m in f.by_type("IfcMaterial") if m.Name == name), None) \
                    or f.create_entity("IfcMaterial", Name=name)
    return MAT[name]


def assoc(elems, name):
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=list(elems), RelatingMaterial=material(name))


def contain(elems, st):
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=list(elems), RelatingStructure=st)


# ------------------------------------------------- colunas (grid 13x13)
def build_columns(sub):
    off = storey_off(sub)
    xs = np.linspace(GX0, GX1, NX)
    ys = np.linspace(GY0, GY1, NY)
    cols = []
    for ix, x in enumerate(xs):
        for iy, y in enumerate(ys):
            prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                                   Position=f.create_entity("IfcAxis2Placement2D",
                                                            Location=Pt([0, 0])),
                                   XDim=0.30, YDim=0.30)
            solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                                    Position=f.create_entity("IfcAxis2Placement3D",
                                                             Location=Pt([0, 0, 0])),
                                    ExtrudedDirection=Dir([0, 0, 1]), Depth=6.85)
            shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                                    RepresentationIdentifier="Body",
                                    RepresentationType="SweptSolid", Items=[solid])
            prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
            loc = [x - off[0], y - off[1], -3.0 - off[2]]
            pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=sub.ObjectPlacement,
                                 RelativePlacement=f.create_entity(
                                     "IfcAxis2Placement3D", Location=Pt(loc)))
            col = f.create_entity("IfcColumn", GlobalId=gid(), OwnerHistory=OWNER,
                                  Name=f"Pilar-BP-{chr(65+iy)}{ix+1}",
                                  ObjectPlacement=pl, Representation=prod,
                                  PredefinedType="COLUMN")
            cols.append(col)
    contain(cols, sub)
    assoc(cols, "Concreto Armado C25")
    return cols, xs, ys


# ------------------------------------------------- IfcGrid
def build_grid(xs, ys, st):
    def axis(tag, p0, p1):
        poly = f.create_entity("IfcPolyline", Points=[Pt(p0), Pt(p1)])
        return f.create_entity("IfcGridAxis", AxisTag=tag, AxisCurve=poly,
                               SameSense=True)
    u = [axis(str(i + 1), [x, GY0 - 2, 0], [x, GY1 + 2, 0]) for i, x in enumerate(xs)]
    v = [axis(chr(65 + i), [GX0 - 2, y, 0], [GX1 + 2, y, 0]) for i, y in enumerate(ys)]
    # geometria do grid (linhas) para visualização
    items = []
    for ax in u + v:
        items.append(ax.AxisCurve)
    rep = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                          RepresentationIdentifier="FootPrint",
                          RepresentationType="GeometricCurveSet", Items=items)
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[rep])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity(
                             "IfcAxis2Placement3D",
                             Location=Pt([-storey_off(st)[0], -storey_off(st)[1],
                                          3.6 - storey_off(st)[2]])))
    grid = f.create_entity("IfcGrid", GlobalId=gid(), OwnerHistory=OWNER,
                           Name="BP-Malha-Estrutural", ObjectPlacement=pl,
                           Representation=prod, UAxes=u, VAxes=v)
    contain([grid], st)
    return grid


# ------------------------------------------------- cobertura + treliça (de v109)
def faceted_brep(vl, faces):
    pts = [Pt(v) for v in vl]
    ff = []
    for idx in faces:
        loop = f.create_entity("IfcPolyLoop", Polygon=[pts[i] for i in idx])
        ff.append(f.create_entity("IfcFace", Bounds=[
            f.create_entity("IfcFaceOuterBound", Bound=loop, Orientation=True)]))
    return f.create_entity("IfcFacetedBrep",
                           Outer=f.create_entity("IfcClosedShell", CfsFaces=ff))


def build_roof(st):
    off = storey_off(st); OV = 2.5
    Xe0, Xe1 = GX0 - OV, GX1 + OV
    Ye0, Ye1 = GY0 - OV, GY1 + OV
    Z_E, Z_R = 3.70, 7.60
    Ym = (Ye0 + Ye1) / 2; depth = Ye1 - Ye0
    Lr = max(1.0, (Xe1 - Xe0) - depth)
    Xc = (Xe0 + Xe1) / 2
    Xr0, Xr1 = Xc - Lr / 2, Xc + Lr / 2
    W = [(Xe0, Ye0, Z_E), (Xe1, Ye0, Z_E), (Xe1, Ye1, Z_E), (Xe0, Ye1, Z_E),
         (Xr0, Ym, Z_R), (Xr1, Ym, Z_R)]
    A, B, C, D, R0, R1 = range(6)
    faces = [[A, B, C, D], [A, B, R1, R0], [C, D, R0, R1], [D, A, R0], [B, C, R1]]
    vl = [(x - off[0], y - off[1], z - off[2]) for (x, y, z) in W]
    brep = faceted_brep(vl, faces)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="Brep", Items=[brep])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
                         RelativePlacement=f.create_entity(
                             "IfcAxis2Placement3D", Location=Pt([0, 0, 0])))
    roof = f.create_entity("IfcRoof", GlobalId=gid(), OwnerHistory=OWNER,
                           Name="Cobertura-4Aguas (Hip)-Beiral-Calibrada-Telha Ceramica",
                           ObjectPlacement=pl, Representation=prod, PredefinedType="HIP_ROOF")
    contain([roof], st)
    assoc([roof], "Telha Cerâmica Vila Galé")


def bar(name, p0, p1, w, h, off, relto):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    d = d / L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    ref = np.cross(up, d); ref = ref / np.linalg.norm(ref)
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=relto,
                         RelativePlacement=f.create_entity(
                             "IfcAxis2Placement3D", Location=Pt((p0 - off).tolist()),
                             Axis=Dir(d.tolist()), RefDirection=Dir(ref.tolist())))
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
    return f.create_entity("IfcMember", GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                           ObjectPlacement=pl, Representation=prod, PredefinedType="MEMBER")


def build_truss(st):
    off = storey_off(st)
    X0 = CX + (146 - CX) * KX; X1 = CX + (184 - CX) * KX
    Y0 = CY + (226 - CY) * KY; Y1 = CY + (264 - CY) * KY
    Z_TOP, DEPTH = 3.85, 1.10
    Z_BOT = Z_TOP - DEPTH
    mod = 5.0
    nx = max(2, round((X1 - X0) / mod)); ny = max(2, round((Y1 - Y0) / mod))
    xs = np.linspace(X0, X1, nx + 1); ys = np.linspace(Y0, Y1, ny + 1)
    xb = (xs[:-1] + xs[1:]) / 2; yb = (ys[:-1] + ys[1:]) / 2
    sc, sd = (0.12, 0.12), (0.09, 0.09)
    asm = f.create_entity("IfcElementAssembly", GlobalId=gid(), OwnerHistory=OWNER,
                          Name="BP-Recepcao-Trelica-Espacial",
                          ObjectPlacement=f.create_entity("IfcLocalPlacement",
                              RelativePlacement=f.create_entity("IfcAxis2Placement3D",
                                                                Location=Pt([0, 0, 0]))),
                          PredefinedType="TRUSS")
    M = []
    top = lambda i, j: (xs[i], ys[j], Z_TOP)
    bot = lambda i, j: (xb[i], yb[j], Z_BOT)
    for j in range(len(ys)):
        for i in range(len(xs) - 1):
            M.append(bar("Banzo-Sup-X", top(i, j), top(i + 1, j), *sc, off, st.ObjectPlacement))
    for i in range(len(xs)):
        for j in range(len(ys) - 1):
            M.append(bar("Banzo-Sup-Y", top(i, j), top(i, j + 1), *sc, off, st.ObjectPlacement))
    for j in range(len(yb)):
        for i in range(len(xb) - 1):
            M.append(bar("Banzo-Inf-X", bot(i, j), bot(i + 1, j), *sc, off, st.ObjectPlacement))
    for i in range(len(xb)):
        for j in range(len(yb) - 1):
            M.append(bar("Banzo-Inf-Y", bot(i, j), bot(i, j + 1), *sc, off, st.ObjectPlacement))
    for i in range(len(xb)):
        for j in range(len(yb)):
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                M.append(bar("Diagonal", bot(i, j), top(i + dx, j + dy), *sd, off, st.ObjectPlacement))
    M = [m for m in M if m]
    f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatingObject=asm, RelatedObjects=M)
    contain([asm], st)
    assoc(M, "Aço Estrutural ASTM A572 (Treliça Aparente)")
    return len(M)


def main():
    sub = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Subsolo")
    ter = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Terreo")
    bp = [e for e in f.by_type("IfcProduct") if bof(e) == "Bloco Principal"]

    # IMPORTANTE: remover o IfcElementAssembly CASCATEIA a remoção dos seus
    # IfcMember agregados — por isso a lista de membros não é tocada à parte
    # (evita acesso a entidades já liberadas -> segfault).
    roofs = [e for e in bp if e.is_a("IfcRoof")]
    asms = [e for e in bp if e.is_a("IfcElementAssembly")]
    columns = [e for e in bp if e.is_a("IfcColumn")]
    members = [e for e in bp if e.is_a("IfcMember")]
    removed = set(id(e) for e in roofs + asms + columns + members)
    survivors = [e for e in bp if id(e) not in removed]
    for e in roofs + asms:
        ifcopenshell.api.run("root.remove_product", f, product=e)
    for e in columns:
        ifcopenshell.api.run("root.remove_product", f, product=e)

    SKIP = ("IfcStairFlight", "IfcOpeningElement")
    moved = w = s_ = 0
    for e in survivors:
        if e.is_a() in SKIP:
            continue
        try:
            if reposition(e):
                moved += 1
            rep = e.Representation
            if rep and not e.is_a("IfcSpace"):
                sol = rep.Representations[0].Items[0]
                if e.is_a() in ("IfcWall", "IfcSlab") and sol.is_a("IfcExtrudedAreaSolid"):
                    if scale_rect(sol, KX, KY):
                        w += 1
        except Exception as ex:
            print("aviso:", e.is_a(), ex)
    # espaços
    for sp in f.by_type("IfcSpace"):
        par = sp.Decomposes[0].RelatingObject if sp.Decomposes else None
        if par and par.Name in ("BP-Subsolo", "BP-Terreo", "BP-Cobertura"):
            rep = sp.Representation
            if rep:
                sol = rep.Representations[0].Items[0]
                if sol.is_a("IfcExtrudedAreaSolid"):
                    scale_rect(sol, KX, KY)
            reposition(sp); s_ += 1

    cols, xs, ys = build_columns(sub)
    grid = build_grid(xs, ys, ter)
    build_roof(ter)
    nt = build_truss(ter)

    f.write(OUT)
    print(f"Reposicionados {moved} | paredes/lajes escaladas {w} | espacos {s_}")
    print(f"Pilares reconstruidos: {len(cols)} ({NX}x{NY}), modulo X={ (GX1-GX0)/(NX-1):.2f} "
          f"Y={(GY1-GY0)/(NY-1):.2f} m")
    print(f"IfcGrid: {len(grid.UAxes)}x{len(grid.VAxes)} eixos | footprint {FOOT_X}x{FOOT_Y} m")
    print(f"Trelica: {nt} barras | cobertura regenerada")
    print("Escrito:", OUT)


if __name__ == "__main__":
    main()
