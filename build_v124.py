#!/usr/bin/env python3
"""HVG Inhotim v124 — Bar da Piscina (Bar Molhado) junto a piscina de ondas.

As piscinas exteriores ja estavam modeladas (IfcCovering: agua, borda, raias,
skimmer, deck). O DWG '14 - Piscinas exteriores' destaca o BAR MOLHADO, ausente
no modelo. Esta revisao adiciona o bar (balcao + cobertura de sombra) junto a
Piscina de Ondas (X[50,90] Y[172.5,187.5])."""
import numpy as np, ifcopenshell, ifcopenshell.guid
SRC="HVG_MASTER_v123_APTOS_COBERTURA.ifc"; OUT="HVG_MASTER_v124_BAR_PISCINA.ifc"
f=ifcopenshell.open(SRC); OWNER=f.by_type("IfcOwnerHistory")[0]
CTX=next(c for c in f.by_type("IfcGeometricRepresentationContext") if c.ContextType=="Model")
SITE=f.by_type("IfcSite")[0]; RELTO=SITE.ObjectPlacement
def gid(): return ifcopenshell.guid.new()
def Pt(v): return f.create_entity("IfcCartesianPoint",Coordinates=[float(x) for x in v])
def Dir(v): return f.create_entity("IfcDirection",DirectionRatios=[float(x) for x in v])
def mat(n): return next((m for m in f.by_type("IfcMaterial") if m.Name==n),None) or f.create_entity("IfcMaterial",Name=n)
def box(cls,name,cx,cy,bz,dx,dy,dz,ptype=None):
    prof=f.create_entity("IfcRectangleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),XDim=dx,YDim=dy)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=dz)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=RELTO,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([cx,cy,bz-dz/2 if dz<0.5 else bz])))
    kw=dict(GlobalId=gid(),OwnerHistory=OWNER,Name=name,ObjectPlacement=pl,Representation=prod)
    if ptype is not None: kw["PredefinedType"]=ptype
    return f.create_entity(cls,**kw)
def cyl(name,cx,cy,bz,h,r,cls="IfcColumn",ptype=None):
    prof=f.create_entity("IfcCircleProfileDef",ProfileType="AREA",Position=f.create_entity("IfcAxis2Placement2D",Location=Pt([0,0])),Radius=r)
    solid=f.create_entity("IfcExtrudedAreaSolid",SweptArea=prof,Position=f.create_entity("IfcAxis2Placement3D",Location=Pt([0,0,0])),ExtrudedDirection=Dir([0,0,1]),Depth=h)
    shape=f.create_entity("IfcShapeRepresentation",ContextOfItems=CTX,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])
    prod=f.create_entity("IfcProductDefinitionShape",Representations=[shape])
    pl=f.create_entity("IfcLocalPlacement",PlacementRelTo=RELTO,RelativePlacement=f.create_entity("IfcAxis2Placement3D",Location=Pt([cx,cy,bz])))
    kw=dict(GlobalId=gid(),OwnerHistory=OWNER,Name=name,ObjectPlacement=pl,Representation=prod)
    if ptype is not None: kw["PredefinedType"]=ptype
    return f.create_entity(cls,**kw)
# Bar da Piscina junto a borda leste da piscina de ondas (deck z~3.2)
BZ=3.20; els=[]
# balcao em L
els.append(box("IfcFurniture","Bar-Piscina-Balcao",92.0,180.0,BZ,4.5,1.0,1.1))
els.append(box("IfcFurniture","Bar-Piscina-Balcao",94.2,177.5,BZ,1.0,4.0,1.1))
# 4 banquetas
for i,yy in enumerate([178.0,179.0,181.0,182.0]):
    els.append(cyl(f"Bar-Piscina-Banqueta-{i+1}",90.6,yy,BZ,0.75,0.18,"IfcFurniture"))
f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=els,RelatingStructure=SITE)
f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=els,RelatingMaterial=mat("Mobiliario Bar Piscina"))
# cobertura de sombra (pergola) sobre o bar
posts=[cyl("Bar-Piscina-Pilar-Sombra",x,y,BZ,2.6,0.08,"IfcColumn") for x,y in [(90.5,177),(96,177),(90.5,184),(96,184)]]
roof=box("IfcRoof","Bar-Piscina-Cobertura-Sombra",93.25,180.5,BZ+2.6,6.5,8.0,0.15,"FLAT_ROOF")
f.create_entity("IfcRelContainedInSpatialStructure",GlobalId=gid(),OwnerHistory=OWNER,RelatedElements=posts+[roof],RelatingStructure=SITE)
f.create_entity("IfcRelAssociatesMaterial",GlobalId=gid(),OwnerHistory=OWNER,RelatedObjects=posts+[roof],RelatingMaterial=mat("Madeira Pergola Bar Piscina"))
print("Bar da Piscina:",len(els),"mobiliario +",len(posts),"pilares + cobertura")
f.write(OUT); print("escrito",OUT)
