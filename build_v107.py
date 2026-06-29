"""
HVG v106 -> v107 : remodelagem DETALHADA das 312 varandas dos blocos.
Para cada IfcSpace VAR (3.0 x 2.0 x 2.6 m), orientada pelo apartamento vizinho:
  - Piso de DECK de madeira
  - Guarda-corpo de VIDRO azul nas 3 bordas externas (frente + 2 laterais)
  - Porta-janela de VIDRO azul na face interna (lado do apto)
  - Forro
Remove os 48 guarda-corpos antigos (inconsistentes) e recria todos.
Saida: HVG_MASTER_v107_VARANDAS.ifc
"""
import ifcopenshell, time, os, numpy as np
import ifcopenshell.util.element as ue
from ifcopenshell.guid import new as guid

SRC="/home/user/Montex/HVG_MASTER_v106_LIMPO.ifc"
DEST="/home/user/Montex/HVG_MASTER_v107_VARANDAS.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]
ctx=None
for c in f.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType=="Model": ctx=c
ctx=ctx or f.by_type("IfcGeometricRepresentationContext")[0]
body=None
for c in f.by_type("IfcGeometricRepresentationSubContext"):
    if c.ContextIdentifier=="Body": body=c
body=body or ctx

def col(rgb): return f.create_entity("IfcColourRgb",None,float(rgb[0]),float(rgb[1]),float(rgb[2]))
def style(rgb,method,spec,rough,t=0.0):
    rnd=f.create_entity("IfcSurfaceStyleRendering",col(rgb),float(t),col(rgb),None,None,
        col(tuple(min(1,x*1.15+0.1) for x in rgb)),f.create_entity("IfcNormalisedRatioMeasure",float(spec)),
        f.create_entity("IfcSpecularRoughness",float(rough)),method)
    return f.create_entity("IfcSurfaceStyle",None,"BOTH",(rnd,))
ST_DECK=style((0.50,0.33,0.18),"PLASTIC",0.35,0.45)
ST_GC=style((0.55,0.72,0.86),"GLASS",0.9,0.05,t=0.5)
ST_PJ=style((0.40,0.58,0.78),"GLASS",0.92,0.04,t=0.5)
ST_FORRO=style((0.93,0.93,0.91),"MATT",0.05,0.95)

def P3(x,y,z): return f.create_entity("IfcCartesianPoint",(float(x),float(y),float(z)))
def D3(x,y,z): return f.create_entity("IfcDirection",(float(x),float(y),float(z)))
def A2P3(x=0,y=0,z=0): return f.create_entity("IfcAxis2Placement3D",P3(x,y,z),D3(0,0,1),D3(1,0,0))
def box(L,W,H,cx,cy,cz):
    prof=f.create_entity("IfcRectangleProfileDef","AREA",None,
        f.create_entity("IfcAxis2Placement2D",f.create_entity("IfcCartesianPoint",(float(cx),float(cy))),
        f.create_entity("IfcDirection",(1.,0.))),float(L),float(W))
    return f.create_entity("IfcExtrudedAreaSolid",prof,A2P3(0,0,cz),D3(0,0,1),float(H))

def matrix(el):
    M=np.eye(4); chain=[]; p=el.ObjectPlacement
    while p: chain.append(p); p=p.PlacementRelTo
    for p in reversed(chain):
        rp=getattr(p,"RelativePlacement",None); T=np.eye(4)
        if rp and rp.is_a("IfcAxis2Placement3D"):
            if rp.Location: T[:3,3]=rp.Location.Coordinates
            if rp.RefDirection:
                x=np.array(list(rp.RefDirection.DirectionRatios)+[0,0,0])[:3]; x=x/ (np.linalg.norm(x) or 1)
                z=np.array(rp.Axis.DirectionRatios) if rp.Axis else np.array([0,0,1.]); z=z/(np.linalg.norm(z) or 1)
                x=x-x.dot(z)*z; x=x/(np.linalg.norm(x) or 1); y=np.cross(z,x)
                T[:3,0]=x; T[:3,1]=y; T[:3,2]=z
        M=M@T
    return M

# space -> storey (aggregates)
sp_storey={}
for rel in f.by_type("IfcRelAggregates"):
    if rel.RelatingObject.is_a("IfcBuildingStorey"):
        for c in rel.RelatedObjects:
            if c.is_a("IfcSpace"): sp_storey[c.id()]=rel.RelatingObject
# storey -> APT spaces (centros world)
storey_apts={}
for sp in f.by_type("IfcSpace"):
    if (sp.Name or "").startswith("APT"):
        st=sp_storey.get(sp.id())
        if st: storey_apts.setdefault(st.id(),[]).append((matrix(sp)[:2,3],sp))

# remove guarda-corpos de varanda antigos
old=[r for r in f.by_type("IfcRailing") if "Varanda" in (r.Name or "")]
for r in old:
    try: ue.remove_deep2(f,r)
    except Exception:
        r.Representation=None
print(f"Guarda-corpos antigos removidos: {len(old)}")

# rel de contencao por storey
storey_rel={}
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    if rel.RelatingStructure.is_a("IfcBuildingStorey"): storey_rel.setdefault(rel.RelatingStructure.id(),rel)

def add(cls,name,space_place,solid,style_):
    rep=f.create_entity("IfcShapeRepresentation",body,"Body","SweptSolid",(solid,))
    pds=f.create_entity("IfcProductDefinitionShape",None,None,(rep,))
    place=f.create_entity("IfcLocalPlacement",space_place,A2P3())
    el=f.create_entity(cls,guid(),oh,name,None,None,place,pds,None)
    f.create_entity("IfcStyledItem",solid,(style_,),None)
    return el

# dimensoes do modulo varanda (do bbox medido: X3.0 Y2.0 Z2.6)
LX,LY,LZ=3.0,2.0,2.6
nv=0; created=[]
for sp in f.by_type("IfcSpace"):
    if "VAR" not in (sp.Name or ""): continue
    st=sp_storey.get(sp.id())
    if st is None: continue
    M=matrix(sp); cvar=M[:2,3]
    # apto mais proximo no mesmo storey -> direcao externa
    apts=storey_apts.get(st.id(),[])
    sy=1.0
    if apts:
        capt=min(apts,key=lambda a:np.hypot(*(a[0]-cvar)))[0]
        dirw=np.array([cvar[0]-capt[0],cvar[1]-capt[1],0.0])
        dl=M[:3,:3].T@dirw   # direcao externa em coords locais do space
        sy=1.0 if dl[1]>=0 else -1.0
    items=[]
    sps=sp.ObjectPlacement
    # piso deck (base)
    items.append(("IfcSlab","Piso-Deck-"+sp.Name, box(LX,LY,0.05,0,0,0.0), ST_DECK))
    # forro (topo)
    items.append(("IfcCovering","Forro-"+sp.Name, box(LX,LY,0.04,0,0,LZ-0.04), ST_FORRO))
    # guarda-corpos vidro: frente (Y externo) + 2 laterais (X)
    items.append(("IfcRailing","GC-Vidro-Frente-"+sp.Name, box(LX,0.05,1.1,0, sy*(LY/2-0.03),0.0), ST_GC))
    items.append(("IfcRailing","GC-Vidro-LatE-"+sp.Name, box(0.05,LY,1.1,-(LX/2-0.03),0,0.0), ST_GC))
    items.append(("IfcRailing","GC-Vidro-LatD-"+sp.Name, box(0.05,LY,1.1, (LX/2-0.03),0,0.0), ST_GC))
    # porta-janela vidro azul na face interna (-sy)
    items.append(("IfcWindow","PortaJanela-"+sp.Name, box(LX-0.2,0.08,2.1,0, -sy*(LY/2-0.04),0.0), ST_PJ))
    rel=storey_rel.get(st.id())
    newels=[]
    for cls,nm,solid,stl in items:
        el=add(cls,nm,sps,solid,stl); newels.append(el)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+newels
    else: storey_rel[st.id()]=f.create_entity("IfcRelContainedInSpatialStructure",guid(),oh,None,None,newels,m_st if False else f.by_id(st.id()))
    created+=newels; nv+=1

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "").split(' | v107')[0]+" | v107: varandas remodeladas em detalhe (deck+guarda-corpo vidro+porta-janela+forro)"
f.write(DEST)
print(f"Varandas remodeladas: {nv} | novos elementos: {len(created)}")
print(f"Salvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
