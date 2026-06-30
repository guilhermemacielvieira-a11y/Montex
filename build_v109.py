#!/usr/bin/env python3
"""
HVG Inhotim — construtor da revisão v109 (reestruturação da planta do Bloco
Principal: pegada quase quadrada -> proporção retangular real).

A planta do Bloco Principal era ~80 x 80 m (quase quadrada), o que forçava
qualquer cobertura de 4 águas a um aspecto piramidal. Esta revisão aplica uma
**escala anisotrópica preservando a área** (alonga X, comprime Y, razão ~1,6:1)
a TODOS os elementos do edifício, e regenera a cobertura (agora com cumeeira
longa) e a treliça espacial da recepção sobre a nova pegada retangular.

Estratégia (BP é um pavilhão de pilares — 289 pilares, 8 paredes perimetrais,
2 lajes, 4 janelas):
  - reposiciona cada elemento por escala da origem do seu placement em torno
    do centro C (pilares, terminais, escadas, janelas, vigas, etc.);
  - estica as 8 paredes perimetrais (XDim do perfil) e as 2 lajes (XDim,YDim);
  - regenera a cobertura hip com cumeeira longa;
  - reconstrói a treliça espacial (288 barras) sobre o novo átrio.

Entrada : HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc
Saída   : HVG_MASTER_v109_PLANTA_RETANGULAR.ifc
"""
import math
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc"
OUT = "HVG_MASTER_v109_PLANTA_RETANGULAR.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")

# centro do bloco e fatores (área preservada, razão alvo ~1,6:1)
CX, CY = 165.0, 245.0
RATIO = 1.6
KX = math.sqrt(RATIO)          # ~1,2649  (alonga X)
KY = 1.0 / math.sqrt(RATIO)    # ~0,7906  (comprime Y)


def gid():
    return ifcopenshell.guid.new()


def P(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def D(v):
    return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def building_of(e):
    c = ue.get_container(e)
    while c and not c.is_a("IfcBuilding"):
        c = c.Decomposes[0].RelatingObject if c.Decomposes else None
    return c.Name if c else "?"


def chain_origin_xy(placement):
    """Origem (mundo) somando as translações da cadeia de placement (xy)."""
    o = np.zeros(2)
    p = placement
    while p is not None:
        rp = p.RelativePlacement
        if rp and rp.Location:
            c = rp.Location.Coordinates
            o = o + np.array([c[0], c[1]])
        p = p.PlacementRelTo
    return o


def scale_about(xy):
    return np.array([CX + (xy[0] - CX) * KX, CY + (xy[1] - CY) * KY])


def reposition(elem):
    """Desloca o elemento escalando a origem do seu placement em torno de C."""
    pl = elem.ObjectPlacement
    rp = pl.RelativePlacement
    if rp is None or rp.Location is None:
        return False
    o = chain_origin_xy(pl)               # origem mundo atual
    tgt = scale_about(o)
    d = tgt - o
    c = list(rp.Location.Coordinates)
    c[0] += float(d[0]); c[1] += float(d[1])
    rp.Location = P(c)
    return True


def scale_rect_profile(solid, fx, fy):
    """Escala XDim/YDim de um IfcRectangleProfileDef (se eixo não rotacionado)."""
    pa = solid.SweptArea
    if not pa.is_a("IfcRectangleProfileDef"):
        return False
    pos = pa.Position
    ref = pos.RefDirection.DirectionRatios if (pos and pos.RefDirection) else (1.0, 0.0)
    aligned = abs(ref[0]) > 0.99      # local-X ~ world-X
    pa.XDim = float(pa.XDim * (fx if aligned else fy))
    pa.YDim = float(pa.YDim * (fy if aligned else fx))
    return True


def is_top_level(elem):
    """True se o placement do elemento é relativo a uma estrutura espacial
    (storey/building/site) — evita mover filhos (flights/openings) duas vezes."""
    parent = elem.ObjectPlacement.PlacementRelTo
    if parent is None:
        return True
    # algum produto espacial usa esse placement?
    for s in f.by_type("IfcSpatialStructureElement"):
        if s.ObjectPlacement is parent:
            return True
    return False


# ----------------------------------------------------------- execução
def main():
    bp_elems = [e for e in f.by_type("IfcProduct")
                if building_of(e) == "Bloco Principal"]

    # 1) remove cobertura e treliça antigas (serão regeneradas)
    old_roofs = [e for e in bp_elems if e.is_a("IfcRoof")]
    old_truss_asm = [e for e in bp_elems if e.is_a("IfcElementAssembly")]
    old_truss_mem = [e for e in bp_elems if e.is_a("IfcMember")]
    removed = set(id(e) for e in old_roofs + old_truss_asm + old_truss_mem)
    # sobreviventes capturados ANTES da remoção (evita tocar entidades deletadas)
    survivors = [e for e in bp_elems if id(e) not in removed]
    for e in old_roofs + old_truss_asm:
        ifcopenshell.api.run("root.remove_product", f, product=e)
    for m in old_truss_mem:
        ifcopenshell.api.run("root.remove_product", f, product=m)

    # 2) reposiciona elementos restantes; escala perfis de paredes e lajes
    SKIP = ("IfcStairFlight", "IfcOpeningElement")
    moved = walls = slabs = spaces = 0
    for e in survivors:
        if e.is_a() in SKIP:
            continue
        try:
            if reposition(e):
                moved += 1
            rep = e.Representation
            if rep and not e.is_a("IfcSpace"):
                sol = rep.Representations[0].Items[0]
                if e.is_a("IfcWall") and sol.is_a("IfcExtrudedAreaSolid"):
                    # parede: estica o comprimento (XDim) conforme o eixo
                    if scale_rect_profile(sol, KX, KY):
                        walls += 1
                elif e.is_a("IfcSlab") and sol.is_a("IfcExtrudedAreaSolid"):
                    if scale_rect_profile(sol, KX, KY):
                        slabs += 1
            elif e.is_a("IfcSpace") and rep:
                sol = rep.Representations[0].Items[0]
                if sol.is_a("IfcExtrudedAreaSolid"):
                    scale_rect_profile(sol, KX, KY)
                # reposiciona o espaço também
                reposition(e)
                spaces += 1
        except Exception as ex:
            print("  aviso:", e.is_a(), e.GlobalId, ex)

    # 2b) espaços do BP (decompostos sob os pavimentos BP-*)
    bp_storeys = {"BP-Subsolo", "BP-Terreo", "BP-Cobertura"}
    for sp in f.by_type("IfcSpace"):
        par = sp.Decomposes[0].RelatingObject if sp.Decomposes else None
        if not (par and par.Name in bp_storeys):
            continue
        try:
            rep = sp.Representation
            if rep:
                sol = rep.Representations[0].Items[0]
                if sol.is_a("IfcExtrudedAreaSolid"):
                    scale_rect_profile(sol, KX, KY)
            if reposition(sp):
                spaces += 1
        except Exception as ex:
            print("  aviso espaco:", sp.GlobalId, ex)

    print(f"Reposicionados: {moved} | paredes esticadas: {walls} | "
          f"lajes: {slabs} | espacos: {spaces}")

    # extensão nova do bloco (paredes perímetro)
    Xw0 = CX + (125.1 - CX) * KX; Xw1 = CX + (204.8 - CX) * KX
    Yw0 = CY + (205.2 - CY) * KY; Yw1 = CY + (284.9 - CY) * KY
    print(f"Nova pegada paredes: X[{Xw0:.1f},{Xw1:.1f}] Y[{Yw0:.1f},{Yw1:.1f}]")

    st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Terreo")
    soff = chain_origin_xy(st.ObjectPlacement)
    soffz = 0.0
    p = st.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.Location:
            soffz += rp.Location.Coordinates[2]
        p = p.PlacementRelTo
    off = np.array([soff[0], soff[1], soffz])
    relto = st.ObjectPlacement

    # 3) regenera a cobertura hip com cumeeira LONGA (planta retangular)
    build_roof(Xw0, Xw1, Yw0, Yw1, off, relto, st)

    # 4) reconstrói a treliça espacial sobre o novo átrio
    build_truss(off, relto, st)

    f.write(OUT)
    print("Escrito:", OUT)


def faceted_brep(verts_local, faces):
    pts = [P(v) for v in verts_local]
    ifc_faces = []
    for idx in faces:
        loop = f.create_entity("IfcPolyLoop", Polygon=[pts[i] for i in idx])
        b = f.create_entity("IfcFaceOuterBound", Bound=loop, Orientation=True)
        ifc_faces.append(f.create_entity("IfcFace", Bounds=[b]))
    return f.create_entity("IfcFacetedBrep",
                           Outer=f.create_entity("IfcClosedShell", CfsFaces=ifc_faces))


def build_roof(Xw0, Xw1, Yw0, Yw1, off, relto, st):
    OV = 2.5
    Xe0, Xe1 = Xw0 - OV, Xw1 + OV
    Ye0, Ye1 = Yw0 - OV, Yw1 + OV
    Z_E, Z_R = 3.70, 8.20
    Ym = (Ye0 + Ye1) / 2.0
    depth = Ye1 - Ye0
    Lr = (Xe1 - Xe0) - depth        # cumeeira de hip a 45° (longa)
    Xc = (Xe0 + Xe1) / 2.0
    Xr0, Xr1 = Xc - Lr / 2, Xc + Lr / 2
    W = [(Xe0, Ye0, Z_E), (Xe1, Ye0, Z_E), (Xe1, Ye1, Z_E), (Xe0, Ye1, Z_E),
         (Xr0, Ym, Z_R), (Xr1, Ym, Z_R)]
    A, B, C, Dd, R0, R1 = range(6)
    faces = [[A, B, C, Dd], [A, B, R1, R0], [C, Dd, R0, R1], [Dd, A, R0], [B, C, R1]]
    vlocal = [(x - off[0], y - off[1], z - off[2]) for (x, y, z) in W]
    brep = faceted_brep(vlocal, faces)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="Brep", Items=[brep])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=relto,
                         RelativePlacement=f.create_entity(
                             "IfcAxis2Placement3D", Location=P([0, 0, 0])))
    roof = f.create_entity(
        "IfcRoof", GlobalId=gid(), OwnerHistory=OWNER,
        Name="Cobertura-4Aguas (Hip)-Cumeeira Longa-Beiral Profundo-Telha Ceramica",
        ObjectPlacement=pl, Representation=prod, PredefinedType="HIP_ROOF")
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=[roof], RelatingStructure=st)
    mat = next(m for m in f.by_type("IfcMaterial") if m.Name == "Telha Cerâmica Vila Galé")
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=[roof], RelatingMaterial=mat)
    slope = math.degrees(math.atan((Z_R - Z_E) / (depth / 2)))
    print(f"Cobertura regenerada: cumeeira {Lr:.1f} m, inclinacao ~{slope:.1f} deg, "
          f"beiral X[{Xe0:.1f},{Xe1:.1f}] Y[{Ye0:.1f},{Ye1:.1f}]")


def bar(name, p0, p1, w, h, off, relto):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    d = d / L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    ref = np.cross(up, d); ref = ref / np.linalg.norm(ref)
    loc = (p0 - off).tolist()
    pl = f.create_entity("IfcLocalPlacement", PlacementRelTo=relto,
                         RelativePlacement=f.create_entity(
                             "IfcAxis2Placement3D", Location=P(loc),
                             Axis=D(d.tolist()), RefDirection=D(ref.tolist())))
    prof = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA",
                           Position=f.create_entity("IfcAxis2Placement2D",
                                                    Location=P([0, 0])),
                           XDim=float(w), YDim=float(h))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D",
                                                     Location=P([0, 0, 0])),
                            ExtrudedDirection=D([0, 0, 1]), Depth=L)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    return f.create_entity("IfcMember", GlobalId=gid(), OwnerHistory=OWNER,
                           Name=name, ObjectPlacement=pl, Representation=prod,
                           PredefinedType="MEMBER")


def build_truss(off, relto, st):
    # átrio escalado
    X0 = CX + (146 - CX) * KX; X1 = CX + (184 - CX) * KX
    Y0 = CY + (226 - CY) * KY; Y1 = CY + (264 - CY) * KY
    Z_TOP, DEPTH = 3.85, 1.20
    Z_BOT = Z_TOP - DEPTH
    mod = 6.33
    nx = max(2, round((X1 - X0) / mod)); ny = max(2, round((Y1 - Y0) / mod))
    xs = np.linspace(X0, X1, nx + 1); ys = np.linspace(Y0, Y1, ny + 1)
    xb = (xs[:-1] + xs[1:]) / 2; yb = (ys[:-1] + ys[1:]) / 2
    sc, sd = (0.12, 0.12), (0.09, 0.09)
    asm = f.create_entity("IfcElementAssembly", GlobalId=gid(), OwnerHistory=OWNER,
                          Name="BP-Recepcao-Trelica-Espacial",
                          ObjectPlacement=f.create_entity(
                              "IfcLocalPlacement", RelativePlacement=f.create_entity(
                                  "IfcAxis2Placement3D", Location=P([0, 0, 0]))),
                          PredefinedType="TRUSS")
    M = []
    top = lambda ix, iy: (xs[ix], ys[iy], Z_TOP)
    bot = lambda ix, iy: (xb[ix], yb[iy], Z_BOT)
    for iy in range(len(ys)):
        for ix in range(len(xs) - 1):
            M.append(bar("Banzo-Sup-X", top(ix, iy), top(ix + 1, iy), *sc, off, relto))
    for ix in range(len(xs)):
        for iy in range(len(ys) - 1):
            M.append(bar("Banzo-Sup-Y", top(ix, iy), top(ix, iy + 1), *sc, off, relto))
    for iy in range(len(yb)):
        for ix in range(len(xb) - 1):
            M.append(bar("Banzo-Inf-X", bot(ix, iy), bot(ix + 1, iy), *sc, off, relto))
    for ix in range(len(xb)):
        for iy in range(len(yb) - 1):
            M.append(bar("Banzo-Inf-Y", bot(ix, iy), bot(ix, iy + 1), *sc, off, relto))
    for ix in range(len(xb)):
        for iy in range(len(yb)):
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                M.append(bar("Diagonal", bot(ix, iy), top(ix + dx, iy + dy), *sd, off, relto))
    M = [m for m in M if m]
    f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatingObject=asm, RelatedObjects=M)
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=[asm], RelatingStructure=st)
    mat = next(m for m in f.by_type("IfcMaterial")
               if "Treliça Aparente" in (m.Name or ""))
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=M, RelatingMaterial=mat)
    print(f"Trelica reconstruida: {len(M)} barras, atrio X[{X0:.1f},{X1:.1f}] "
          f"Y[{Y0:.1f},{Y1:.1f}] ({nx}x{ny} modulos)")


if __name__ == "__main__":
    main()
