#!/usr/bin/env python3
"""
HVG Inhotim — construtor da revisão v106 (estruturas de cobertura aparentes).

Resolve as duas divergências de alta severidade levantadas na auditoria
foto x modelo (HVG_Inhotim_Comparacao_Foto_x_Modelo_v105.md):

  4.1  SPA  — troca a laje plana por cobertura inclinada de 2 águas + tesouras
              de madeira lamelada colada aparentes (telha cerâmica).
  4.2  Recepção (Bloco Principal) — modela a treliça espacial metálica (space
              frame de dupla camada) aparente sobre o Átrio-Lobby Central.

Entrada : HVG_MASTER_v105_REALISTA.ifc
Saída   : HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc

Reprodutível com IfcOpenShell 0.8.x. Toda a geometria é criada como
IfcExtrudedAreaSolid (barras de seção retangular) e IfcRoof prismático,
com placement relativo ao pavimento de cada edifício e associação de material.
"""
import math
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api

SRC = "HVG_MASTER_v105_REALISTA.ifc"
OUT = "HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0] if f.by_type("IfcOwnerHistory") else None
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")


# ---------------------------------------------------------------- utilidades
def gid():
    return ifcopenshell.guid.new()


def D(v):
    return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


def P(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def storey_offset(storey):
    """Translação acumulada (mundo) do placement do pavimento."""
    off = np.zeros(3)
    p = storey.ObjectPlacement
    while p is not None:
        rp = p.RelativePlacement
        if rp and rp.Location:
            off = off + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return off


def get_storey(name):
    return next(s for s in f.by_type("IfcBuildingStorey") if s.Name == name)


def get_building(name):
    return next(b for b in f.by_type("IfcBuilding") if b.Name == name)


MATERIALS = {}


def material(name):
    if name in MATERIALS:
        return MATERIALS[name]
    m = next((x for x in f.by_type("IfcMaterial") if x.Name == name), None)
    if m is None:
        m = f.create_entity("IfcMaterial", Name=name)
    MATERIALS[name] = m
    return m


def associate_material(elements, mat_name):
    mat = material(mat_name)
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=list(elements), RelatingMaterial=mat)


def contain(elements, storey):
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=list(elements),
                    RelatingStructure=storey)


def aggregate(assembly, parts):
    f.create_entity("IfcRelAggregates", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatingObject=assembly, RelatedObjects=list(parts))


def axis_placement(location, axis=None, ref=None, rel_to=None):
    a2p = f.create_entity(
        "IfcAxis2Placement3D", Location=P(location),
        Axis=D(axis) if axis is not None else None,
        RefDirection=D(ref) if ref is not None else None)
    return f.create_entity("IfcLocalPlacement", PlacementRelTo=rel_to,
                           RelativePlacement=a2p)


def bar(name, p0, p1, w, h, storey_off, rel_to, ptype="MEMBER", cls="IfcMember"):
    """Barra reta de p0 a p1 (coords mundo), seção w x h.
       Placement relativo ao pavimento (rel_to), origem local = p0-offset."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    d = d / L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    ref = np.cross(up, d)
    ref = ref / np.linalg.norm(ref)
    loc = (p0 - storey_off).tolist()
    placement = axis_placement(loc, axis=d.tolist(), ref=ref.tolist(), rel_to=rel_to)
    profile = f.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA",
        Position=f.create_entity("IfcAxis2Placement2D", Location=f.create_entity(
            "IfcCartesianPoint", Coordinates=[0.0, 0.0])),
        XDim=float(w), YDim=float(h))
    solid = f.create_entity(
        "IfcExtrudedAreaSolid", SweptArea=profile,
        Position=f.create_entity("IfcAxis2Placement3D",
                                 Location=P([0.0, 0.0, 0.0])),
        ExtrudedDirection=D([0, 0, 1]), Depth=L)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    el = f.create_entity(cls, GlobalId=gid(), OwnerHistory=OWNER, Name=name,
                         ObjectPlacement=placement, Representation=prod,
                         PredefinedType=ptype)
    return el


def assembly(name, ptype="NOTDEFINED"):
    return f.create_entity("IfcElementAssembly", GlobalId=gid(),
                           OwnerHistory=OWNER, Name=name,
                           ObjectPlacement=axis_placement([0, 0, 0]),
                           PredefinedType=ptype)


def prism_roof(name, profile_pts_yz, x0, x1, storey_off, rel_to):
    """Cobertura prismática: polígono no plano Y-Z extrudado ao longo de X.
       profile_pts_yz: lista de (Y,Z) em coords mundo. Extrusão de x0 a x1."""
    # placement: eixo local X = mundo X; perfil definido no plano local X-Y
    # Estratégia: colocar o solido com Position cujo eixo Z = +X mundo.
    pts = [(y - storey_off[1], z - storey_off[2]) for (y, z) in profile_pts_yz]
    poly = f.create_entity("IfcPolyline", Points=[
        f.create_entity("IfcCartesianPoint", Coordinates=[float(a), float(b)])
        for (a, b) in pts] + [f.create_entity(
            "IfcCartesianPoint", Coordinates=[float(pts[0][0]), float(pts[0][1])])])
    profile = f.create_entity("IfcArbitraryClosedProfileDef",
                              ProfileType="AREA", OuterCurve=poly)
    # Solid local frame: Z = mundo +X, X = mundo +Y  -> Location at x0 (mundo)
    solid_pos = f.create_entity(
        "IfcAxis2Placement3D",
        Location=P([x0 - storey_off[0], 0.0, 0.0]),
        Axis=D([1, 0, 0]), RefDirection=D([0, 1, 0]))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=profile,
                            Position=solid_pos, ExtrudedDirection=D([0, 0, 1]),
                            Depth=float(x1 - x0))
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    roof = f.create_entity("IfcRoof", GlobalId=gid(), OwnerHistory=OWNER,
                           Name=name, ObjectPlacement=axis_placement(
                               [0, 0, 0], rel_to=rel_to),
                           Representation=prod, PredefinedType="GABLE_ROOF")
    return roof


# ======================================================== 4.1  SPA
def build_spa():
    st = get_storey("SPA-Terreo")
    bld = get_building("SPA")
    off = storey_offset(st)
    relto = st.ObjectPlacement
    # pegada (mundo) a partir dos pilares/laje do SPA
    X0, X1 = 67.5, 92.5            # direção da cumeeira (comprimento 25 m)
    Y0, Y1 = 263.5, 276.5         # vão das tesouras (~13 m)
    Z_EAVE = 3.0
    RISE = 2.0
    Ymid = (Y0 + Y1) / 2.0
    Z_RIDGE = Z_EAVE + RISE
    parts = []

    # remove a cobertura plana existente do SPA
    for r in list(f.by_type("IfcRoof")):
        try:
            cont = r.ContainedInStructure
            in_spa = any(rel.RelatingStructure == st for rel in cont)
        except Exception:
            in_spa = False
        if in_spa and "Plana" in (r.Name or ""):
            ifcopenshell.api.run("root.remove_product", f, product=r)

    # --- tesouras de madeira lamelada colada (glulam) ---
    n_truss = 7
    xs = np.linspace(X0 + 0.5, X1 - 0.5, n_truss)
    sec = (0.12, 0.30)             # 12 x 30 cm banzo
    all_members = []
    for i, x in enumerate(xs, 1):
        asm = assembly(f"SPA-Tesoura-Madeira-T{i:02d}", ptype="TRUSS")
        m = []
        # banzo inferior
        m.append(bar(f"T{i:02d}-BanzoInf", (x, Y0, Z_EAVE), (x, Y1, Z_EAVE),
                     *sec, off, relto))
        # banzos superiores (2 águas)
        m.append(bar(f"T{i:02d}-BanzoSupE", (x, Y0, Z_EAVE), (x, Ymid, Z_RIDGE),
                     *sec, off, relto))
        m.append(bar(f"T{i:02d}-BanzoSupD", (x, Ymid, Z_RIDGE), (x, Y1, Z_EAVE),
                     *sec, off, relto))
        # pendural central (king post)
        m.append(bar(f"T{i:02d}-Pendural", (x, Ymid, Z_EAVE), (x, Ymid, Z_RIDGE),
                     0.10, 0.20, off, relto))
        # diagonais (escoras)
        qy0 = (Y0 + Ymid) / 2.0; qy1 = (Ymid + Y1) / 2.0
        zq = Z_EAVE + RISE / 2.0
        m.append(bar(f"T{i:02d}-EscoraE", (x, Ymid, Z_EAVE), (x, qy0, zq),
                     0.10, 0.18, off, relto))
        m.append(bar(f"T{i:02d}-EscoraD", (x, Ymid, Z_EAVE), (x, qy1, zq),
                     0.10, 0.18, off, relto))
        m = [x for x in m if x]
        aggregate(asm, m)
        contain([asm], st)
        all_members += m
        parts.append(asm)
    associate_material(all_members, "Madeira Lamelada Colada (Glulam)")

    # --- terças longitudinais (apoio do telhado) ---
    tercas = []
    for (yt, zt) in [(Y0, Z_EAVE), (Ymid, Z_RIDGE), (Y1, Z_EAVE),
                     (qy0, zq), (qy1, zq)]:
        t = bar(f"SPA-Terca-Y{yt:.1f}", (X0, yt, zt), (X1, yt, zt),
                0.08, 0.16, off, relto)
        if t:
            tercas.append(t)
    contain(tercas, st)
    associate_material(tercas, "Madeira Lamelada Colada (Glulam)")

    # --- cobertura de 2 águas (telha cerâmica) ---
    th = 0.20  # espessura aparente do plano de telhado
    ov = 0.8   # beiral
    prof = [
        (Y0 - ov, Z_EAVE),           (Ymid, Z_RIDGE),
        (Y1 + ov, Z_EAVE),           (Y1 + ov, Z_EAVE - th),
        (Ymid, Z_RIDGE - th),        (Y0 - ov, Z_EAVE - th),
    ]
    roof = prism_roof("Cobertura-2Aguas-Telha Ceramica-Tesouras Madeira",
                      prof, X0 - ov, X1 + ov, off, relto)
    contain([roof], st)
    associate_material([roof], "Telha Cerâmica Vila Galé")
    return len(all_members) + len(tercas), 1, len(parts)


# ======================================================== 4.2  Recepção
def build_reception():
    st = get_storey("BP-Terreo")
    off = storey_offset(st)
    relto = st.ObjectPlacement
    # átrio (mundo)
    X0, X1 = 146.0, 184.0
    Y0, Y1 = 226.0, 264.0
    Z_TOP = 3.85      # camada superior (base da cobertura hip do BP)
    DEPTH = 1.20      # altura do banzo da treliça espacial
    Z_BOT = Z_TOP - DEPTH
    mod = 6.33        # módulo do grid

    nx = max(2, round((X1 - X0) / mod))
    ny = max(2, round((Y1 - Y0) / mod))
    xs = np.linspace(X0, X1, nx + 1)
    ys = np.linspace(Y0, Y1, ny + 1)
    # nós inferiores deslocados meio módulo (space frame piramidal)
    xb = (xs[:-1] + xs[1:]) / 2.0
    yb = (ys[:-1] + ys[1:]) / 2.0

    sec_chord = (0.12, 0.12)
    sec_diag = (0.09, 0.09)
    asm = assembly("BP-Recepcao-Trelica-Espacial", ptype="TRUSS")
    members = []

    def top(ix, iy):
        return (xs[ix], ys[iy], Z_TOP)

    def bot(ix, iy):
        return (xb[ix], yb[iy], Z_BOT)

    # banzos superiores (grelha em X e Y)
    for iy in range(len(ys)):
        for ix in range(len(xs) - 1):
            members.append(bar("Banzo-Sup-X", top(ix, iy), top(ix + 1, iy),
                               *sec_chord, off, relto))
    for ix in range(len(xs)):
        for iy in range(len(ys) - 1):
            members.append(bar("Banzo-Sup-Y", top(ix, iy), top(ix, iy + 1),
                               *sec_chord, off, relto))
    # banzos inferiores
    for iy in range(len(yb)):
        for ix in range(len(xb) - 1):
            members.append(bar("Banzo-Inf-X", bot(ix, iy), bot(ix + 1, iy),
                               *sec_chord, off, relto))
    for ix in range(len(xb)):
        for iy in range(len(yb) - 1):
            members.append(bar("Banzo-Inf-Y", bot(ix, iy), bot(ix, iy + 1),
                               *sec_chord, off, relto))
    # diagonais: cada nó inferior conecta aos 4 nós superiores do seu módulo
    for ix in range(len(xb)):
        for iy in range(len(yb)):
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                members.append(bar("Diagonal", bot(ix, iy),
                                   top(ix + dx, iy + dy),
                                   *sec_diag, off, relto))
    members = [m for m in members if m]
    aggregate(asm, members)
    contain([asm], st)
    associate_material(members, "Aço Estrutural ASTM A572 (Treliça Aparente)")
    return len(members), nx, ny


if __name__ == "__main__":
    sm, sr, st_ = build_spa()
    rm, rnx, rny = build_reception()
    f.write(OUT)
    print(f"SPA: {sm} barras de madeira + 1 cobertura 2 águas ({st_} tesouras)")
    print(f"Recepção: {rm} barras de aço (space frame {rnx}x{rny} módulos)")
    print(f"Escrito: {OUT}")
