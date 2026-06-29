"""
HVG v101 -> v104 : nivelamento ROBUSTO (corrige TODOS os descolamentos).
Abordagem: nao move buildings/storeys (alguns elementos tem placement absoluto e
nao acompanhariam). Em vez disso, desloca CADA elemento fisico pela cota de
implantacao do seu edificio (ou do terreno, se for paisagem/via):
    placement_local_Z -= cota_impl_local
Funciona para placement relativo E absoluto. Preserva altura relativa (telhado no
topo, subsolo abaixo, piso no chao). Remove o morro; gramado plano como paisagem.
Saida: HVG_MASTER_v104_NIVELADO_OK.ifc
"""
import ifcopenshell, time, os, numpy as np
from ifcopenshell.guid import new as guid
from scipy.interpolate import griddata

SRC="/home/user/Montex/HVG_MASTER_v101_DIMENSIONADO.ifc"
DEST="/home/user/Montex/HVG_MASTER_v104_NIVELADO_OK.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]
site=f.by_type("IfcSite")[0]

def pxy(el):
    x=y=0.0; p=el.ObjectPlacement
    while p:
        rp=getattr(p,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location:
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]
        p=getattr(p,"PlacementRelTo",None)
    return x,y

# ---- malha do terreno -> interpolador da cota ----
sx,sy,soz=0.0,0.0,0.0
p=site.ObjectPlacement
while p:
    rp=p.RelativePlacement
    if rp and rp.Location: c=rp.Location.Coordinates; sx+=c[0]; sy+=c[1]; soz+=c[2]
    p=p.PlacementRelTo
tfs=[it for r in site.Representation.Representations for it in r.Items if it.is_a("IfcTriangulatedFaceSet")][0]
V=np.array(tfs.Coordinates.CoordList,float)
TX=V[:,0]+sx; TY=V[:,1]+sy; TZ=V[:,2]+soz
def terreno_z(x,y):
    z=griddata((TX,TY),TZ,(x,y),method="linear")
    if np.isnan(z): z=griddata((TX,TY),TZ,(x,y),method="nearest")
    return float(z)

# ---- cota de implantacao (terreo) de cada edificio ----
build_z={}
for b in f.by_type("IfcBuilding"):
    pl=b.ObjectPlacement
    if pl and pl.RelativePlacement and pl.RelativePlacement.Location:
        build_z[b.Name]=pl.RelativePlacement.Location.Coordinates[2]
bnames=sorted([n for n in build_z if n], key=len, reverse=True)

# storey -> building (cota)
def building_of(obj):
    for rel in f.by_type("IfcRelAggregates"):
        if obj in (rel.RelatedObjects or []):
            par=rel.RelatingObject
            return par if par.is_a("IfcBuilding") else building_of(par)
    return None
storey_bz={}
for st in f.by_type("IfcBuildingStorey"):
    b=building_of(st)
    if b and b.Name in build_z: storey_bz[st.id()]=build_z[b.Name]

# geom XY (placement + centroide da geometria absoluta) para elementos de site
def geom_xy(el):
    px,py=pxy(el); xs=[]; ys=[]
    if el.Representation:
        for rep in el.Representation.Representations:
            for it in rep.Items:
                for sub in f.traverse(it):
                    if sub.is_a("IfcExtrudedAreaSolid") and sub.Position and sub.Position.Location:
                        c=sub.Position.Location.Coordinates; xs.append(c[0]); ys.append(c[1])
                    elif sub.is_a("IfcCartesianPoint") and len(sub.Coordinates)==3:
                        c=sub.Coordinates; xs.append(c[0]); ys.append(c[1])
    if xs: return px+float(np.mean(xs)), py+float(np.mean(ys))
    return px,py
def building_in_name(nm):
    for bn in bnames:
        if bn in (nm or ""): return bn
    return None

# container (storey/site) e pai (aggregates) de cada elemento
el_container={}
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    st=rel.RelatingStructure
    for el in rel.RelatedElements: el_container[el.id()]=st
parent_of={}
for rel in f.by_type("IfcRelAggregates"):
    for c in (rel.RelatedObjects or []): parent_of[c.id()]=rel.RelatingObject

def ref_of(el):
    """cota de implantacao subindo container + aggregates ate achar building/storey."""
    cur=el
    for _ in range(12):
        if cur is None: break
        c=el_container.get(cur.id())
        if c is not None:
            if c.is_a("IfcBuildingStorey") and c.id() in storey_bz: return storey_bz[c.id()]
            if c.is_a("IfcBuilding") and c.Name in build_z: return build_z[c.Name]
            cur=c; continue
        p=parent_of.get(cur.id())
        if p is not None:
            if p.is_a("IfcBuilding") and p.Name in build_z: return build_z[p.Name]
            if p.is_a("IfcBuildingStorey") and p.id() in storey_bz: return storey_bz[p.id()]
            cur=p; continue
        break
    return None

# ---- desloca cada elemento fisico por -cota_impl ----
SKIP={"IfcSite","IfcBuilding","IfcBuildingStorey","IfcAnnotation","IfcSpace","IfcGrid","IfcGridAxis","IfcOpeningElement"}
done=set(); n=0; nb=0; nt=0
for el in f.by_type("IfcElement"):
    if el.is_a() in SKIP: continue
    pl=getattr(el,"ObjectPlacement",None)
    if not (pl and pl.RelativePlacement and pl.RelativePlacement.Location): continue
    if pl.id() in done: continue
    ref=ref_of(el)
    if ref is not None:
        nb+=1
    else:
        bn=building_in_name(el.Name)
        if bn: ref=build_z[bn]; nb+=1
        else:
            x,y=geom_xy(el); ref=terreno_z(x,y); nt+=1
    lx,ly,lz=pl.RelativePlacement.Location.Coordinates
    pl.RelativePlacement.Location.Coordinates=(float(lx),float(ly),float(lz-ref))
    done.add(pl.id()); n+=1

# ---- desloca IfcSpace (ambientes/varandas) junto com seu edificio ----
space_storey={}
for rel in f.by_type("IfcRelAggregates"):
    if rel.RelatingObject.is_a("IfcBuildingStorey"):
        for c in rel.RelatedObjects:
            if c.is_a("IfcSpace"): space_storey[c.id()]=rel.RelatingObject
nsp=0
for sp in f.by_type("IfcSpace"):
    pl=getattr(sp,"ObjectPlacement",None)
    if not (pl and pl.RelativePlacement and pl.RelativePlacement.Location): continue
    if pl.id() in done: continue
    ref=ref_of(sp)
    if ref is None:
        st=space_storey.get(sp.id())
        ref=storey_bz.get(st.id()) if st else None
    if ref is None:
        bn=building_in_name(sp.Name) or building_in_name(sp.LongName)
        ref=build_z[bn] if bn else terreno_z(*geom_xy(sp))
    lx,ly,lz=pl.RelativePlacement.Location.Coordinates
    pl.RelativePlacement.Location.Coordinates=(float(lx),float(ly),float(lz-ref))
    done.add(pl.id()); nsp+=1

# ---- passo final: clamp de outliers remanescentes (referencia falhou) ----
def geom_minz(el):
    zs=[]
    for rep in (el.Representation.Representations if el.Representation else []):
        for it in rep.Items:
            for sub in f.traverse(it):
                if sub.is_a("IfcExtrudedAreaSolid"):
                    b=sub.Position.Location.Coordinates[2] if (sub.Position and sub.Position.Location) else 0.0
                    zs.append(b)
    return min(zs) if zs else 0.0
def wz_el(el):
    z=0.0;p=el.ObjectPlacement
    while p:
        rp=getattr(p,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location: z+=rp.Location.Coordinates[2]
        p=getattr(p,"PlacementRelTo",None)
    return z
SKIP_CLAMP={"IfcSite","IfcBuilding","IfcBuildingStorey","IfcGrid","IfcGridAxis","IfcOpeningElement","IfcAnnotation"}
nclamp=0
for el in list(f.by_type("IfcElement"))+list(f.by_type("IfcSpace")):
    if el.is_a() in SKIP_CLAMP or not el.Representation: continue
    pl=getattr(el,"ObjectPlacement",None)
    if not (pl and pl.RelativePlacement and pl.RelativePlacement.Location): continue
    base=wz_el(el)+geom_minz(el)
    if base>11 or base<-7:               # fora da faixa plausivel (predios ate ~9m, subsolo -5.6)
        lx,ly,lz=pl.RelativePlacement.Location.Coordinates
        pl.RelativePlacement.Location.Coordinates=(float(lx),float(ly),float(lz-base))  # base -> 0
        nclamp+=1

# ---- remove morro + terrenos complementares ----
site.Representation=None
rt=0
for g in f.by_type("IfcGeographicElement"):
    if "TERRENO" in ((g.ObjectType or "")+(g.Name or "")).upper(): g.Representation=None; rt+=1

# ---- gramado plano (paisagem) logo abaixo do plano 0 ----
def P3(x,y,z): return f.create_entity("IfcCartesianPoint",(float(x),float(y),float(z)))
def D3(x,y,z): return f.create_entity("IfcDirection",(float(x),float(y),float(z)))
ctx=None
for c in f.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType=="Model": ctx=c
ctx=ctx or f.by_type("IfcGeometricRepresentationContext")[0]
X0,Y0,X1,Y1=-40,-40,460,540
prof=f.create_entity("IfcRectangleProfileDef","AREA",None,
    f.create_entity("IfcAxis2Placement2D",f.create_entity("IfcCartesianPoint",((X0+X1)/2,(Y0+Y1)/2)),
    f.create_entity("IfcDirection",(1.,0.))),float(X1-X0),float(Y1-Y0))
solid=f.create_entity("IfcExtrudedAreaSolid",prof,
    f.create_entity("IfcAxis2Placement3D",P3(0,0,-0.30),D3(0,0,1),D3(1,0,0)),D3(0,0,1),0.30)
rep=f.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",(solid,))
pds=f.create_entity("IfcProductDefinitionShape",None,None,(rep,))
place=f.create_entity("IfcLocalPlacement",site.ObjectPlacement,
    f.create_entity("IfcAxis2Placement3D",P3(0,0,0),D3(0,0,1),D3(1,0,0)))
grama=f.create_entity("IfcGeographicElement",guid(),oh,"Gramado-Paisagem","Terreno plano (paisagem)",None,place,pds,None,"TERRAIN")
mat=f.create_entity("IfcMaterial","Grama Paisagem",None,None)
col=f.create_entity("IfcColourRgb",None,0.36,0.55,0.27)
rnd=f.create_entity("IfcSurfaceStyleRendering",col,0.0,None,None,None,None,None,None,"NOTDEFINED")
stl=f.create_entity("IfcSurfaceStyle","Grama Paisagem","BOTH",(rnd,))
f.create_entity("IfcStyledItem",solid,(stl,),None)
f.create_entity("IfcRelAssociatesMaterial",guid(),oh,None,None,[grama],mat)
f.create_entity("IfcRelContainedInSpatialStructure",guid(),oh,None,None,[grama],site)

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "").split(' | v10')[0]+" | v104: nivelado ao plano 0 por elemento (robusto a placement absoluto), terreno so paisagem"
f.write(DEST)
print(f"Elementos deslocados: {n} (edificio: {nb}, terreno: {nt}) + {nsp} spaces | morro+{rt} terrenos removidos")
print(f"Salvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
