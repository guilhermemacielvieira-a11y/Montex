#!/usr/bin/env python3
"""HVG Inhotim v121 — portas dos demais edificios por deteccao de vaos.

Para cada edificio com divisorias (exceto o Bloco Principal, ja com portas),
agrupa as paredes-divisoria por linha (mesma direcao + mesma reta), ordena ao
longo da linha e detecta lacunas de 0,7-1,1 m (vaos de porta), inserindo uma
IfcDoor em cada vao.
"""
import numpy as np, ifcopenshell, ifcopenshell.guid, ifcopenshell.util.element as ue
from collections import defaultdict
SRC="HVG_MASTER_v120_SPA_AMBIENTES.ifc"; OUT="HVG_MASTER_v121_PORTAS_GERAIS.ifc"
DH=2.10
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection",DirectionRatios=[float(x) for x in v])
def bof(e):
    c=ue.get_container(e)
    while c and not c.is_a("IfcBuilding"):
        c=c.Decomposes[0].RelatingObject if c.Decomposes else None
    return c.Name if c else "?"
def soff(st):
    o=np.zeros(3);p=st.ObjectPlacement
    while p:
        rp=p.RelativePlacement
        if rp and rp.Location:o=o+np.array(rp.Location.Coordinates)
        p=p.PlacementRelTo
    return o
def wall_info(w):
    rp=w.ObjectPlacement.RelativePlacement; loc=np.array(rp.Location.Coordinates)
    u=np.array(rp.RefDirection.DirectionRatios[:2]) if rp.RefDirection else np.array([1.,0])
    u=u/(np.linalg.norm(u) or 1); L=w.Representation.Representations[0].Items[0].SweptArea.XDim
    M=loc[:2]  # local (relativo ao storey); usamos local consistente por storey
    return M,u,float(L),loc[2]
def make_door(stp, M, u, t, w, base_z, st):
    # placement relativo ao storey, posicao M + t*u (coords locais do storey)
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=float(w),YDim=0.05)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=DH-0.05)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    loc=M+t*u
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=stp,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([loc[0],loc[1],base_z]),Axis=Dir([0,0,1]),RefDirection=Dir([u[0],u[1],0])))
    return f.create_entity("IfcDoor",GlobalId=gid(),OwnerHistory=OWNER,Name=f"Porta-{w:.2f}x{DH:.2f}",ObjectPlacement=pl,Representation=prod,OverallHeight=DH,OverallWidth=float(w),PredefinedType="DOOR",OperationType="SINGLE_SWING_LEFT")

# agrupa paredes-divisoria por (storey, linha) e detecta vaos
walls=[w for w in f.by_type("IfcWall") if (w.Name or "").startswith("Parede-Divisoria") and bof(w)!="Bloco Principal"]
bystorey=defaultdict(list)
for w in walls:
    st=ue.get_container(w)
    if st and st.is_a("IfcBuildingStorey"): bystorey[st].append(w)
tot=0
for st,ws in bystorey.items():
    stp=st.ObjectPlacement
    lines=defaultdict(list)
    for w in ws:
        M,u,L,bz=wall_info(w)
        ang=round(np.degrees(np.arctan2(u[1],u[0]))%180,0)
        # distancia perpendicular da reta a origem (no frame local)
        n=np.array([-u[1],u[0]]); perp=round(float(np.dot(M,n)),1)
        lines[(ang,perp,round(bz,1))].append((float(np.dot(M,u)),L,M,u,bz))
    doors=[]
    for key,segs in lines.items():
        if len(segs)<2: continue
        segs.sort(key=lambda s: s[0])
        # intervalos ocupados [t-L/2, t+L/2]
        iv=[(t-L/2,t+L/2,M,u,bz) for t,L,M,u,bz in segs]
        for i in range(len(iv)-1):
            gap=iv[i+1][0]-iv[i][1]
            if 0.65<=gap<=1.15:
                tc=(iv[i][1]+iv[i+1][0])/2
                M0,u0,bz0=iv[i][2],iv[i][3],iv[i][4]
                # posicao do centro do vao ao longo de u, a partir de M0
                t_along=tc-np.dot(M0,u0)
                doors.append(make_door(stp,M0,u0,t_along,min(gap,0.9),bz0,st))
    if doors:
        f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=doors,RelatingStructure=st)
        tot+=len(doors)
print("portas inseridas (vaos):",tot)
f.write(OUT); print("escrito",OUT)
