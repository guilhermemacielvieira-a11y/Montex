#!/usr/bin/env python3
"""HVG Inhotim v120 — ambientes (IfcSpace) do SPA, da planta oficial."""
import sys, re
import numpy as np, ifcopenshell, ifcopenshell.guid
sys.path.insert(0,"/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from detail_lib import wall_segments, make_transform
from load_dwgjson import load
SC="/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC="HVG_MASTER_v119_MENORES.ifc"; OUT="HVG_MASTER_v120_SPA_AMBIENTES.ifc"
BB=(67.7,92.3,263.1,276.9); H=3.0
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
st=next(s for s in f.by_type("IfcBuildingStorey") if s.Name=="SPA-Terreo")
off=np.zeros(3);p=st.ObjectPlacement
while p:
    rp=p.RelativePlacement
    if rp and rp.Location: off=off+np.array(rp.Location.Coordinates)
    p=p.PlacementRelTo
# transform from SPA wall cluster (same as v118)
seg=wall_segments(f"{SC}/bld_spa.json",{"ALVENARIA","PAR1","PAR","SPA_ALVENARIA"})
mid=np.c_[(seg[:,0]+seg[:,2])/2,(seg[:,1]+seg[:,3])/2]
m=(mid[:,0]>298)&(mid[:,0]<338)&(mid[:,1]>-276)&(mid[:,1]<-242)
tf=make_transform(seg[m],BB,inset=0.3)
# rooms: pair area labels with nearest name label
d=load(f"{SC}/bld_spa.json");objs=d["OBJECTS"]
A=[];N=[]
for o in objs:
    if o.get("entity") in ("TEXT","MTEXT"):
        tv=(o.get("text_value") or o.get("text") or "")
        tv=re.sub(r'\\[A-Za-z][^;]*;','',tv).replace('{','').replace('}','').replace('\\P',' ').strip()
        ip=o.get("ins_pt")
        if not(ip and 298<ip[0]<338 and -276<ip[1]<-242): continue
        ma=re.search(r'A\s*=\s*([\d.,]+)\s*m',tv)
        if ma: A.append((float(ma.group(1).replace(',','.')),ip[0],ip[1]))
        elif re.search(r'[A-Za-zÀ-ÿ]{4,}',tv) and not re.search(r'planta|escala|fach|acabam|granito|porcel|nivel|pavimento',tv,re.I):
            N.append((tv[:24],ip[0],ip[1]))
def make_space(name,area,wx,wy):
    side=float(np.clip(np.sqrt(area),1.5,8.0))
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=side,YDim=side)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=f.create_entity("IfcDirection",DirectionRatios=[0.,0.,1.]),Depth=H)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=st.ObjectPlacement,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([wx-off[0],wy-off[1],0.0-off[2]])))
    sp=f.create_entity("IfcSpace",GlobalId=gid(),OwnerHistory=OWNER,Name=f"SPA-{name[:16]}",LongName=name,ObjectPlacement=pl,Representation=prod,CompositionType="ELEMENT",PredefinedType="INTERNAL")
    q=f.create_entity("IfcQuantityArea",Name="GrossFloorArea",AreaValue=float(area))
    eq=f.create_entity("IfcElementQuantity",GlobalId=gid(),OwnerHistory=OWNER,Name="Qto_SpaceBaseQuantities",Quantities=[q])
    f.create_entity("IfcRelDefinesByProperties",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=[sp],RelatingPropertyDefinition=eq)
    return sp
# remove existing generic SPA spaces
import ifcopenshell.api
for sp in list(f.by_type("IfcSpace")):
    par=sp.Decomposes[0].RelatingObject if sp.Decomposes else None
    if par and par.Name=="SPA-Terreo":
        ifcopenshell.api.run("root.remove_product",f,product=sp)
spaces=[]
for area,ax,ay in A:
    # nearest name
    nm="Ambiente"
    if N:
        dn=min(N,key=lambda n:(n[1]-ax)**2+(n[2]-ay)**2); 
        if (dn[1]-ax)**2+(dn[2]-ay)**2 < 16: nm=dn[0]
    w=tf([ax,ay]); spaces.append(make_space(nm,area,w[0],w[1]))
f.create_entity("IfcRelAggregates",GlobalId=gid(),OwnerHistory=OWNER,RelatingObject=st,RelatedObjects=spaces)
f.write(OUT); print(f"SPA: {len(spaces)} ambientes (areas) | escrito {OUT}")
