#!/usr/bin/env python3
"""
HVG Inhotim — construtor da revisão v107 (cobertura do Bloco Principal).

Resolve a divergência 4.3 da auditoria foto x modelo: a cobertura do Bloco
Principal estava nomeada "Piramidal" e, sobretudo, **sem beiral** — ficava
5,85 m para dentro das fachadas (as paredes avançavam além do telhado).

Esta revisão substitui a cobertura por um **telhado de 4 águas (hip) de baixa
inclinação com BEIRAL PROFUNDO** (2,5 m de balanço além das fachadas) e
cumeeira horizontal, mais fiel às fotografias (p.5–7), e a renomeia.

Entrada : HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc
Saída   : HVG_MASTER_v107_COBERTURA_BP.ifc
"""
import numpy as np
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api
import ifcopenshell.util.element as ue

SRC = "HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc"
OUT = "HVG_MASTER_v107_COBERTURA_BP.ifc"

f = ifcopenshell.open(SRC)
OWNER = f.by_type("IfcOwnerHistory")[0]
CTX = next(c for c in f.by_type("IfcGeometricRepresentationContext")
           if c.ContextType == "Model")


def gid():
    return ifcopenshell.guid.new()


def storey_offset(storey):
    off = np.zeros(3)
    p = storey.ObjectPlacement
    while p is not None:
        rp = p.RelativePlacement
        if rp and rp.Location:
            off = off + np.array(rp.Location.Coordinates)
        p = p.PlacementRelTo
    return off


def building_of(e):
    c = ue.get_container(e)
    while c and not c.is_a("IfcBuilding"):
        c = c.Decomposes[0].RelatingObject if c.Decomposes else None
    return c.Name if c else "?"


def faceted_brep(verts_local, faces):
    """IfcFacetedBrep a partir de vértices (locais) e faces (índices)."""
    pts = [f.create_entity("IfcCartesianPoint",
                           Coordinates=[float(x) for x in v]) for v in verts_local]
    ifc_faces = []
    for idx in faces:
        loop = f.create_entity("IfcPolyLoop", Polygon=[pts[i] for i in idx])
        bound = f.create_entity("IfcFaceOuterBound", Bound=loop, Orientation=True)
        ifc_faces.append(f.create_entity("IfcFace", Bounds=[bound]))
    shell = f.create_entity("IfcClosedShell", CfsFaces=ifc_faces)
    return f.create_entity("IfcFacetedBrep", Outer=shell)


def build():
    st = next(s for s in f.by_type("IfcBuildingStorey") if s.Name == "BP-Terreo")
    off = storey_offset(st)

    # --- remove cobertura antiga do Bloco Principal ---
    old = [r for r in f.by_type("IfcRoof") if building_of(r) == "Bloco Principal"]
    for r in old:
        print("removendo:", r.Name)
        ifcopenshell.api.run("root.remove_product", f, product=r)

    # --- parâmetros do novo telhado (coords mundo) ---
    # fachadas do BP: X[125.1,204.8] Y[205.2,284.9], topo das paredes Z=3.55
    OV = 2.5                       # beiral (balanço) além das fachadas
    Xe0, Xe1 = 125.1 - OV, 204.8 + OV
    Ye0, Ye1 = 205.2 - OV, 284.9 + OV
    Z_E = 3.70                     # cota do beiral (logo acima das paredes)
    Z_R = 8.20                     # cota da cumeeira (rise 4,5 m -> ~6° baixa)
    Ym = (Ye0 + Ye1) / 2.0
    Xc = (Xe0 + Xe1) / 2.0
    Lr = 28.0                      # comprimento da cumeeira (espigão)
    Xr0, Xr1 = Xc - Lr / 2, Xc + Lr / 2

    # vértices mundo: A,B,C,D (beiral) + R0,R1 (cumeeira)
    W = [(Xe0, Ye0, Z_E), (Xe1, Ye0, Z_E), (Xe1, Ye1, Z_E), (Xe0, Ye1, Z_E),
         (Xr0, Ym, Z_R), (Xr1, Ym, Z_R)]
    A, B, C, D, R0, R1 = range(6)
    faces = [
        [A, B, C, D],          # base (beiral) plana
        [A, B, R1, R0],        # água frontal (Ye0)
        [C, D, R0, R1],        # água posterior (Ye1)
        [D, A, R0],            # tacaniça esquerda (Xe0)
        [B, C, R1],            # tacaniça direita (Xe1)
    ]
    verts_local = [(x - off[0], y - off[1], z - off[2]) for (x, y, z) in W]

    brep = faceted_brep(verts_local, faces)
    shape = f.create_entity("IfcShapeRepresentation", ContextOfItems=CTX,
                            RepresentationIdentifier="Body",
                            RepresentationType="Brep", Items=[brep])
    prod = f.create_entity("IfcProductDefinitionShape", Representations=[shape])
    placement = f.create_entity(
        "IfcLocalPlacement", PlacementRelTo=st.ObjectPlacement,
        RelativePlacement=f.create_entity(
            "IfcAxis2Placement3D",
            Location=f.create_entity("IfcCartesianPoint",
                                     Coordinates=[0.0, 0.0, 0.0])))
    roof = f.create_entity(
        "IfcRoof", GlobalId=gid(), OwnerHistory=OWNER,
        Name="Cobertura-4Aguas (Hip Baixa)-Beiral Profundo-Telha Ceramica Vila Gale",
        ObjectPlacement=placement, Representation=prod, PredefinedType="HIP_ROOF")
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=gid(),
                    OwnerHistory=OWNER, RelatedElements=[roof],
                    RelatingStructure=st)
    mat = next(m for m in f.by_type("IfcMaterial")
               if m.Name == "Telha Cerâmica Vila Galé")
    f.create_entity("IfcRelAssociatesMaterial", GlobalId=gid(), OwnerHistory=OWNER,
                    RelatedObjects=[roof], RelatingMaterial=mat)

    slope = np.degrees(np.arctan((Z_R - Z_E) / ((Ye1 - Ye0) / 2)))
    print(f"Nova cobertura: beiral {OV} m, cumeeira {Lr} m, inclinacao ~{slope:.1f} deg")
    print(f"  beiral X[{Xe0:.1f},{Xe1:.1f}] Y[{Ye0:.1f},{Ye1:.1f}] Z[{Z_E},{Z_R}]")
    return roof


if __name__ == "__main__":
    build()
    f.write(OUT)
    print("Escrito:", OUT)
