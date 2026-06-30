#!/usr/bin/env python3
"""HVG Inhotim v118 — divisorias do SPA (DWG 13 - Bloco Spa, via LibreDWG)."""
import sys
import numpy as np, ifcopenshell, ifcopenshell.guid
sys.path.insert(0,"/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from detail_lib import wall_segments, map_to_footprint
SC="/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC="HVG_MASTER_v117_APARTAMENTOS.ifc"; OUT="HVG_MASTER_v118_SPA.ifc"
THICK=0.15; H=3.0; BB=(67.7,92.3,263.1,276.9)
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection",DirectionRatios=[float(x) for x in v])
st=next(s for s in f.by_type("IfcBuildingStorey") if s.Name=="SPA-Terreo")
off=np.zeros(3); p=st.ObjectPlacement
while p:
    rp=p.RelativePlacement
    if rp and rp.Location: off=off+np.array(rp.Location.Coordinates)
    p=p.PlacementRelTo
def make_wall(p0,p1):
    p0=np.asarray(p0,float);p1=np.asarray(p1,float);d=p1-p0;L=float(np.hypot(d[0],d[1]))
    if L<0.2: return None
    u=d/L;mid=(p0+p1)/2
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=L,YDim=THICK)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=H)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=st.ObjectPlacement,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([mid[0]-off[0],mid[1]-off[1],0.0-off[2]]),Axis=Dir([0,0,1]),RefDirection=Dir([u[0],u[1],0])))
    return f.create_entity("IfcWall",GlobalId=gid(),OwnerHistory=OWNER,Name="Parede-Divisoria-Alvenaria",ObjectPlacement=pl,Representation=prod,PredefinedType="PARTITIONING")
seg=wall_segments(f"{SC}/bld_spa.json",{"ALVENARIA","PAR1","PAR","SPA_ALVENARIA"})
mid=np.c_[(seg[:,0]+seg[:,2])/2,(seg[:,1]+seg[:,3])/2]
m=(mid[:,0]>298)&(mid[:,0]<338)&(mid[:,1]>-276)&(mid[:,1]<-242)
mapped=map_to_footprint(seg[m],BB,inset=0.3)
walls=[w for w in (make_wall(x[:2],x[2:]) for x in mapped) if w]
f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=walls,RelatingStructure=st)
mat=next((m for m in f.by_type("IfcMaterial") if m.Name=="Alvenaria Bloco Cerâmico Rebocado"),None) or f.create_entity("IfcMaterial",Name="Alvenaria Bloco Cerâmico Rebocado")
f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=walls,RelatingMaterial=mat)
f.write(OUT); print(f"SPA: {len(walls)} divisorias | escrito {OUT}")
