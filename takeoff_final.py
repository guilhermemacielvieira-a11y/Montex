#!/usr/bin/env python3
"""HVG v90 - Takeoff 5D consolidado: quantitativos confiaveis (Qto + geometria MEP/telhado)
e orcamento indicativo com precos de referencia (substituir por composicao propria)."""
import ifcopenshell, csv, json
import ifcopenshell.util.element as E
from collections import defaultdict
m=ifcopenshell.open("HVG_MASTER_v90_LOD300.ifc")
geomj=json.load(open("takeoff_geom.json"))

def qty(el,*names):
    want=set(names)
    for r in el.IsDefinedBy:
        if r.is_a("IfcRelDefinesByProperties") and r.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
            for q in r.RelatingPropertyDefinition.Quantities:
                if q.Name in want:
                    for a in ("VolumeValue","AreaValue","LengthValue","CountValue"):
                        v=getattr(q,a,None)
                        if v is not None: return float(v)
    return 0.0
def mat_name(el):
    for r in el.HasAssociations:
        if r.is_a("IfcRelAssociatesMaterial") and r.RelatingMaterial.is_a("IfcMaterial"):
            return r.RelatingMaterial.Name
    return "(sem material)"
def in_storey(el):
    c=E.get_container(el); return c is not None and c.is_a("IfcBuildingStorey")

# ---- agregacao confiavel ----
def is_concrete(mn): return "Concreto" in mn or "Steel Deck" in mn
col_vol=sum(qty(e,"NetVolume","GrossVolume") for e in m.by_type("IfcColumn"))
beam_vol=sum(qty(e,"NetVolume","GrossVolume") for e in m.by_type("IfcBeam"))
# pilares/vigas por material (concreto vs aco)
def vol_by_mat(cls):
    d=defaultdict(float)
    for e in m.by_type(cls): d[mat_name(e)]+=qty(e,"NetVolume","GrossVolume")
    return d
# lajes: area Qto separada struct/site
slab_struct=defaultdict(lambda:[0.0,0]); slab_site=defaultdict(lambda:[0.0,0]); slab_vol=0.0
for sl in m.by_type("IfcSlab"):
    a=qty(sl,"GrossArea","NetArea"); slab_vol+=qty(sl,"NetVolume","GrossVolume")
    (slab_struct if in_storey(sl) else slab_site)[mat_name(sl)][0]+=a
    (slab_struct if in_storey(sl) else slab_site)[mat_name(sl)][1]+=1
wall_area=sum(qty(e,"NetSideArea","GrossSideArea") for e in m.by_type("IfcWall"))
wall_vol=sum(qty(e,"NetVolume","GrossVolume") for e in m.by_type("IfcWall"))
cov_area=defaultdict(float)
for e in m.by_type("IfcCovering"): cov_area[mat_name(e)]+=qty(e,"NetArea","GrossArea")
win_area=sum(qty(e,"Area") for e in m.by_type("IfcWindow")); win_n=len(m.by_type("IfcWindow"))
door_area=sum(qty(e,"Area") for e in m.by_type("IfcDoor")); door_n=len(m.by_type("IfcDoor"))

# ---- TABELA QUANTITATIVA MESTRE ----
QT=[]
QT.append(("Estrutura","Pilares - concreto/aco","m3",round(col_vol,2),len(m.by_type("IfcColumn"))))
QT.append(("Estrutura","Vigas - concreto/aco","m3",round(beam_vol,2),len(m.by_type("IfcBeam"))))
QT.append(("Estrutura","Lajes - volume","m3",round(slab_vol,2),len(m.by_type("IfcSlab"))))
ss=sum(v[0] for v in slab_struct.values()); QT.append(("Estrutura","Lajes de piso - area","m2",round(ss,1),sum(v[1] for v in slab_struct.values())))
QT.append(("Arquitetura","Paredes - area","m2",round(wall_area,1),len(m.by_type("IfcWall"))))
QT.append(("Arquitetura","Paredes - volume","m3",round(wall_vol,1),len(m.by_type("IfcWall"))))
QT.append(("Arquitetura","Esquadrias/Janelas","m2",round(win_area,1),win_n))
QT.append(("Arquitetura","Portas","un",door_n,door_n))
QT.append(("Cobertura","Telhado - superficie","m2",geomj["roof_area"],len(m.by_type("IfcRoof"))))
covtot=sum(cov_area.values()); QT.append(("Acabamento","Revestimentos/Coberturas","m2",round(covtot,1),len(m.by_type("IfcCovering"))))
se=sum(v[0] for v in slab_site.values()); QT.append(("Urbanismo","Pavimentacao/site - area","m2",round(se,1),sum(v[1] for v in slab_site.values())))
QT.append(("MEP","Tubulacao hidraulica/incendio","m",geomj["mep_len"].get("IfcPipeSegment",0),len(m.by_type("IfcPipeSegment"))))
QT.append(("MEP","Dutos AVAC","m",geomj["mep_len"].get("IfcDuctSegment",0),len(m.by_type("IfcDuctSegment"))))
QT.append(("MEP","Eletrocalhas/bandejas","m",geomj["mep_len"].get("IfcCableCarrierSegment",0),len(m.by_type("IfcCableCarrierSegment"))))

with open("HVG_v90_Takeoff_Mestre.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["Disciplina","Servico","Unidade","Quantidade","N_Elementos"])
    for r in QT: w.writerow(r)

print("=== TAKEOFF MESTRE (v90) ===")
for d,sv,u,q,n in QT: print(f"  [{d:11}] {sv:30} {q:>11} {u:4} ({n})")

# ---- ORCAMENTO INDICATIVO (precos REFERENCIA - substituir por composicao) ----
# (servico, unidade, qtd, preco_ref_BRL)
PR={"Pilares - concreto/aco":("m3",col_vol,2600),"Vigas - concreto/aco":("m3",beam_vol,2600),
    "Lajes (Steel Deck/concreto)":("m2",ss,310),"Paredes (alvenaria/drywall)":("m2",wall_area,190),
    "Esquadrias/Janelas":("m2",win_area,950),"Portas":("un",door_n,1300),
    "Telhado (telha+estrutura)":("m2",geomj["roof_area"],240),"Revestimentos/Coberturas":("m2",covtot,160),
    "Pavimentacao externa":("m2",se,120),"Tubulacao":("m",geomj["mep_len"].get("IfcPipeSegment",0),85),
    "Dutos AVAC":("m",geomj["mep_len"].get("IfcDuctSegment",0),230),
    "Eletrocalhas":("m",geomj["mep_len"].get("IfcCableCarrierSegment",0),130)}
with open("HVG_v90_Orcamento_Indicativo.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["Servico","Unidade","Quantidade","Preco_Ref_BRL_unit","Subtotal_BRL"])
    tot=0
    for sv,(u,q,p) in PR.items():
        sub=q*p; tot+=sub; w.writerow([sv,u,round(q,1),p,round(sub,2)])
    w.writerow(["TOTAL INDICATIVO (REFERENCIA)","","","",round(tot,2)])
print(f"\n=== ORCAMENTO INDICATIVO (precos de REFERENCIA) ===")
tot=0
for sv,(u,q,p) in PR.items():
    sub=q*p; tot+=sub; print(f"  {sv:30} {round(q,1):>9} {u:3} x R${p:>5} = R$ {sub:>13,.0f}")
print(f"  {'TOTAL INDICATIVO':30} {'':>9} {'':3}            R$ {tot:>13,.0f}")
print(f"  Custo/m2 construido (util {31585:.0f} m2): R$ {tot/31585:,.0f}/m2")
