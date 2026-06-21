#!/usr/bin/env python3
"""HVG Fase 2 (v87 -> v88): compatibilizacao executiva.
 1) Consolida IfcMaterial duplicados/quase-duplicados
 2) Cria IfcGrid (eixos estruturais do Bloco Principal)
 3) Resolve 2 clashes reais (eletrocalha A11 x estrada) rebaixando a calha
 4) Modela furacao: IfcOpeningElement + IfcRelVoidsElement para prumadas que cruzam lajes de piso
"""
import ifcopenshell, ifcopenshell.geom as geom, ifcopenshell.util.placement as P
import numpy as np, multiprocessing, json, csv, unicodedata
from collections import defaultdict, Counter

m=ifcopenshell.open("HVG_MASTER_v87_Arq_MEP_coordenado.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
ctx=m.by_type("IfcGeometricRepresentationContext")[0]
def newg(): return ifcopenshell.guid.new()

# ============ 1) CONSOLIDAR MATERIAIS ============
def norm(s): return unicodedata.normalize('NFKD',(s or "").lower()).encode('ascii','ignore').decode()
groups=defaultdict(list)
for mt in m.by_type("IfcMaterial"): groups[norm(mt.Name)].append(mt)
def quality(mt):  # preferir nome com acento/maiuscula correta (mais bytes nao-ascii)
    return sum(1 for ch in (mt.Name or "") if ord(ch)>127)
removed=0
for k,v in groups.items():
    if len(v)<2: continue
    canon=max(v,key=quality)
    for dup in v:
        if dup==canon: continue
        for inv in m.get_inverse(dup):
            for i,att in enumerate(inv):
                if att==dup: inv[i]=canon
                elif isinstance(att,(tuple,list)) and dup in att:
                    inv[i]=tuple(canon if x==dup else x for x in att)
        m.remove(dup); removed+=1
print(f"[1] Materiais consolidados: -{removed} (restam {len(m.by_type('IfcMaterial'))})")

# ============ 2) IfcGrid (Bloco Principal) ============
import ifcopenshell.util.element as E
def wpos(e): x=P.get_local_placement(e.ObjectPlacement); return (round(float(x[0][3]),2),round(float(x[1][3]),2))
bp_cols=[c for c in m.by_type("IfcColumn")
         if any(r.RelatingStructure.Name in ("BP-Subsolo","BP-Terreo") for r in c.ContainedInStructure)]
xs=sorted({wpos(c)[0] for c in bp_cols}); ys=sorted({wpos(c)[1] for c in bp_cols})
def axis(tag, p1, p2):
    poly=m.create_entity("IfcPolyline",[m.create_entity("IfcCartesianPoint",[float(p1[0]),float(p1[1])]),
                                        m.create_entity("IfcCartesianPoint",[float(p2[0]),float(p2[1])])])
    return m.create_entity("IfcGridAxis",AxisTag=tag,AxisCurve=poly,SameSense=True)
y0,y1=min(ys)-2,max(ys)+2; x0,x1=min(xs)-2,max(xs)+2
import string
uax=[axis(string.ascii_uppercase[i],(x,y0),(x,y1)) for i,x in enumerate(xs)]   # eixos verticais (X) -> letras
vax=[axis(str(i+1),(x0,y),(x1,y)) for i,y in enumerate(ys)]                    # eixos horizontais (Y) -> numeros
grid_place=m.create_entity("IfcLocalPlacement",None,
    m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[0.,0.,0.]),None,None))
subctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext")] or [ctx]
grid=m.create_entity("IfcGrid",GlobalId=newg(),OwnerHistory=oh,Name="BP-EIXOS",
     Description="Malha estrutural Bloco Principal (~4,97m)",ObjectPlacement=grid_place,
     UAxes=uax,VAxes=vax)
# conter no pavimento BP-Terreo
bp_terreo=[s for s in m.by_type("IfcBuildingStorey") if s.Name=="BP-Terreo"][0]
rel=None
for r in bp_terreo.ContainsElements: rel=r;break
if rel: rel.RelatedElements=list(rel.RelatedElements)+[grid]
else: m.create_entity("IfcRelContainedInSpatialStructure",newg(),oh,None,None,[grid],bp_terreo)
print(f"[2] IfcGrid criado: {len(uax)} eixos U (A..) x {len(vax)} eixos V (1..)")

# ============ 3) Resolver clashes eletrocalha x estrada ============
moved3=0
for cc in m.by_type("IfcCableCarrierSegment"):
    if cc.Name=="Bloco-A-11-L2-CT":
        loc=cc.ObjectPlacement.RelativePlacement.Location
        x,y,z=loc.Coordinates
        loc.Coordinates=(float(x),float(y),float(z-0.12))  # rebaixa 12cm
        moved3+=1
print(f"[3] Eletrocalhas rebaixadas (clash x estrada): {moved3}")

m.write("HVG_MASTER_v88_Arq_MEP_executivo.ifc")
print("Parcial gravado (sem furos ainda).")
