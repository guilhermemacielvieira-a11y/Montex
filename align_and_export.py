"""
(a) Alinha cada underlay ao CENTRO do footprint real do edificio (via iterador geom)
    e re-embute no IFC -> HVG_MASTER_v97_underlays_align.ifc
(b) Exporta os DXFs ja transladados para o sistema do v95 (coords locais do modelo),
    preservando camadas -> /tmp/georef/*.dxf -> HVG_underlays_georef_v97.zip

Translacao apenas (1:1 metros), centro-a-centro: mediana robusta do underlay -> centro do footprint.
"""
import ifcopenshell, ifcopenshell.geom as geom, ezdxf, uuid, time, os, zipfile, csv
import numpy as np
from collections import defaultdict

SRC   = "/home/user/Montex/HVG_MASTER_v95_corrigido.ifc"
DEST  = "/home/user/Montex/HVG_MASTER_v97_underlays_align.ifc"
PKG   = "/tmp/ac_pkg"
OUTD  = "/tmp/georef"
ZIPF  = "/home/user/Montex/HVG_underlays_georef_v97.zip"
CSVF  = "/home/user/Montex/HVG_underlays_transform_v97.csv"
QUANT = 0.001

# (dxf, rotulo, storey_id, layer, escala, obs, nome_saida)
UNDERLAYS = [
    ("02.dxf", "Guarita",               127, "MTX-Underlay-Guarita",  "1:50",  "planta + cortes", "HVG_Guarita_underlay_georef.dxf"),
    ("05.dxf", "Centro de Convencoes",   56,  "MTX-Underlay-CC",       "1:100", "planta limpa", "HVG_CentroConvencoes_underlay_georef.dxf"),
    ("06.dxf", "Restaurante da Piscina", 82,  "MTX-Underlay-RP",       "1:100", "planta limpa", "HVG_RestaurantePiscina_underlay_georef.dxf"),
    ("09.dxf", "Clube NEP",              114, "MTX-Underlay-NEP",      "1:100", "planta limpa", "HVG_ClubeNEP_underlay_georef.dxf"),
    ("13.dxf", "SPA",                    101, "MTX-Underlay-SPA",      "1:100", "plantas + cortes", "HVG_SPA_underlay_georef.dxf"),
    ("04.dxf", "Boite",                  69,  "MTX-Underlay-Boite",    "1:100", "plantas + cortes", "HVG_Boite_underlay_georef.dxf"),
    ("BlocoPrincipal_R1_Proje_o_da_Cobertura.dxf", "Bloco Principal", 43, "MTX-Underlay-BP", "1:100",
        "2 plantas giradas ~45 - separar/rotacionar no AC", "HVG_BlocoPrincipal_underlay_georef.dxf"),
    ("BlocoB_R1_Planta_1.dxf", "Bloco B - Terreo/Subsolo", 446, "MTX-Underlay-BlocoB-T", "1:100",
        "regiao principal 64x37", "HVG_BlocoB_Terreo_underlay_georef.dxf"),
    ("BlocoB_R2_UPLANTA_1_PAVIMENTO.dxf", "Bloco B - 1 Pavimento", 452, "MTX-Underlay-BlocoB-P1", "1:100",
        "planta 1 pavimento", "HVG_BlocoB_Pav1_underlay_georef.dxf"),
]

t0 = time.time()
m = ifcopenshell.open(SRC)
owner = m.by_type("IfcOwnerHistory")[0] if m.by_type("IfcOwnerHistory") else None

def world_xy(el):
    x = y = 0.0; p = el.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.is_a("IfcAxis2Placement3D"):
            c = rp.Location.Coordinates; x += c[0]; y += c[1]
        p = p.PlacementRelTo
    return x, y

# ---- footprint real de cada pavimento (bbox via iterador geom) ----
TARGET = {sid: (m.by_id(sid)) for (_, _, sid, *_ ) in UNDERLAYS}
st_world = {sid: world_xy(st) for sid, st in TARGET.items()}
el_storey = {}; include = []
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    sid = rel.RelatingStructure.id()
    if sid in TARGET:
        for el in rel.RelatedElements:
            if el.is_a("IfcAnnotation"):
                continue
            if el.Representation:
                el_storey[el.id()] = sid; include.append(el)
s = geom.settings(); s.set(s.USE_WORLD_COORDS, True)
it = geom.iterator(s, m, 4, include=include)
bb = defaultdict(lambda: [1e18, 1e18, -1e18, -1e18])
if it.initialize():
    while True:
        sh = it.get(); sid = el_storey.get(sh.id)
        if sid is not None:
            v = np.array(sh.geometry.verts).reshape(-1, 3)
            if len(v):
                b = bb[sid]
                b[0] = min(b[0], v[:, 0].min()); b[1] = min(b[1], v[:, 1].min())
                b[2] = max(b[2], v[:, 0].max()); b[3] = max(b[3], v[:, 1].max())
        if not it.next():
            break
# centro do footprint em coords LOCAIS do pavimento
fp_center_local = {}
for sid in TARGET:
    b = bb[sid]; sx, sy = st_world[sid]
    fp_center_local[sid] = ((b[0] + b[2]) / 2 - sx, (b[1] + b[3]) / 2 - sy)
print("footprints (centro local):", {m.by_id(k).Name: tuple(round(x,2) for x in v) for k,v in fp_center_local.items()})

# ---- contexto de anotacao ----
ctx_model = None
for c in m.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType == "Model":
        ctx_model = c
ctx_model = ctx_model or m.by_type("IfcGeometricRepresentationContext")[0]
ctx_annot = m.create_entity("IfcGeometricRepresentationSubContext",
    ContextIdentifier="Annotation", ContextType="Plan",
    ParentContext=ctx_model, TargetView="PLAN_VIEW")

def guid():
    return ifcopenshell.guid.compress(uuid.uuid4().hex)

def read_lines_layers(path):
    doc = ezdxf.readfile(path)
    segs = []; layers = []
    for e in doc.modelspace():
        if e.dxftype() == "LINE":
            s = e.dxf.start; t = e.dxf.end
            segs.append((s.x, s.y, t.x, t.y)); layers.append(e.dxf.layer)
    return doc, np.array(segs, float), layers

def outlier_mask(segs):
    xs = np.concatenate([segs[:,0], segs[:,2]]); ys = np.concatenate([segs[:,1], segs[:,3]])
    xlo, xhi = np.percentile(xs, .5), np.percentile(xs, 99.5)
    ylo, yhi = np.percentile(ys, .5), np.percentile(ys, 99.5)
    mx = (xhi-xlo)*0.05+1; my = (yhi-ylo)*0.05+1
    xlo-=mx; xhi+=mx; ylo-=my; yhi+=my
    return ((segs[:,0]>=xlo)&(segs[:,0]<=xhi)&(segs[:,1]>=ylo)&(segs[:,1]<=yhi)&
            (segs[:,2]>=xlo)&(segs[:,2]<=xhi)&(segs[:,3]>=ylo)&(segs[:,3]<=yhi))

def chain_segments(segs):
    def key(x,y): return (round(x/QUANT), round(y/QUANT))
    pidx = {}; coords = []
    def idx(x,y):
        k = key(x,y)
        if k not in pidx: pidx[k] = len(coords); coords.append((float(x),float(y)))
        return pidx[k]
    edges = []; adj = defaultdict(list)
    for (x1,y1,x2,y2) in segs:
        a = idx(x1,y1); b = idx(x2,y2)
        if a == b: continue
        eid = len(edges); edges.append((a,b)); adj[a].append((b,eid)); adj[b].append((a,eid))
    used = [False]*len(edges); paths = []
    for e0 in range(len(edges)):
        if used[e0]: continue
        a,b = edges[e0]; used[e0]=True; path=[a,b]; cur=b
        while True:
            nx=None
            for (nb,eid) in adj[cur]:
                if not used[eid]: nx=(nb,eid); break
            if nx is None: break
            used[nx[1]]=True; path.append(nx[0]); cur=nx[0]
        cur=a
        while True:
            nx=None
            for (nb,eid) in adj[cur]:
                if not used[eid]: nx=(nb,eid); break
            if nx is None: break
            used[nx[1]]=True; path.insert(0,nx[0]); cur=nx[0]
        paths.append(path)
    return coords, paths

storey_rel = {}
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    if rel.RelatingStructure.is_a("IfcBuildingStorey"):
        storey_rel.setdefault(rel.RelatingStructure.id(), rel)

os.makedirs(OUTD, exist_ok=True)
rows = []
for dxf, label, sid, layer, escala, obs, outname in UNDERLAYS:
    storey = m.by_id(sid)
    doc, segs, layers = read_lines_layers(f"{PKG}/{dxf}")
    mask = outlier_mask(segs)
    segs_k = segs[mask]; layers_k = [l for l, ok in zip(layers, mask) if ok]
    # mediana robusta do underlay
    ux = np.concatenate([segs_k[:,0], segs_k[:,2]]); uy = np.concatenate([segs_k[:,1], segs_k[:,3]])
    umx, umy = np.median(ux), np.median(uy)
    cxl, cyl = fp_center_local[sid]            # alvo: centro do footprint (local storey)
    tx, ty = cxl - umx, cyl - umy              # translacao -> coords locais do storey
    # coords locais do storey (para IFC)
    seg_loc = segs_k.copy()
    seg_loc[:,0]+=tx; seg_loc[:,2]+=tx; seg_loc[:,1]+=ty; seg_loc[:,3]+=ty
    # ---- (a) embute no IFC ----
    coords, paths = chain_segments(seg_loc)
    cl = m.create_entity("IfcCartesianPointList3D", CoordList=[(x,y,0.0) for (x,y) in coords])
    curves = []
    for p in paths:
        seg = m.create_entity("IfcLineIndex", [i+1 for i in p])
        curves.append(m.create_entity("IfcIndexedPolyCurve", Points=cl, Segments=[seg], SelfIntersect=False))
    rep = m.create_entity("IfcShapeRepresentation", ContextOfItems=ctx_annot,
        RepresentationIdentifier="Annotation", RepresentationType="GeometricCurveSet", Items=curves)
    shape = m.create_entity("IfcProductDefinitionShape", Representations=[rep])
    placement = m.create_entity("IfcLocalPlacement", PlacementRelTo=storey.ObjectPlacement,
        RelativePlacement=m.create_entity("IfcAxis2Placement3D",
            Location=m.create_entity("IfcCartesianPoint", Coordinates=(0.0,0.0,0.0))))
    ann = m.create_entity("IfcAnnotation", GlobalId=guid(), OwnerHistory=owner,
        Name=f"Underlay DXF - {label}", ObjectType="MTX-UNDERLAY-DXF",
        ObjectPlacement=placement, Representation=shape)
    rel = storey_rel.get(sid)
    if rel: rel.RelatedElements = list(rel.RelatedElements) + [ann]
    else:
        storey_rel[sid] = m.create_entity("IfcRelContainedInSpatialStructure", GlobalId=guid(),
            OwnerHistory=owner, RelatedElements=[ann], RelatingStructure=storey)
    m.create_entity("IfcPresentationLayerWithStyle", Name=layer, AssignedItems=[rep],
        LayerOn=True, LayerFrozen=True, LayerBlocked=True, LayerStyles=[])
    props = [m.create_entity("IfcPropertySingleValue", Name=k,
                NominalValue=m.create_entity("IfcLabel", v)) for k, v in [
                ("SourceDXF", dxf), ("Manifest", "MTX-BIM-HVG-PROT-002"),
                ("Escala", escala), ("CRS", "EPSG:31983 E578800/N7773500/H935"),
                ("Alinhamento", "centro-a-centro (footprint real v95)"), ("Observacao", obs)]]
    pset = m.create_entity("IfcPropertySet", GlobalId=guid(), OwnerHistory=owner,
        Name="MTX_Underlay", HasProperties=props)
    m.create_entity("IfcRelDefinesByProperties", GlobalId=guid(), OwnerHistory=owner,
        RelatedObjects=[ann], RelatingPropertyDefinition=pset)
    # ---- (b) exporta DXF em coords do MODELO v95 (world local) ----
    sx, sy = st_world[sid]
    out = ezdxf.new(dxfversion="R2010"); out.header["$INSUNITS"] = 6
    msp = out.modelspace()
    for lname in {l for l in layers_k}:
        if lname not in out.layers:
            try: out.layers.add(lname)
            except Exception: pass
    for (x1,y1,x2,y2), lname in zip(seg_loc, layers_k):
        msp.add_line((x1+sx, y1+sy), (x2+sx, y2+sy), dxfattribs={"layer": lname})
    out.saveas(f"{OUTD}/{outname}")
    rows.append([dxf, label, storey.Name, outname, round(sx,2), round(sy,2),
                 round(tx,3), round(ty,3), len(segs), int(mask.sum()), len(paths)])
    print(f"  {label:26s} -> {storey.Name:12s} transl_local=({tx:8.2f},{ty:8.2f}) world_origin=({sx:.1f},{sy:.1f}) {outname}")

print(f"\nSalvando IFC {DEST} ...")
m.write(DEST)
# zip + csv
with zipfile.ZipFile(ZIPF, "w", zipfile.ZIP_DEFLATED) as z:
    for r in rows: z.write(f"{OUTD}/{r[3]}", r[3])
with open(CSVF, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source_dxf","edificio","pavimento","dxf_saida","model_origin_x","model_origin_y",
                "transl_local_x","transl_local_y","linhas_orig","linhas_uteis","polilinhas"])
    w.writerows(rows)
print(f"Zip: {ZIPF}  | CSV: {CSVF}  | tempo {time.time()-t0:.1f}s")
