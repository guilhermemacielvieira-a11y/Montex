#!/usr/bin/env python3
"""HVG v91 -> v92: REMOVE guarda-corpos fragilizados (extrudes de circulo com eixo rotacionado,
causa de render errado) e RECONSTROI guarda-corpos de vidro robustos (caixas axis-aligned)
em TODAS as varandas, com posicao derivada do placement (sem depender da malha)."""
import ifcopenshell, ifcopenshell.util.placement as Pl, numpy as np
import ifcopenshell.util.element as E
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
ctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier=="Body"][0]
def g(): return ifcopenshell.guid.new()
def find_mat(n):
    for mt in m.by_type("IfcMaterial"):
        if mt.Name==n: return mt
    return m.create_entity("IfcMaterial",n)
vidro=find_mat("Vidro Laminado 8mm")

def rect_fp(sp):
    M=Pl.get_local_placement(sp.ObjectPlacement); it=None
    for r in sp.Representation.Representations:
        for x in r.Items:
            if x.is_a("IfcExtrudedAreaSolid") and x.SweptArea.is_a("IfcRectangleProfileDef"): it=x;break
    if not it: return None
    p=it.SweptArea; hx=p.XDim/2; hy=p.YDim/2
    loc=list(it.Position.Location.Coordinates); loc=(loc+[0,0,0])[:3]
    cs=[]
    for sx in(-hx,hx):
        for sy in(-hy,hy):
            w=M@np.array([loc[0]+sx,loc[1]+sy,loc[2],1.0]); cs.append(w[:3])
    c=np.array(cs); return [c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max(),float(M[2,3])]

# 1) REMOVER railings de varanda problematicos
old=[e for e in m.by_type("IfcRailing") if "Varanda" in (e.Name or "")]
def purge(el):
    for r in list(el.ContainedInStructure): r.RelatedElements=[x for x in r.RelatedElements if x!=el]
    for rel in list(m.get_inverse(el)):
        if rel.is_a() in ("IfcRelAssociatesMaterial","IfcRelContainedInSpatialStructure","IfcRelAggregates"):
            try: rel.RelatedObjects=[x for x in rel.RelatedObjects if x!=el]
            except: 
                try: rel.RelatedElements=[x for x in rel.RelatedElements if x!=el]
                except: pass
    pds=el.Representation
    m.remove(el)
    if pds:
        for rep in pds.Representations:
            for it in list(rep.Items):
                for si in [x for x in m.get_inverse(it) if x.is_a("IfcStyledItem")]: m.remove(si)
                try: m.remove(it)
                except: pass
            try: m.remove(rep)
            except: pass
        try: m.remove(pds)
        except: pass
for e in old: purge(e)
print("Railings de varanda removidos:",len(old))

# 2) RECONSTRUIR guarda-corpos robustos por pavimento
def glass_style():
    col=m.create_entity("IfcColourRgb",None,0.55,0.78,0.9)
    rend=m.create_entity("IfcSurfaceStyleRendering",col,0.45,None,None,None,None,None,None,"NOTDEFINED")
    return m.create_entity("IfcPresentationStyleAssignment",[m.create_entity("IfcSurfaceStyle",None,"BOTH",[rend])])
def vbox(cx,cy,zb,w,d,h):
    pr=m.create_entity("IfcRectangleProfileDef","AREA",None,m.create_entity("IfcAxis2Placement2D",m.create_entity("IfcCartesianPoint",[0.,0.]),None),float(w),float(d))
    pos=m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[float(cx),float(cy),float(zb)]),m.create_entity("IfcDirection",[0.,0.,1.]),m.create_entity("IfcDirection",[1.,0.,0.]))
    return m.create_entity("IfcExtrudedAreaSolid",pr,pos,m.create_entity("IfcDirection",[0.,0.,1.]),float(h))
def contain(el,st):
    rel=next((r for r in st.ContainsElements),None)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+[el]
    else: m.create_entity("IfcRelContainedInSpatialStructure",g(),oh,None,None,[el],st)

created=0
for b in m.by_type("IfcBuilding"):
    if not (b.Name.startswith("Bloco-A") or b.Name.startswith("Bloco-B")): continue
    for st in [x for x in m.by_type("IfcBuildingStorey") if E.get_aggregate(x)==b]:
        vars=[sp for sp in m.by_type("IfcSpace") if E.get_aggregate(sp)==st and (sp.Name or "").startswith("VAR")]
        apts=[sp for sp in m.by_type("IfcSpace") if E.get_aggregate(sp)==st and (sp.Name or "").startswith("APT")]
        if not vars: continue
        vf=[rect_fp(sp) for sp in vars]; vf=[x for x in vf if x]
        if not vf: continue
        vf=np.array(vf)
        xmn,xmx=vf[:,0].min(),vf[:,1].max(); ymn,ymx=vf[:,2].min(),vf[:,3].max(); pz=vf[0,4]
        # lado externo: oposto ao centroide dos aptos
        if apts:
            af=[rect_fp(sp) for sp in apts]; af=np.array([x for x in af if x]); acy=(af[:,2].min()+af[:,3].min())/2
        else: acy=ymx+5
        vcy=(ymn+ymx)/2
        outerY = ymn if vcy<acy else ymx
        ycen=outerY + (0.03 if vcy<acy else -0.03)
        painel=vbox((xmn+xmx)/2,ycen,pz+0.05,xmx-xmn,0.04,1.05)
        corr=vbox((xmn+xmx)/2,ycen,pz+1.10,xmx-xmn,0.08,0.05)
        sa=glass_style()
        for sol in (painel,corr): m.create_entity("IfcStyledItem",sol,[sa],None)
        rep=m.create_entity("IfcProductDefinitionShape",None,None,[m.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",[painel,corr])])
        plc=m.create_entity("IfcLocalPlacement",None,m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[0.,0.,0.]),None,None))
        nr=m.create_entity("IfcRailing",g(),oh,f"GuardaCorpo-Varanda-{st.Name}","Guarda-corpo de vidro h=1.10m (NBR 14718)",None,plc,rep,None,"GUARDRAIL")
        m.create_entity("IfcRelAssociatesMaterial",g(),oh,None,None,[nr],vidro)
        contain(nr,st); created+=1
print("Guarda-corpos robustos criados:",created)
proj=m.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+(" | v92 ALINHAMENTO/RENDER: removidos %d guarda-corpos com geometria fragil (extrude de circulo eixo-rotacionado) e reconstruidos %d guarda-corpos de vidro robustos (caixas axis-aligned) em todas as varandas, contidos no pavimento e com material."%(len(old),created))
m.write("HVG_MASTER_v92_alinhado.ifc")
print("Gravado: HVG_MASTER_v92_alinhado.ifc")
