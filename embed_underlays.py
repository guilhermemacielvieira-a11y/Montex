"""
Embute os underlays DXF (pacote PROT-002) no IFC v95, georreferenciados.
Fonte de verdade: import_manifest.csv (arquivo -> edificio -> piso).
Cada underlay vira IfcAnnotation 2D numa camada MTX-Underlay travada,
contida no pavimento correto, posicionada na origem local do pavimento
(coincidente com a origem compartilhada EPSG:31983 E578800/N7773500/H935).

Saida: HVG_MASTER_v96_underlays.ifc
"""
import ifcopenshell, ezdxf, uuid, time
import numpy as np
from collections import defaultdict

PKG   = "/tmp/ac_pkg"
SRC   = "/home/user/Montex/HVG_MASTER_v95_corrigido.ifc"
DEST  = "/home/user/Montex/HVG_MASTER_v96_underlays.ifc"
QUANT = 0.001  # 1 mm para dedup/encadeamento

# (dxf, rotulo, storey_id, layer, escala, obs)
UNDERLAYS = [
    ("02.dxf", "Guarita",                127, "MTX-Underlay-Guarita",   "1:50",  "planta + cortes"),
    ("05.dxf", "Centro de Convencoes",    56,  "MTX-Underlay-CC",        "1:100", "planta limpa (grid/sanitarios/PCD)"),
    ("06.dxf", "Restaurante da Piscina",  82,  "MTX-Underlay-RP",        "1:100", "planta limpa"),
    ("09.dxf", "Clube NEP",               114, "MTX-Underlay-NEP",       "1:100", "planta limpa"),
    ("13.dxf", "SPA",                     101, "MTX-Underlay-SPA",       "1:100", "plantas + cortes"),
    ("04.dxf", "Boite",                   69,  "MTX-Underlay-Boite",     "1:100", "plantas + cortes"),
    ("BlocoPrincipal_R1_Proje_o_da_Cobertura.dxf", "Bloco Principal", 43, "MTX-Underlay-BP",
        "1:100", "2 plantas giradas ~45 (terreo+subsolo) - separar/rotacionar no Archicad"),
    ("BlocoB_R1_Planta_1.dxf", "Bloco B - Terreo/Subsolo", 446,
        "MTX-Underlay-BlocoB-T", "1:100", "regiao principal 64x37"),
    ("BlocoB_R2_UPLANTA_1_PAVIMENTO.dxf", "Bloco B - 1 Pavimento", 452, "MTX-Underlay-BlocoB-P1",
        "1:100", "planta 1 pavimento 61x66"),
]

t0 = time.time()
m = ifcopenshell.open(SRC)
owner = m.by_type("IfcOwnerHistory")[0] if m.by_type("IfcOwnerHistory") else None

# contexto de modelo
ctx_model = None
for c in m.by_type("IfcGeometricRepresentationContext"):
    if c.is_a("IfcGeometricRepresentationContext") and not c.is_a("IfcGeometricRepresentationSubContext"):
        if c.ContextType == "Model":
            ctx_model = c
if ctx_model is None:
    ctx_model = m.by_type("IfcGeometricRepresentationContext")[0]

# subcontexto de anotacao (PLAN_VIEW)
ctx_annot = m.create_entity(
    "IfcGeometricRepresentationSubContext",
    ContextIdentifier="Annotation", ContextType="Plan",
    ParentContext=ctx_model, TargetView="PLAN_VIEW")

def guid():
    return ifcopenshell.guid.compress(uuid.uuid4().hex)

def read_lines(path):
    doc = ezdxf.readfile(path)
    segs = []
    for e in doc.modelspace():
        if e.dxftype() == "LINE":
            s = e.dxf.start; t = e.dxf.end
            segs.append((s.x, s.y, t.x, t.y))
    return np.array(segs, dtype=float)

def filter_outliers(segs):
    xs = np.concatenate([segs[:,0], segs[:,2]])
    ys = np.concatenate([segs[:,1], segs[:,3]])
    xlo, xhi = np.percentile(xs, 0.5), np.percentile(xs, 99.5)
    ylo, yhi = np.percentile(ys, 0.5), np.percentile(ys, 99.5)
    mx = (xhi - xlo) * 0.05 + 1.0
    my = (yhi - ylo) * 0.05 + 1.0
    xlo -= mx; xhi += mx; ylo -= my; yhi += my
    ok = ((segs[:,0] >= xlo) & (segs[:,0] <= xhi) & (segs[:,1] >= ylo) & (segs[:,1] <= yhi) &
          (segs[:,2] >= xlo) & (segs[:,2] <= xhi) & (segs[:,3] >= ylo) & (segs[:,3] <= yhi))
    return segs[ok]

def chain_segments(segs):
    """Dedup pontos (1mm), encadeia segmentos em polilinhas. Retorna (coords, paths)."""
    def key(x, y): return (round(x / QUANT), round(y / QUANT))
    pt_index = {}
    coords = []
    def idx(x, y):
        k = key(x, y)
        if k not in pt_index:
            pt_index[k] = len(coords)
            coords.append((float(x), float(y)))
        return pt_index[k]
    edges = []
    adj = defaultdict(list)
    for (x1, y1, x2, y2) in segs:
        a = idx(x1, y1); b = idx(x2, y2)
        if a == b:
            continue
        eid = len(edges); edges.append((a, b))
        adj[a].append((b, eid)); adj[b].append((a, eid))
    used = [False] * len(edges)
    paths = []
    for eid0 in range(len(edges)):
        if used[eid0]:
            continue
        a, b = edges[eid0]; used[eid0] = True
        path = [a, b]
        # estende para frente (a partir de b)
        cur = b
        while True:
            nxt = None
            for (nb, eid) in adj[cur]:
                if not used[eid]:
                    nxt = (nb, eid); break
            if nxt is None:
                break
            used[nxt[1]] = True; path.append(nxt[0]); cur = nxt[0]
        # estende para tras (a partir de a)
        cur = a
        while True:
            nxt = None
            for (nb, eid) in adj[cur]:
                if not used[eid]:
                    nxt = (nb, eid); break
            if nxt is None:
                break
            used[nxt[1]] = True; path.insert(0, nxt[0]); cur = nxt[0]
        paths.append(path)
    return coords, paths

# rel de contencao por storey (reuso)
storey_rel = {}
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    st = rel.RelatingStructure
    if st.is_a("IfcBuildingStorey"):
        storey_rel.setdefault(st.id(), rel)

summary = []
for item in UNDERLAYS:
    dxf, label, st_id, layer, escala, obs = item
    path = f"{PKG}/{dxf}"
    storey = m.by_id(st_id)
    segs = read_lines(path)
    n_raw = len(segs)
    segs = filter_outliers(segs)
    n_kept = len(segs)
    # translada canto-min -> origem do pavimento
    minx = min(segs[:,0].min(), segs[:,2].min())
    miny = min(segs[:,1].min(), segs[:,3].min())
    segs[:,0] -= minx; segs[:,2] -= minx
    segs[:,1] -= miny; segs[:,3] -= miny
    coords, paths = chain_segments(segs)

    # geometria compacta
    coord_list = m.create_entity("IfcCartesianPointList3D",
                                 CoordList=[(x, y, 0.0) for (x, y) in coords])
    curves = []
    for p in paths:
        idx1 = [i + 1 for i in p]  # 1-based
        seg = m.create_entity("IfcLineIndex", idx1)
        curves.append(m.create_entity("IfcIndexedPolyCurve",
                                      Points=coord_list, Segments=[seg], SelfIntersect=False))
    rep = m.create_entity("IfcShapeRepresentation",
                          ContextOfItems=ctx_annot, RepresentationIdentifier="Annotation",
                          RepresentationType="GeometricCurveSet", Items=curves)
    shape = m.create_entity("IfcProductDefinitionShape", Representations=[rep])

    placement = m.create_entity("IfcLocalPlacement",
        PlacementRelTo=storey.ObjectPlacement,
        RelativePlacement=m.create_entity("IfcAxis2Placement3D",
            Location=m.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))))

    ann = m.create_entity("IfcAnnotation",
        GlobalId=guid(), OwnerHistory=owner,
        Name=f"Underlay DXF - {label}", ObjectType="MTX-UNDERLAY-DXF",
        ObjectPlacement=placement, Representation=shape)

    # contencao no pavimento
    rel = storey_rel.get(st_id)
    if rel:
        rel.RelatedElements = list(rel.RelatedElements) + [ann]
    else:
        rel = m.create_entity("IfcRelContainedInSpatialStructure",
            GlobalId=guid(), OwnerHistory=owner,
            RelatedElements=[ann], RelatingStructure=storey)
        storey_rel[st_id] = rel

    # camada travada
    m.create_entity("IfcPresentationLayerWithStyle",
        Name=layer, AssignedItems=[rep],
        LayerOn=True, LayerFrozen=True, LayerBlocked=True, LayerStyles=[])

    # PSet de rastreabilidade
    props = [
        m.create_entity("IfcPropertySingleValue", Name="SourceDXF",
                        NominalValue=m.create_entity("IfcLabel", dxf)),
        m.create_entity("IfcPropertySingleValue", Name="Manifest",
                        NominalValue=m.create_entity("IfcLabel", "MTX-BIM-HVG-PROT-002")),
        m.create_entity("IfcPropertySingleValue", Name="Escala",
                        NominalValue=m.create_entity("IfcLabel", escala)),
        m.create_entity("IfcPropertySingleValue", Name="CRS",
                        NominalValue=m.create_entity("IfcLabel", "EPSG:31983 E578800/N7773500/H935")),
        m.create_entity("IfcPropertySingleValue", Name="Observacao",
                        NominalValue=m.create_entity("IfcLabel", obs)),
    ]
    pset = m.create_entity("IfcPropertySet", GlobalId=guid(), OwnerHistory=owner,
                           Name="MTX_Underlay", HasProperties=props)
    m.create_entity("IfcRelDefinesByProperties", GlobalId=guid(), OwnerHistory=owner,
                    RelatedObjects=[ann], RelatingPropertyDefinition=pset)

    summary.append((label, dxf, storey.Name, n_raw, n_kept, len(coords), len(paths)))
    print(f"  {label:28s} {dxf:42s} -> {storey.Name:12s} lines {n_raw:>7d}->{n_kept:<7d} pts {len(coords):>7d} chains {len(paths):>7d}")

print(f"\nSalvando {DEST} ...")
m.write(DEST)
print(f"OK em {time.time()-t0:.1f}s")
print("\nResumo:")
for s in summary:
    print("  ", s)
