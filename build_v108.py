#!/usr/bin/env python3
"""
HVG Inhotim — construtor da revisão v108 (cenografia de lazer).

Resolve as divergências 4.5 e 4.6 (severidade baixa) da auditoria foto x modelo,
adicionando a cenografia das áreas infantis vista nas fotografias:

  4.5  Piscina das Crianças / Parque aquático (p.12) — brinquedos aquáticos
       (cogumelos-chafariz, balde basculante, escorregas, palmeira lúdica,
       esculturas) e guarda-sóis.
  4.6  Clube da Criança / Pista de carros (p.13) — sinalização vertical (placas)
       e pintura viária (faixas/circuito) sobre a pista já existente.

Entrada : HVG_MASTER_v107_COBERTURA_BP.ifc
Saída   : HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc
"""
import math
import numpy as np
import ifcopenshell
import ifcopenshell.guid

SRC = "HVG_MASTER_v107_COBERTURA_BP.ifc"
OUT = "HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")
SITE = f.by_type("IfcSite")[0]                 # offset (0,0,0) -> mundo == local
RELTO = SITE.ObjectPlacement


def gid():
    return ifcopenshell.guid.new()


def P(v):
    return f.create_entity("IfcCartesianPoint", Coordinates=[float(x) for x in v])


def D(v):
    return f.create_entity("IfcDirection", DirectionRatios=[float(x) for x in v])


MAT = {}


def material(name):
    if name not in MAT:
        m = next((x for x in f.by_type("IfcMaterial") if x.Name == name), None)
        MAT[name] = m or f.create_entity("IfcMaterial", Name=name)
    return MAT[name]


def placement(loc, axis=None, ref=None):
    a2p = f.create_entity("IfcAxis2Placement3D", Location=P(loc),
                          Axis=D(axis) if axis else None,
                          RefDirection=D(ref) if ref else None)
    return f.create_entity("IfcLocalPlacement", PlacementRelTo=RELTO,
                           RelativePlacement=a2p)


def _product(cls, name, loc, solid, ptype, axis=None, ref=None):
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="SweptSolid", Items=[solid])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    kw = dict(GlobalId=gid(), OwnerHistory=OWNER, Name=name,
              ObjectPlacement=placement(loc, axis, ref), Representation=prod)
    if ptype is not None:
        kw["PredefinedType"] = ptype
    return f.create_entity(cls, **kw)


def vcyl(name, base, h, r, cls="IfcFurniture", ptype=None):
    """Cilindro vertical (poste/tronco/chafariz)."""
    prof = f.create_entity("IfcCircleProfileDef", ProfileType="AREA",
                           Position=f.create_entity(
                               "IfcAxis2Placement2D", Location=P([0, 0])),
                           Radius=float(r))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D",
                                                     Location=P([0, 0, 0])),
                            ExtrudedDirection=D([0, 0, 1]), Depth=float(h))
    return _product(cls, name, base, solid, ptype)


def disc(name, center, r, t, cls="IfcFurniture", ptype=None):
    return vcyl(name, [center[0], center[1], center[2] - t / 2], t, r, cls, ptype)


def box(name, center, dx, dy, dz, cls="IfcFurniture", ptype=None):
    prof = f.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA",
        Position=f.create_entity("IfcAxis2Placement2D", Location=P([0, 0])),
        XDim=float(dx), YDim=float(dy))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D",
                                                     Location=P([0, 0, 0])),
                            ExtrudedDirection=D([0, 0, 1]), Depth=float(dz))
    return _product(cls, name, [center[0], center[1], center[2] - dz / 2],
                    solid, ptype)


def obox(name, p0, p1, w, h, cls="IfcFurniture", ptype=None):
    """Barra/caixa de p0 a p1 (seção w x h) — escorregas e faixas inclinadas."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    d = d / L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    ref = np.cross(up, d); ref = ref / np.linalg.norm(ref)
    prof = f.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA",
        Position=f.create_entity("IfcAxis2Placement2D", Location=P([0, 0])),
        XDim=float(w), YDim=float(h))
    solid = f.create_entity("IfcExtrudedAreaSolid", SweptArea=prof,
                            Position=f.create_entity("IfcAxis2Placement3D",
                                                     Location=P([0, 0, 0])),
                            ExtrudedDirection=D([0, 0, 1]), Depth=L)
    return _product(cls, name, p0.tolist(), solid, ptype,
                    axis=d.tolist(), ref=ref.tolist())


def contain(elems, name_rel):
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=list(elems),
                    RelatingStructure=SITE)


def assoc(elems, mat_name):
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=list(elems), RelatingMaterial=material(mat_name))


# ============================================ 4.5 Parque aquático
def build_waterpark():
    # piscina infantil: X[77.5,92.5] Y[255,265], lâmina d'água Z~2.30, deck Z~1.84
    Zw = 2.30
    el_color, el_palm, el_sun, el_struct = [], [], [], []

    # 3 cogumelos-chafariz (poste + disco)
    for i, (x, y) in enumerate([(81, 258), (88, 261), (84, 263)], 1):
        post = vcyl(f"Brinquedo-Cogumelo-Chafariz-{i}-Haste", [x, y, Zw], 2.2, 0.09)
        cap = disc(f"Brinquedo-Cogumelo-Chafariz-{i}-Chapeu", [x, y, Zw + 2.3], 0.9, 0.18)
        el_color += [post, cap]
    # balde basculante
    bp = vcyl("Brinquedo-Balde-Basculante-Haste", [90, 257, Zw], 3.2, 0.10)
    bk = box("Brinquedo-Balde-Basculante-Balde", [90, 257, Zw + 3.3], 1.0, 1.0, 0.9)
    el_color += [bp, bk]
    # 2 escorregas (rampa inclinada de plataforma a água)
    el_color.append(obox("Brinquedo-Escorrega-1", [79, 256, Zw + 2.6], [80.5, 256, Zw + 0.1],
                         0.9, 0.12))
    el_color.append(obox("Brinquedo-Escorrega-2", [86, 264, Zw + 2.2], [87.5, 264, Zw + 0.1],
                         0.8, 0.12))
    # palmeira lúdica (tronco + folhas radiais)
    tr = vcyl("Brinquedo-Palmeira-Tronco", [83.5, 260, Zw], 2.6, 0.12)
    el_struct.append(tr)
    for a in range(6):
        ang = math.radians(a * 60)
        c = [83.5, 260, Zw + 2.6]
        tip = [c[0] + 1.4 * math.cos(ang), c[1] + 1.4 * math.sin(ang), c[2] - 0.3]
        el_palm.append(obox(f"Brinquedo-Palmeira-Folha-{a+1}", c, tip, 0.5, 0.06))
    # 2 esculturas lúdicas (pato / sapo) — massas simples
    el_color.append(box("Brinquedo-Escultura-Pato", [78.5, 263, Zw + 0.4], 1.0, 0.7, 0.9))
    el_color.append(box("Brinquedo-Escultura-Sapo", [91, 263, Zw + 0.3], 0.9, 0.9, 0.7))
    # 6 guarda-sóis no deck (poste + lona)
    for i, (x, y) in enumerate([(75, 254), (75, 266), (95, 254), (95, 266),
                                (85, 252.5), (85, 267.5)], 1):
        post = vcyl(f"Guarda-Sol-Infantil-{i}-Mastro", [x, y, 1.84], 2.4, 0.05)
        canopy = disc(f"Guarda-Sol-Infantil-{i}-Lona", [x, y, 1.84 + 2.5], 1.6, 0.10)
        el_struct.append(post); el_sun.append(canopy)

    el_color = [e for e in el_color if e]
    el_palm = [e for e in el_palm if e]
    contain(el_color + el_palm + el_sun + el_struct, "site")
    assoc(el_color, "Plástico Lúdico Colorido")
    assoc(el_palm, "Plástico Lúdico Verde")
    assoc(el_sun, "Lona Guarda-Sol Laranja")
    assoc(el_struct, "Aço Galvanizado Estrutura Lúdica")
    return len(el_color + el_palm + el_sun + el_struct)


# ============================================ 4.6 Pista de carros — sinalização + pintura
def build_track():
    # pista: X[371,409] Y[221,239], superfície Z~-0.08
    X0, X1, Y0, Y1 = 372.0, 408.0, 222.0, 238.0
    Zs = -0.06
    marks, signs_plate, signs_post = [], [], []
    wlin = 0.15  # largura de faixa
    t = 0.02

    # circuito externo (4 faixas de contorno)
    marks.append(box("Faixa-Pista-Contorno-S", [(X0 + X1) / 2, Y0, Zs], X1 - X0, wlin, t))
    marks.append(box("Faixa-Pista-Contorno-N", [(X0 + X1) / 2, Y1, Zs], X1 - X0, wlin, t))
    marks.append(box("Faixa-Pista-Contorno-O", [X0, (Y0 + Y1) / 2, Zs], wlin, Y1 - Y0, t))
    marks.append(box("Faixa-Pista-Contorno-L", [X1, (Y0 + Y1) / 2, Zs], wlin, Y1 - Y0, t))
    # divisória central tracejada (eixo da pista)
    xc0, xc1, ym = X0 + 3, X1 - 3, (Y0 + Y1) / 2
    n = 14
    for i in range(n):
        x = xc0 + (xc1 - xc0) * (i + 0.5) / n
        if i % 2 == 0:
            marks.append(box(f"Faixa-Eixo-Tracejado-{i+1}",
                            [x, ym, Zs], (xc1 - xc0) / n * 0.6, wlin, t))
    # 2 faixas de pedestres (zebrado)
    for j, xz in enumerate([X0 + 9, X1 - 9], 1):
        for k in range(5):
            marks.append(box(f"Faixa-Pedestre-{j}-{k+1}",
                            [xz, ym - 2 + k, Zs], 1.2, 0.25, t))
    # rotunda central (anel)
    for a in range(16):
        ang = math.radians(a * 22.5)
        x = (X0 + X1) / 2 + 3.0 * math.cos(ang)
        y = ym + 3.0 * math.sin(ang)
        marks.append(box(f"Faixa-Rotatoria-{a+1}", [x, y, Zs], 0.9, wlin, t))

    # 14 placas de sinalização (poste + placa)
    sign_pos = [(376, 224), (382, 224), (388, 224), (394, 224), (400, 224),
                (376, 236), (388, 236), (400, 236), (404, 230), (380, 230),
                (392, 227), (392, 233), (385, 230), (398, 230)]
    for i, (x, y) in enumerate(sign_pos, 1):
        post = vcyl(f"Placa-Sinalizacao-Pista-{i}-Poste", [x, y, Zs], 1.1, 0.035)
        plate = box(f"Placa-Sinalizacao-Pista-{i}-Placa", [x, y, Zs + 1.2], 0.4, 0.06, 0.4)
        signs_post.append(post); signs_plate.append(plate)

    marks = [m for m in marks if m]
    contain(marks + signs_post + signs_plate, "site")
    assoc(marks, "Tinta Viária Branca")
    assoc(signs_post, "Aço Galvanizado Poste")
    assoc(signs_plate, "Alumínio Placa Sinalização")
    return len(marks), len(signs_plate)


if __name__ == "__main__":
    nw = build_waterpark()
    nm, ns = build_track()
    f.write(OUT)
    print(f"Parque aquático: {nw} elementos lúdicos/guarda-sóis")
    print(f"Pista de carros: {nm} faixas de pintura + {ns} placas")
    print("Escrito:", OUT)
