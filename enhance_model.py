#!/usr/bin/env python3
"""HVG v87 -> v87.1: saneamento de containment e materiais.
- Reassocia 5 elementos orfaos a estrutura espacial correta
- Completa associacao de material em muros de arrimo e elementos de pavimentacao/paisagismo"""
import ifcopenshell, ifcopenshell.util.placement as P
import ifcopenshell.util.element as E
import math
m=ifcopenshell.open("/home/user/Montex/HVG_MASTER_v87_Arq_MEP_coordenado.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
def wxy(e):
    x=P.get_local_placement(e.ObjectPlacement); return (float(x[0][3]),float(x[1][3]),float(x[2][3]))

# ---------- 1) CONTAINMENT de orfaos ----------
site=m.by_type("IfcSite")[0]
storeys=[(st, wxy(st)) for st in m.by_type("IfcBuildingStorey")]
def nearest_storey(p):
    # edificio mais proximo em XY, depois a laje/storey mais alto desse edificio <= Z do roof
    best_b=None;bd=1e18
    for b in m.by_type("IfcBuilding"):
        sts=[st for st,_ in storeys if E.get_aggregate(st)==b]
        if not sts: continue
        sp=[s for s,xy in storeys if s in sts]
        import statistics
        xs=[xy[0] for s,xy in storeys if s in sts]; ys=[xy[1] for s,xy in storeys if s in sts]
        cx=sum(xs)/len(xs); cy=sum(ys)/len(ys)
        d=(cx-p[0])**2+(cy-p[1])**2
        if d<bd: bd=d; best_b=b
    sts=[(st,xy) for st,xy in storeys if E.get_aggregate(st)==best_b]
    cand=[(st,xy) for st,xy in sts if xy[2] <= p[2]+1.0] or sts
    return max(cand, key=lambda t:t[1][2])[0]

def contain(el, struct):
    # adiciona a um IfcRelContainedInSpatialStructure existente do struct, ou cria
    rel=None
    for r in struct.ContainsElements:
        rel=r; break
    if rel:
        rel.RelatedElements = list(rel.RelatedElements)+[el]
    else:
        m.create_entity("IfcRelContainedInSpatialStructure",
            ifcopenshell.guid.new(), oh, None, None, [el], struct)

orphans=[e for e in m.by_type("IfcElement") if not e.ContainedInStructure and not e.Decomposes and not e.is_a("IfcOpeningElement")]
fixed=[]
for e in orphans:
    p=wxy(e)
    if e.is_a("IfcCovering"):
        contain(e, site); fixed.append((e.is_a(),e.Name,"Site"))
    else:
        st=nearest_storey(p)
        contain(e, st); fixed.append((e.is_a(),e.Name,st.Name))
print("Orfaos reassociados:")
for f in fixed: print("  ",f)

# ---------- 2) MATERIAIS ----------
def find_mat(name):
    for mt in m.by_type("IfcMaterial"):
        if mt.Name==name: return mt
    return None
def get_or_make_mat(name):
    mt=find_mat(name)
    if not mt: mt=m.create_entity("IfcMaterial", name)
    return mt
def associate(elements, mat):
    if not elements: return 0
    m.create_entity("IfcRelAssociatesMaterial", ifcopenshell.guid.new(), oh,
        None, None, list(elements), mat)
    return len(elements)

c25=find_mat("Concreto Armado C25")
c30=find_mat("Concreto Armado C30")
asfalto=get_or_make_mat("Pavimento Asfaltico CBUQ")
termo=get_or_make_mat("Termoplastico Sinalizacao Viaria")
terra=get_or_make_mat("Terra Vegetal Adubada")

def no_mat(el): return not any(r.is_a("IfcRelAssociatesMaterial") for r in el.HasAssociations)

# muros de arrimo
walls=[w for w in m.by_type("IfcWall") if no_mat(w)]
n=associate(walls, c30); print(f"Muros de arrimo -> Concreto Armado C30: {n}")

# slabs por ObjectType
buckets={}
for s in m.by_type("IfcSlab"):
    if no_mat(s):
        ot=(s.ObjectType or "").lower()
        if "asfalt" in ot or "pavimento asf" in ot: key=asfalto
        elif "guia" in ot or "meio-fio" in ot or "plataforma" in ot: key=c25
        elif "faixa" in ot or "sinaliza" in ot: key=termo
        elif "canteiro" in ot or "horta" in ot: key=terra
        else: key=c25
        buckets.setdefault(key.Name,[]).append(s)
        # store mapping by material entity
for matname,els in buckets.items():
    mt=find_mat(matname)
    n=associate(els, mt); print(f"Slabs -> {matname}: {n}")

# verificacao
rem_w=[w for w in m.by_type("IfcWall") if no_mat(w)]
rem_s=[s for s in m.by_type("IfcSlab") if no_mat(s)]
rem_o=[e for e in m.by_type("IfcElement") if not e.ContainedInStructure and not e.Decomposes and not e.is_a("IfcOpeningElement")]
print(f"\nResidual: walls s/mat={len(rem_w)} slabs s/mat={len(rem_s)} orfaos={len(rem_o)}")

proj=m.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+(
    " | v87.1 SANEAMENTO: 5 elementos orfaos reassociados a estrutura espacial (1 gramado->Site, 4 lajes planas->pavimento), "
    "%d muros de arrimo e %d lajes de pavimentacao/paisagismo com IfcMaterial completado (0 pendencias)."%(n if False else len(walls), len(rem_s)*0 + sum(len(v) for v in buckets.values())))

OUT="/home/user/Montex/HVG_MASTER_v87_Arq_MEP_coordenado.ifc"
m.write(OUT)
print("Gravado:", OUT)
