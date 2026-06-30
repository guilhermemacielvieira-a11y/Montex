#!/usr/bin/env python3
"""HVG Inhotim v119 — divisorias dos edificios menores (Boite, Clube NEP,
Guarita, Apoio Quadras, Subestacao) a partir dos DWG oficiais."""
import sys, json
import numpy as np, ifcopenshell, ifcopenshell.guid
sys.path.insert(0,"/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad")
from detail_lib import wall_segments, map_to_footprint
SC="/tmp/claude-0/-home-user-Montex/df3589ab-af83-5be6-bd5e-2ba82fe33b91/scratchpad"
SRC="HVG_MASTER_v118_SPA.ifc"; OUT="HVG_MASTER_v119_MENORES.ifc"; THICK=0.13
BL=json.load(open(f"{SC}/small_blocks.json"))
CONF=[
 ("Boite Soul & Blues", "bld_boite.json", {"PAR","PAR1"}, 3.0),
 ("Clube NEP",          "bld_clube.json", {"Par1"},       3.0),
 ("Guarita",            "bld_guarita.json", {"PAR1"},     3.0),
 ("Apoio Quadras",      "bld_quadras.json", {"Alvenaria","PAR1","PAR"}, 3.0),
 ("Subestacao",         "bld_subest.json", {"ALVENARIA","PAREDES"}, 3.5),
]
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
def mat(n): return next((m for m in f.by_type("IfcMaterial") if m.Name==n),None) or f.create_entity("IfcMaterial",Name=n)
def densest(seg, wx, wy):
    """Mantem segmentos no cluster mais denso (janela do tamanho do footprint)."""
    mid=np.c_[(seg[:,0]+seg[:,2])/2,(seg[:,1]+seg[:,3])/2]
    # bin grande ~ tamanho do edificio
    bx=max(wx,wy)*1.3
    keys=np.floor(mid/bx).astype(int)
    from collections import Counter
    cc=Counter(map(tuple,keys))
    bk=max(cc,key=cc.get)
    cen=(np.array(bk)+0.5)*bx
    m=(np.abs(mid[:,0]-cen[0])<bx)&(np.abs(mid[:,1]-cen[1])<bx)
    return seg[m]
def make_wall(p0,p1,st,off,h):
    p0=np.asarray(p0,float);p1=np.asarray(p1,float);d=p1-p0;L=float(np.hypot(d[0],d[1]))
    if L<0.2:return None
    u=d/L;mid=(p0+p1)/2
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=L,YDim=THICK)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=h)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=st.ObjectPlacement,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([mid[0]-off[0],mid[1]-off[1],0.0-off[2]]),Axis=Dir([0,0,1]),RefDirection=Dir([u[0],u[1],0])))
    return f.create_entity("IfcWall",GlobalId=gid(),OwnerHistory=OWNER,Name="Parede-Divisoria-Alvenaria",ObjectPlacement=pl,Representation=prod,PredefinedType="PARTITIONING")
tot=0
for B,jf,lays,h in CONF:
    if B not in BL: print("sem footprint:",B); continue
    bb=tuple(BL[B]["bbox"]); st=next(s for s in f.by_type("IfcBuildingStorey") if s.Name==BL[B]["storey"]); off=soff(st)
    seg=wall_segments(f"{SC}/{jf}",lays)
    if not len(seg): print(B,"sem paredes"); continue
    seg=densest(seg, bb[1]-bb[0], bb[3]-bb[2])
    mapped=map_to_footprint(seg,bb,inset=0.25)
    walls=[w for w in (make_wall(m[:2],m[2:],st,off,h) for m in mapped) if w]
    f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=walls,RelatingStructure=st)
    f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=walls,RelatingMaterial=mat("Alvenaria Bloco Cerâmico Rebocado"))
    tot+=len(walls); print(f"{B}: {len(walls)} divisorias")
f.write(OUT); print("Total:",tot,"| escrito",OUT)
