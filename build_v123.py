#!/usr/bin/env python3
"""HVG Inhotim v123 — nivel de cobertura dos apartamentos (terracos/platibandas).

Cria um IfcBuildingStorey 'Cobertura' em cada bloco (A em +2,8; B em +5,6) e
mapeia as muretas/platibandas da PLANTA da COBERTURA (camada Par1) como IfcWall
de 1,0 m (parapeito). A laje de cobertura ja existe (IfcRoof)."""
import sys, json
import numpy as np, ifcopenshell, ifcopenshell.guid
sys.path.insert(0,"/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from detail_lib import wall_segments, map_to_footprint
SC="/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC="HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc"; OUT="HVG_MASTER_v123_APTOS_COBERTURA.ifc"
THICK=0.20; H=1.0
ST=json.load(open(f"{SC}/apt_storeys.json"))
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection",DirectionRatios=[float(x) for x in v])
def soff(st):
    o=np.zeros(3);p=st.ObjectPlacement
    while p:
        rp=p.RelativePlacement
        if rp and rp.Location:o=o+np.array(rp.Location.Coordinates)
        p=p.PlacementRelTo
    return o
# quadrante de cobertura
SEGA=None;SEGB=None
def quad(jf,xlo,xhi,ylo,yhi):
    seg=wall_segments(f"{SC}/{jf}",{"Par1"})
    mid=np.c_[(seg[:,0]+seg[:,2])/2,(seg[:,1]+seg[:,3])/2]
    m=(mid[:,0]>xlo)&(mid[:,0]<xhi)&(mid[:,1]>ylo)&(mid[:,1]<yhi)
    return seg[m]
SEGA=quad("bld_aptA.json",3494,3545,1395,1421)
SEGB=quad("bld_aptB.json",3505,3550,1397,1423)
print("cobertura segs: A",len(SEGA),"B",len(SEGB))
def mat(n): return next((m for m in f.by_type("IfcMaterial") if m.Name==n),None) or f.create_entity("IfcMaterial",Name=n)
MAT=mat("Concreto Platibanda Cobertura")
def make_wall(p0,p1,st,off,elev):
    p0=np.asarray(p0,float);p1=np.asarray(p1,float);d=p1-p0;L=float(np.hypot(d[0],d[1]))
    if L<0.2:return None
    u=d/L;mid=(p0+p1)/2
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=L,YDim=THICK)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=H)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    lz=float(elev)-off[2]
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=st.ObjectPlacement,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([mid[0]-off[0],mid[1]-off[1],lz]),Axis=Dir([0,0,1]),RefDirection=Dir([u[0],u[1],0])))
    return f.create_entity("IfcWall",GlobalId=gid(),OwnerHistory=OWNER,Name="Platibanda-Cobertura-Apto",ObjectPlacement=pl,Representation=prod,PredefinedType="PARAPET")
tot=0
for bn,info in ST.items():
    bld=next(b for b in f.by_type("IfcBuilding") if b.Name==bn)
    isA=bn.startswith("Bloco-A"); seg=SEGA if isA else SEGB; elev=2.8 if isA else 5.6
    # reaproveita referencial do pavimento superior existente
    topname=next(s for s in info["storeys"] if s.endswith("Terreo")) if isA else next(s for s in info["storeys"] if s.endswith("Pav1"))
    top=next(s for s in f.by_type("IfcBuildingStorey") if s.Name==topname)
    # cria storey Cobertura com mesmo placement-pai do topo
    cov=f.create_entity("IfcBuildingStorey",GlobalId=gid(),OwnerHistory=OWNER,Name=f"{topname.split('-')[0]}-Cobertura",
        ObjectPlacement=f.create_entity("IfcLocalPlacement",PlacementRelTo=top.ObjectPlacement.PlacementRelTo,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0]))),
        CompositionType="ELEMENT",Elevation=float(elev))
    # agrega ao edificio
    agg=next((r for r in bld.IsDecomposedBy if r.is_a("IfcRelAggregates")),None)
    agg.RelatedObjects=list(agg.RelatedObjects)+[cov]
    off=soff(cov)
    mapped=map_to_footprint(seg,tuple(info["bbox"]),inset=0.2)
    walls=[w for w in (make_wall(m[:2],m[2:],cov,off,elev) for m in mapped) if w]
    f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=walls,RelatingStructure=cov)
    f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=walls,RelatingMaterial=MAT)
    tot+=len(walls)
print("Total platibandas:",tot)
f.write(OUT); print("escrito",OUT)
