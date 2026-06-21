#!/usr/bin/env python3
"""Adiciona janelas (com aberturas) a Clube NEP e Guarita (0 janelas - deficiencia)."""
import ifcopenshell, ifcopenshell.util.placement as Pl, numpy as np
import ifcopenshell.util.element as E
m=ifcopenshell.open("HVG_MASTER_v92_alinhado.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
ctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier=="Body"][0]
def g(): return ifcopenshell.guid.new()
def find_mat(n):
    for mt in m.by_type("IfcMaterial"):
        if mt.Name==n: return mt
    return m.create_entity("IfcMaterial",n)
vidro=find_mat("Vidro Laminado 8mm"); alum=find_mat("Esquadria Aluminio Branco")
def style(rgb,t=0.4):
    col=m.create_entity("IfcColourRgb",None,*[float(c) for c in rgb])
    r=m.create_entity("IfcSurfaceStyleRendering",col,t,None,None,None,None,None,None,"NOTDEFINED")
    return m.create_entity("IfcPresentationStyleAssignment",[m.create_entity("IfcSurfaceStyle",None,"BOTH",[r])])
def box(cx,cy,zb,w,d,h,rgb):
    pr=m.create_entity("IfcRectangleProfileDef","AREA",None,m.create_entity("IfcAxis2Placement2D",m.create_entity("IfcCartesianPoint",[0.,0.]),None),float(w),float(d))
    pos=m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[float(cx),float(cy),float(zb)]),None,None)
    sol=m.create_entity("IfcExtrudedAreaSolid",pr,pos,m.create_entity("IfcDirection",[0.,0.,1.]),float(h))
    m.create_entity("IfcStyledItem",sol,[style(rgb)],None)
    return sol
def shape(sol):
    return m.create_entity("IfcProductDefinitionShape",None,None,[m.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",[sol])])
def idplc(): return m.create_entity("IfcLocalPlacement",None,m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[0.,0.,0.]),None,None))
def contain(el,st):
    rel=next((r for r in st.ContainsElements),None)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+[el]
    else: m.create_entity("IfcRelContainedInSpatialStructure",g(),oh,None,None,[el],st)
def wall_world(w):
    M=Pl.get_local_placement(w.ObjectPlacement); it=[x for r in w.Representation.Representations for x in r.Items if x.is_a("IfcExtrudedAreaSolid")][0]
    p=it.SweptArea; loc=list(it.Position.Location.Coordinates); loc=(loc+[0,0,0])[:3]
    w0=M@np.array([loc[0],loc[1],loc[2],1.0]); return float(w0[0]),float(w0[1]),float(w0[2]),p.XDim,p.YDim,float(it.Depth)

def add_window(name,st,host,cx,cy,zb,ww,dd,hh):
    # abertura voida a parede
    op_sol=box(cx,cy,zb-0.02,ww+0.02,dd+0.06,hh+0.04,(0.5,0.5,0.5))
    op=m.create_entity("IfcOpeningElement",g(),oh,"Abertura-Janela",None,None,idplc(),shape(op_sol),None,"OPENING")
    m.create_entity("IfcRelVoidsElement",g(),oh,None,None,host,op)
    # janela (vidro)
    wsol=box(cx,cy,zb,ww,dd,hh,(0.55,0.78,0.9))
    win=m.create_entity("IfcWindow",g(),oh,name,"Janela aluminio+vidro",None,idplc(),shape(wsol),None,hh,ww,"WINDOW",None,None)
    m.create_entity("IfcRelFillsElement",g(),oh,None,None,op,win)
    m.create_entity("IfcRelAssociatesMaterial",g(),oh,None,None,[win],vidro)
    # Qto
    qa=m.create_entity("IfcQuantityArea","Area",None,None,float(ww*hh),None)
    m.create_entity("IfcRelDefinesByProperties",g(),oh,None,None,[win],m.create_entity("IfcElementQuantity",g(),oh,"Qto_WindowBaseQuantities",None,None,[qa]))
    contain(win,st); return win

count=0
plans={
 "Clube NEP":[("sul",3),("norte",3)],
 "Guarita":[("todas",1)],
}
for bn in ("Clube NEP","Guarita"):
    b=[x for x in m.by_type("IfcBuilding") if x.Name==bn][0]
    st=[x for x in m.by_type("IfcBuildingStorey") if E.get_aggregate(x)==b][0]
    zf=Pl.get_local_placement(st.ObjectPlacement)[2,3]
    walls=[e for r in st.ContainsElements for e in r.RelatedElements if e.is_a()=="IfcWall"]
    wi=[(w,)+wall_world(w) for w in walls]
    for w,cx,cy,cz,XD,YD,H in wi:
        horiz = XD>YD  # parede correndo em X
        L = XD if horiz else YD; n = 3 if (bn=="Clube NEP" and L>10) else (2 if L>6 else 1)
        for k in range(n):
            t=(k+1)/(n+1)
            if horiz:
                jx=cx-XD/2+t*XD; jy=cy; ww,dd=1.4,YD+0.02
            else:
                jx=cx; jy=cy-YD/2+t*YD; ww,dd=XD+0.02,1.4
            add_window(f"Janela-{bn}-{w.Name[-6:]}-{k+1}",st,w,jx,jy,zf+1.0,ww,dd,1.2); count+=1
print("Janelas adicionadas:",count)
# validar
for bn in ("Clube NEP","Guarita"):
    b=[x for x in m.by_type("IfcBuilding") if x.Name==bn][0]
    w=sum(1 for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==b for r in st.ContainsElements for e in r.RelatedElements if e.is_a()=="IfcWindow")
    print(f"  {bn}: {w} janelas agora")
proj=m.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+(" | v92.2: %d janelas (aluminio+vidro, com aberturas) adicionadas ao Clube NEP e Guarita (estavam sem janelas - deficiencia de iluminacao/ventilacao natural)."%count)
m.write("HVG_MASTER_v92_alinhado.ifc")
print("v92 atualizado.")
