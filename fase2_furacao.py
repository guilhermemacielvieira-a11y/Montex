#!/usr/bin/env python3
"""Fase 2 - parte 4: furacao de prumadas MEP em lajes de piso (IfcOpeningElement + IfcRelVoidsElement)."""
import ifcopenshell, ifcopenshell.geom as geom, ifcopenshell.util.placement as P
import numpy as np, multiprocessing, csv
m=ifcopenshell.open("HVG_MASTER_v88_Arq_MEP_executivo.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
ctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier=="Body"]
ctx=ctx[0] if ctx else m.by_type("IfcGeometricRepresentationContext")[0]
def newg(): return ifcopenshell.guid.new()
def mat_of(el):
    for r in el.HasAssociations:
        if r.is_a("IfcRelAssociatesMaterial"):
            return getattr(r.RelatingMaterial,'Name',None)
def sysn(el):
    for r in (el.HasAssignments or []):
        if r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup.is_a("IfcDistributionSystem"):
            return r.RelatingGroup.Name

# lajes de piso estruturais
floor=set()
for sl in m.by_type("IfcSlab"):
    st=sl.ContainedInStructure
    if st and st[0].RelatingStructure.is_a("IfcBuildingStorey"):
        mt=(mat_of(sl) or "")
        if "Steel Deck" in mt or "Concreto Armado" in mt: floor.add(sl.id())

s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
box={}
want=set(["IfcPipeSegment","IfcDuctSegment","IfcCableSegment","IfcSlab"])
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        if el.is_a() in want:
            v=np.array(sh.geometry.verts).reshape(-1,3)
            if len(v): box[sh.id]=(el.is_a(),v.min(0),v.max(0))
        if not it.next(): break
slabs=[(i,b) for i,b in box.items() if b[0]=="IfcSlab" and i in floor]
meps=[(i,b) for i,b in box.items() if b[0]!="IfcSlab"]

pens=[]
for mi,mb in meps:
    sz=mb[2]-mb[1]
    if max(sz[0],sz[1])>0.6: continue   # exclui mains horizontais
    rsize=max(sz[0],sz[1])
    for si,sb in slabs:
        if mb[1][0]<sb[2][0] and sb[1][0]<mb[2][0] and mb[1][1]<sb[2][1] and sb[1][1]<mb[2][1]:
            z0,z1=sb[1][2],sb[2][2]
            if mb[1][2]<z0-0.02 and mb[2][2]>z1+0.02:
                cx=(max(mb[1][0],sb[1][0])+min(mb[2][0],sb[2][0]))/2
                cy=(max(mb[1][1],sb[1][1])+min(mb[2][1],sb[2][1]))/2
                pens.append((mi,si,float(cx),float(cy),float(z0),float(z1),float(rsize)))

# dedupe por (mep,slab)
seen=set(); P2=[]
for p in pens:
    k=(p[0],p[1])
    if k in seen: continue
    seen.add(k); P2.append(p)
print("Furos a modelar:", len(P2))

def make_opening(slab, cx,cy,z0,z1,sleeve):
    M=P.get_local_placement(slab.ObjectPlacement); Minv=np.linalg.inv(M)
    bottom=Minv@np.array([cx,cy,z0-0.05,1.0]); 
    depth=float((z1-z0)+0.10)
    lx,ly,lz=float(bottom[0]),float(bottom[1]),float(bottom[2])
    prof=m.create_entity("IfcRectangleProfileDef","AREA",None,
        m.create_entity("IfcAxis2Placement2D",m.create_entity("IfcCartesianPoint",[0.,0.]),None),
        float(sleeve),float(sleeve))
    pos=m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[lx,ly,lz]),
        m.create_entity("IfcDirection",[0.,0.,1.]),m.create_entity("IfcDirection",[1.,0.,0.]))
    solid=m.create_entity("IfcExtrudedAreaSolid",prof,pos,
        m.create_entity("IfcDirection",[0.,0.,1.]),depth)
    shp=m.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",[solid])
    pds=m.create_entity("IfcProductDefinitionShape",None,None,[shp])
    plc=m.create_entity("IfcLocalPlacement",slab.ObjectPlacement,
        m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[0.,0.,0.]),None,None))
    op=m.create_entity("IfcOpeningElement",newg(),oh,"Furo-Prumada",
        "Passagem MEP em laje (sleeve)",None,plc,pds,None,"OPENING")
    m.create_entity("IfcRelVoidsElement",newg(),oh,None,None,slab,op)
    return op

reg=[]
for mi,si,cx,cy,z0,z1,rsize in P2:
    slab=m.by_id(si); mep=m.by_id(mi)
    sleeve=round(max(rsize+0.10,0.10),3)
    make_opening(slab,cx,cy,z0,z1,sleeve)
    reg.append([mep.is_a(),mep.Name,sysn(mep) or "-",slab.Name,
                round(cx,2),round(cy,2),round((z0+z1)/2,2),round(rsize,3),sleeve])
print("Furos criados:", len(reg), "| IfcOpeningElement total:", len(m.by_type("IfcOpeningElement")))

with open("HVG_v88_Registro_Furacao.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(["Tipo_MEP","Prumada","Sistema","Laje_Hospedeira","X","Y","Z","Diam_Tubo_m","Sleeve_m"])
    w.writerows(sorted(reg,key=lambda r:(r[3],r[4],r[5])))

proj=m.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+(
    " | v88 EXECUTIVO: materiais consolidados, IfcGrid de eixos (Bloco Principal), "
    "2 clashes eletrocalha x estrada resolvidos e %d furos de prumada (IfcOpeningElement+IfcRelVoidsElement) "
    "modelados em lajes de piso."%len(reg))
m.write("HVG_MASTER_v88_Arq_MEP_executivo.ifc")
print("Gravado v88 final.")
