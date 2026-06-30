#!/usr/bin/env python3
"""HVG Inhotim v122 — demais pavimentos dos apartamentos (subsolos / 1o pav).

Extrai por quadrante as plantas Par1 dos DWG 07/08 (1o/2o sub-solo do A;
sub-solo e 1o pavimento do B) e replica nos 16 blocos, nos storeys
correspondentes (paredes no piso de cada pavimento)."""
import sys, json
import numpy as np, ifcopenshell, ifcopenshell.guid
sys.path.insert(0,"/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from detail_lib import wall_segments, map_to_footprint
SC="/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC="HVG_MASTER_v121_PORTAS_GERAIS.ifc"; OUT="HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc"
THICK=0.13; H=2.8
ST=json.load(open(f"{SC}/apt_storeys.json"))
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection",DirectionRatios=[float(x) for x in v])
def soffxy(st):
    o=np.zeros(3);p=st.ObjectPlacement
    while p:
        rp=p.RelativePlacement
        if rp and rp.Location:o=o+np.array(rp.Location.Coordinates)
        p=p.PlacementRelTo
    return o
def quad(jf, xlo,xhi,ylo,yhi):
    seg=wall_segments(f"{SC}/{jf}",{"Par1"})
    mid=np.c_[(seg[:,0]+seg[:,2])/2,(seg[:,1]+seg[:,3])/2]
    m=(mid[:,0]>xlo)&(mid[:,0]<xhi)&(mid[:,1]>ylo)&(mid[:,1]<yhi)
    return seg[m]
# quadrantes (aptA: split X3494 Y1395; aptB: split X3505 Y1397)
SEG={
 "A_SubSolo1": quad("bld_aptA.json",3450,3494,1370,1395),
 "A_SubSolo2": quad("bld_aptA.json",3450,3494,1395,1421),
 "B_SubSolo":  quad("bld_aptB.json",3455,3505,1368,1397),
 "B_Pav1":     quad("bld_aptB.json",3455,3505,1397,1423),
}
for k,v in SEG.items(): print(k,len(v),"segs")
def make_wall(p0,p1,st,off):
    p0=np.asarray(p0,float);p1=np.asarray(p1,float);d=p1-p0;L=float(np.hypot(d[0],d[1]))
    if L<0.2:return None
    u=d/L;mid=(p0+p1)/2
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=L,YDim=THICK)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=H)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    lz=float(st.Elevation or 0.0)-off[2]
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=st.ObjectPlacement,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([mid[0]-off[0],mid[1]-off[1],lz]),Axis=Dir([0,0,1]),RefDirection=Dir([u[0],u[1],0])))
    return f.create_entity("IfcWall",GlobalId=gid(),OwnerHistory=OWNER,Name="Parede-Divisoria-Apto",ObjectPlacement=pl,Representation=prod,PredefinedType="PARTITIONING")
def mat(n): return next((m for m in f.by_type("IfcMaterial") if m.Name==n),None) or f.create_entity("IfcMaterial",Name=n)
M=mat("Alvenaria Bloco Cerâmico Rebocado (Apto)")
tot=0
for bn,info in ST.items():
    bb=tuple(info["bbox"])
    if bn.startswith("Bloco-A"):
        plan={"SubSolo1":SEG["A_SubSolo1"],"SubSolo2":SEG["A_SubSolo2"]}
    else:
        plan={"SubSolo":SEG["B_SubSolo"],"Pav1":SEG["B_Pav1"]}
    for suffix,seg in plan.items():
        if not len(seg): continue
        stn=next((s for s in info["storeys"] if s.endswith(suffix)),None)
        if not stn: continue
        st=next(s for s in f.by_type("IfcBuildingStorey") if s.Name==stn); off=soffxy(st)
        mapped=map_to_footprint(seg,bb,inset=0.3)
        walls=[w for w in (make_wall(m[:2],m[2:],st,off) for m in mapped) if w]
        f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=walls,RelatingStructure=st)
        f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=walls,RelatingMaterial=M)
        tot+=len(walls)
print("Total divisorias (subsolos/pav):",tot)
f.write(OUT); print("escrito",OUT)
