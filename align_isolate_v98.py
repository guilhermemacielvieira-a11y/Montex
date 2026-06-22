"""
Pipeline final de underlays (v95 -> v98 consolidado):
 - de-rotacao automatica (estimativa do angulo dominante) -> resolve Bloco Principal ~45 graus
 - isolamento da planta por JANELA DE DENSIDADE usando o footprint real como gabarito
   (aplicado as folhas com planta+cortes: Guarita, SPA, Boite, e a planta do Bloco Principal)
 - alinhamento centro-a-centro ao footprint real (bbox via iterador geom)
Saidas:
 - HVG_MASTER_v98_underlays_iso.ifc  (consolidado, ultima versao)
 - HVG_underlays_georef_v98.zip + HVG_underlays_transform_v98.csv
 - HVG_v98_Underlays_Overlay.png
"""
import ifcopenshell, ifcopenshell.geom as geom, ezdxf, uuid, time, os, zipfile, csv
import numpy as np
from collections import defaultdict

SRC  = "/home/user/Montex/HVG_MASTER_v95_corrigido.ifc"
DEST = "/home/user/Montex/HVG_MASTER_v98_underlays_iso.ifc"
PKG  = "/tmp/ac_pkg"; OUTD = "/tmp/georef98"
ZIPF = "/home/user/Montex/HVG_underlays_georef_v98.zip"
CSVF = "/home/user/Montex/HVG_underlays_transform_v98.csv"
QUANT = 0.001

# (dxf, rotulo, storey_id, layer, escala, isolar, nome_saida)
UNDERLAYS = [
    ("02.dxf", "Guarita",               127, "MTX-Underlay-Guarita", "1:50",  True,  "HVG_Guarita_underlay_georef.dxf"),
    ("05.dxf", "Centro de Convencoes",   56,  "MTX-Underlay-CC",      "1:100", False, "HVG_CentroConvencoes_underlay_georef.dxf"),
    ("06.dxf", "Restaurante da Piscina", 82,  "MTX-Underlay-RP",      "1:100", False, "HVG_RestaurantePiscina_underlay_georef.dxf"),
    ("09.dxf", "Clube NEP",              114, "MTX-Underlay-NEP",     "1:100", False, "HVG_ClubeNEP_underlay_georef.dxf"),
    ("13.dxf", "SPA",                    101, "MTX-Underlay-SPA",     "1:100", True,  "HVG_SPA_underlay_georef.dxf"),
    ("04.dxf", "Boite",                  69,  "MTX-Underlay-Boite",   "1:100", True,  "HVG_Boite_underlay_georef.dxf"),
    ("BlocoPrincipal_R1_Proje_o_da_Cobertura.dxf", "Bloco Principal", 43, "MTX-Underlay-BP", "1:100", True, "HVG_BlocoPrincipal_underlay_georef.dxf"),
    ("BlocoB_R1_Planta_1.dxf", "Bloco B - Terreo/Subsolo", 446, "MTX-Underlay-BlocoB-T", "1:100", False, "HVG_BlocoB_Terreo_underlay_georef.dxf"),
    ("BlocoB_R2_UPLANTA_1_PAVIMENTO.dxf", "Bloco B - 1 Pavimento", 452, "MTX-Underlay-BlocoB-P1", "1:100", False, "HVG_BlocoB_Pav1_underlay_georef.dxf"),
]

t0 = time.time()
m = ifcopenshell.open(SRC)
owner = m.by_type("IfcOwnerHistory")[0] if m.by_type("IfcOwnerHistory") else None

def world_xy(el):
    x=y=0.0; p=el.ObjectPlacement
    while p:
        rp=p.RelativePlacement
        if rp and rp.is_a("IfcAxis2Placement3D"):
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]
        p=p.PlacementRelTo
    return x,y

# ---- footprint real (bbox via iterador geom) + tamanho ----
TARGET={sid:m.by_id(sid) for (_,_,sid,*_ ) in UNDERLAYS}
st_world={sid:world_xy(st) for sid,st in TARGET.items()}
el_storey={}; include=[]
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    sid=rel.RelatingStructure.id()
    if sid in TARGET:
        for el in rel.RelatedElements:
            if el.is_a("IfcAnnotation"): continue
            if el.Representation: el_storey[el.id()]=sid; include.append(el)
s=geom.settings(); s.set(s.USE_WORLD_COORDS,True)
it=geom.iterator(s,m,4,include=include)
bb=defaultdict(lambda:[1e18,1e18,-1e18,-1e18])
if it.initialize():
    while True:
        sh=it.get(); sid=el_storey.get(sh.id)
        if sid is not None:
            v=np.array(sh.geometry.verts).reshape(-1,3)
            if len(v):
                b=bb[sid]
                b[0]=min(b[0],v[:,0].min()); b[1]=min(b[1],v[:,1].min())
                b[2]=max(b[2],v[:,0].max()); b[3]=max(b[3],v[:,1].max())
        if not it.next(): break
fp_center={}; fp_size={}
for sid in TARGET:
    b=bb[sid]; sx,sy=st_world[sid]
    fp_center[sid]=((b[0]+b[2])/2-sx,(b[1]+b[3])/2-sy)
    fp_size[sid]=(b[2]-b[0],b[3]-b[1])

# ---- helpers de geometria ----
def read_lines_layers(path):
    doc=ezdxf.readfile(path); segs=[]; lay=[]
    for e in doc.modelspace():
        if e.dxftype()=="LINE":
            s=e.dxf.start; t=e.dxf.end; segs.append((s.x,s.y,t.x,t.y)); lay.append(e.dxf.layer)
    return np.array(segs,float), np.array(lay,object)

def outlier_mask(segs):
    xs=np.concatenate([segs[:,0],segs[:,2]]); ys=np.concatenate([segs[:,1],segs[:,3]])
    xlo,xhi=np.percentile(xs,.5),np.percentile(xs,99.5); ylo,yhi=np.percentile(ys,.5),np.percentile(ys,99.5)
    mx=(xhi-xlo)*.05+1; my=(yhi-ylo)*.05+1; xlo-=mx;xhi+=mx;ylo-=my;yhi+=my
    return ((segs[:,0]>=xlo)&(segs[:,0]<=xhi)&(segs[:,1]>=ylo)&(segs[:,1]<=yhi)&
            (segs[:,2]>=xlo)&(segs[:,2]<=xhi)&(segs[:,3]>=ylo)&(segs[:,3]<=yhi))

def estimate_angle(segs):
    dx=segs[:,2]-segs[:,0]; dy=segs[:,3]-segs[:,1]; L=np.hypot(dx,dy)
    th=(np.degrees(np.arctan2(dy,dx)))%90.0
    h,_=np.histogram(th,bins=np.arange(0,90.0001,0.5),weights=L)
    peak=(np.argmax(h)+0.5)*0.5
    return peak-90 if peak>45 else peak

def rotate(segs,ang,pivot):
    a=np.radians(-ang); ca,sa=np.cos(a),np.sin(a); px,py=pivot; out=segs.copy()
    for i in (0,2):
        x=segs[:,i]-px; y=segs[:,i+1]-py
        out[:,i]=ca*x-sa*y+px; out[:,i+1]=sa*x+ca*y+py
    return out

def density_center(segs,W,H,cell=0.5):
    mx=(segs[:,0]+segs[:,2])/2; my=(segs[:,1]+segs[:,3])/2
    L=np.hypot(segs[:,2]-segs[:,0],segs[:,3]-segs[:,1])
    x0,y0=mx.min(),my.min(); x1,y1=mx.max(),my.max()
    nx=max(int((x1-x0)/cell)+1,1); ny=max(int((y1-y0)/cell)+1,1)
    H2,_,_=np.histogram2d(mx,my,bins=[nx,ny],range=[[x0,x0+nx*cell],[y0,y0+ny*cell]],weights=L)
    wx=min(max(int(W/cell),1),nx); wy=min(max(int(H/cell),1),ny)
    S=np.pad(H2.cumsum(0).cumsum(1),((1,0),(1,0)))
    tot=(S[wx:,wy:]-S[:-wx,wy:]-S[wx:,:-wy]+S[:-wx,:-wy])
    bi,bj=np.unravel_index(np.argmax(tot),tot.shape)
    return x0+(bi+wx/2)*cell, y0+(bj+wy/2)*cell

def chain_segments(segs):
    def key(x,y): return (round(x/QUANT),round(y/QUANT))
    pidx={}; coords=[]
    def idx(x,y):
        k=key(x,y)
        if k not in pidx: pidx[k]=len(coords); coords.append((float(x),float(y)))
        return pidx[k]
    edges=[]; adj=defaultdict(list)
    for (x1,y1,x2,y2) in segs:
        a=idx(x1,y1); b=idx(x2,y2)
        if a==b: continue
        eid=len(edges); edges.append((a,b)); adj[a].append((b,eid)); adj[b].append((a,eid))
    used=[False]*len(edges); paths=[]
    for e0 in range(len(edges)):
        if used[e0]: continue
        a,b=edges[e0]; used[e0]=True; path=[a,b]; cur=b
        while True:
            nx=next(((nb,eid) for (nb,eid) in adj[cur] if not used[eid]),None)
            if nx is None: break
            used[nx[1]]=True; path.append(nx[0]); cur=nx[0]
        cur=a
        while True:
            nx=next(((nb,eid) for (nb,eid) in adj[cur] if not used[eid]),None)
            if nx is None: break
            used[nx[1]]=True; path.insert(0,nx[0]); cur=nx[0]
        paths.append(path)
    return coords,paths

# ---- contexto de anotacao ----
ctx_model=None
for c in m.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType=="Model": ctx_model=c
ctx_model=ctx_model or m.by_type("IfcGeometricRepresentationContext")[0]
ctx_annot=m.create_entity("IfcGeometricRepresentationSubContext",ContextIdentifier="Annotation",
    ContextType="Plan",ParentContext=ctx_model,TargetView="PLAN_VIEW")
def guid(): return ifcopenshell.guid.compress(uuid.uuid4().hex)
storey_rel={}
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    if rel.RelatingStructure.is_a("IfcBuildingStorey"): storey_rel.setdefault(rel.RelatingStructure.id(),rel)

os.makedirs(OUTD,exist_ok=True)
rows=[]; overlay=[]
for dxf,label,sid,layer,escala,isolar,outname in UNDERLAYS:
    storey=m.by_id(sid); W,H=fp_size[sid]; cxl,cyl=fp_center[sid]
    segs,lay=read_lines_layers(f"{PKG}/{dxf}")
    mk=outlier_mask(segs); segs=segs[mk]; lay=lay[mk]
    ang=estimate_angle(segs); derot=abs(ang)>3
    if derot:
        piv=(np.median(np.concatenate([segs[:,0],segs[:,2]])),np.median(np.concatenate([segs[:,1],segs[:,3]])))
        segs=rotate(segs,ang,piv)
    n_before=len(segs)
    if isolar:
        cx,cy=density_center(segs,W,H)
        isoW,isoH=max(W*1.15,W+8),max(H*1.15,H+8)
        mx=(segs[:,0]+segs[:,2])/2; my=(segs[:,1]+segs[:,3])/2
        keep=(np.abs(mx-cx)<=isoW/2)&(np.abs(my-cy)<=isoH/2)
        segs=segs[keep]; lay=lay[keep]
    n_iso=len(segs)
    ux=np.concatenate([segs[:,0],segs[:,2]]); uy=np.concatenate([segs[:,1],segs[:,3]])
    ref=(np.median(ux),np.median(uy)); tx,ty=cxl-ref[0],cyl-ref[1]
    seg_loc=segs.copy(); seg_loc[:,0]+=tx; seg_loc[:,2]+=tx; seg_loc[:,1]+=ty; seg_loc[:,3]+=ty
    # ---- IFC ----
    coords,paths=chain_segments(seg_loc)
    cl=m.create_entity("IfcCartesianPointList3D",CoordList=[(x,y,0.0) for (x,y) in coords])
    curves=[m.create_entity("IfcIndexedPolyCurve",Points=cl,
            Segments=[m.create_entity("IfcLineIndex",[i+1 for i in p])],SelfIntersect=False) for p in paths]
    rep=m.create_entity("IfcShapeRepresentation",ContextOfItems=ctx_annot,
        RepresentationIdentifier="Annotation",RepresentationType="GeometricCurveSet",Items=curves)
    shape=m.create_entity("IfcProductDefinitionShape",Representations=[rep])
    placement=m.create_entity("IfcLocalPlacement",PlacementRelTo=storey.ObjectPlacement,
        RelativePlacement=m.create_entity("IfcAxis2Placement3D",
            Location=m.create_entity("IfcCartesianPoint",Coordinates=(0.0,0.0,0.0))))
    ann=m.create_entity("IfcAnnotation",GlobalId=guid(),OwnerHistory=owner,
        Name=f"Underlay DXF - {label}",ObjectType="MTX-UNDERLAY-DXF",
        ObjectPlacement=placement,Representation=shape)
    rel=storey_rel.get(sid)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+[ann]
    else: storey_rel[sid]=m.create_entity("IfcRelContainedInSpatialStructure",GlobalId=guid(),
        OwnerHistory=owner,RelatedElements=[ann],RelatingStructure=storey)
    m.create_entity("IfcPresentationLayerWithStyle",Name=layer,AssignedItems=[rep],
        LayerOn=True,LayerFrozen=True,LayerBlocked=True,LayerStyles=[])
    metodo=("isolado+de-rotado" if (isolar and derot) else "isolado" if isolar else "centro-a-centro")
    props=[m.create_entity("IfcPropertySingleValue",Name=k,NominalValue=m.create_entity("IfcLabel",v))
           for k,v in [("SourceDXF",dxf),("Manifest","MTX-BIM-HVG-PROT-002"),("Escala",escala),
           ("CRS","EPSG:31983 E578800/N7773500/H935"),("Metodo",metodo),
           ("RotacaoAplicada_graus",f"{ang:.1f}" if derot else "0")]]
    pset=m.create_entity("IfcPropertySet",GlobalId=guid(),OwnerHistory=owner,Name="MTX_Underlay",HasProperties=props)
    m.create_entity("IfcRelDefinesByProperties",GlobalId=guid(),OwnerHistory=owner,
        RelatedObjects=[ann],RelatingPropertyDefinition=pset)
    # ---- DXF georref (coords do modelo v95) ----
    sx,sy=st_world[sid]
    out=ezdxf.new(dxfversion="R2010"); out.header["$INSUNITS"]=6; msp=out.modelspace()
    for ln in set(lay.tolist()):
        if ln not in out.layers:
            try: out.layers.add(ln)
            except Exception: pass
    for (x1,y1,x2,y2),ln in zip(seg_loc,lay):
        msp.add_line((x1+sx,y1+sy),(x2+sx,y2+sy),dxfattribs={"layer":ln})
    out.saveas(f"{OUTD}/{outname}")
    rows.append([dxf,label,storey.Name,outname,metodo,f"{ang:.1f}" if derot else "0",
                 n_before,n_iso,len(paths),round(sx,1),round(sy,1)])
    overlay.append((label,storey.Name,seg_loc,(sx,sy)))
    print(f"  {label:26s} {metodo:18s} rot={ang if derot else 0:6.1f}  linhas {n_before:>7d}->{n_iso:<7d} poly={len(paths):>6d}")

print(f"\nSalvando IFC consolidado {DEST} ...")
m.write(DEST)
with zipfile.ZipFile(ZIPF,"w",zipfile.ZIP_DEFLATED) as z:
    for r in rows: z.write(f"{OUTD}/{r[3]}",r[3])
with open(CSVF,"w",newline="") as f:
    w=csv.writer(f); w.writerow(["source_dxf","edificio","pavimento","dxf_saida","metodo",
        "rotacao_graus","linhas_pre_iso","linhas_pos_iso","polilinhas","model_x","model_y"]); w.writerows(rows)

# ---- overlay de verificacao ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
st_loc=defaultdict(list)
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    st=rel.RelatingStructure
    if not st.is_a("IfcBuildingStorey"): continue
    sx,sy=world_xy(st)
    for el in rel.RelatedElements:
        if el.is_a("IfcAnnotation") or not el.ObjectPlacement: continue
        wx,wy=world_xy(el); st_loc[st.Name].append((wx,wy))
fig,axs=plt.subplots(3,3,figsize=(18,18))
for ax,(label,sname,seg_loc,(sx,sy)) in zip(axs.flat,overlay):
    segw=[[(s[0]+sx,s[1]+sy),(s[2]+sx,s[3]+sy)] for s in seg_loc]
    ax.add_collection(LineCollection(segw,colors="#1f4e79",lw=0.2))
    fp=np.array(st_loc.get(sname,[]))
    if len(fp):
        fp=fp[(np.abs(fp[:,0])>0.01)|(np.abs(fp[:,1])>0.01)]
        # footprint bbox real
    b=bb[[k for k in TARGET if m.by_id(k).Name==sname][0]] if any(m.by_id(k).Name==sname for k in TARGET) else None
    if b: ax.add_patch(plt.Rectangle((b[0],b[1]),b[2]-b[0],b[3]-b[1],fill=False,ec="red",lw=2,label="footprint v95"))
    ax.set_title(f"{label} [{sname}]",fontsize=11); ax.autoscale(); ax.set_aspect("equal"); ax.grid(alpha=.2); ax.legend(fontsize=7)
plt.suptitle("v98 — underlays isolados/de-rotados (azul) x footprint real v95 (retangulo vermelho)",fontsize=14)
plt.tight_layout(); plt.savefig("HVG_v98_Underlays_Overlay.png",dpi=80,bbox_inches="tight")
print(f"Overlay salvo. Tempo total {time.time()-t0:.1f}s")
