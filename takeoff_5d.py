#!/usr/bin/env python3
"""HVG v90 - Levantamento de quantitativos (5D): por categoria, material e edificio."""
import ifcopenshell, csv, json
import ifcopenshell.util.element as E
from collections import defaultdict
m=ifcopenshell.open("HVG_MASTER_v90_LOD300.ifc")

def qty(el,*names):
    """retorna primeiro valor numerico encontrado entre os nomes dados em qualquer Qto."""
    want=set(names)
    for r in el.IsDefinedBy:
        if r.is_a("IfcRelDefinesByProperties") and r.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
            for q in r.RelatingPropertyDefinition.Quantities:
                if q.Name in want:
                    for a in ("VolumeValue","AreaValue","LengthValue","CountValue","WeightValue"):
                        v=getattr(q,a,None)
                        if v is not None: return float(v)
    return 0.0
def mat_name(el):
    for r in el.HasAssociations:
        if r.is_a("IfcRelAssociatesMaterial"):
            mt=r.RelatingMaterial
            if mt.is_a("IfcMaterial"): return mt.Name
            if mt.is_a("IfcMaterialLayerSetUsage"): 
                ls=mt.ForLayerSet
                if ls and ls.MaterialLayers: return ls.MaterialLayers[0].Material.Name
            if mt.is_a("IfcMaterialList") and mt.Materials: return mt.Materials[0].Name
            if hasattr(mt,'Name'): return mt.Name
    return "(sem material)"
def building_of(el):
    c=E.get_container(el)
    while c is not None and not c.is_a("IfcBuilding"):
        c=E.get_aggregate(c) if hasattr(c,'Decomposes') else None
        if c is None: break
    if c and c.is_a("IfcBuilding"): return c.Name
    # via aggregate chain (spaces)
    a=E.get_aggregate(el)
    while a is not None and not a.is_a("IfcBuilding"):
        a=E.get_aggregate(a)
    return a.Name if a else "(site/externo)"

# ---- quantitativos por categoria x material ----
# (categoria, ifc_class, [quant_names], unidade)
cats=[
 ("Pilar - Concreto/Aco","IfcColumn",["NetVolume","GrossVolume"],"m3"),
 ("Viga - Concreto/Aco","IfcBeam",["NetVolume","GrossVolume"],"m3"),
 ("Laje","IfcSlab",["NetVolume","GrossVolume"],"m3"),
 ("Laje (area)","IfcSlab",["NetArea","GrossArea"],"m2"),
 ("Parede (area)","IfcWall",["NetSideArea","GrossSideArea"],"m2"),
 ("Parede (volume)","IfcWall",["NetVolume","GrossVolume"],"m3"),
 ("Revestimento/Cobertura","IfcCovering",["NetArea","GrossArea"],"m2"),
 ("Telhado","IfcRoof",["NetArea","GrossArea"],"m2"),
 ("Janela/Esquadria","IfcWindow",["Area"],"m2"),
 ("Porta","IfcDoor",["Area"],"m2"),
 ("Tubulacao","IfcPipeSegment",["Length"],"m"),
 ("Duto AVAC","IfcDuctSegment",["Length"],"m"),
 ("Eletrocalha/Bandeja","IfcCableCarrierSegment",["Length"],"m"),
]
rows=[]; bymat=defaultdict(lambda: defaultdict(float)); bycat=defaultdict(float); counts=defaultdict(int)
for catname,cls,qnames,unit in cats:
    agg=defaultdict(lambda:[0.0,0])
    for el in m.by_type(cls):
        v=qty(el,*qnames)
        # length for MEP via geometry fallback handled by quantity; if 0 skip
        mn=mat_name(el)
        agg[mn][0]+=v; agg[mn][1]+=1
        bycat[(catname,unit)]+=v; counts[catname]+=1
    for mn,(v,c) in agg.items():
        rows.append([catname,unit,mn,round(v,2),c])

# escrever CSV quantitativo por material
with open("HVG_v90_Quantitativos_por_Material.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["Categoria","Unidade","Material","Quantidade","N_Elementos"])
    for r in sorted(rows,key=lambda x:(x[0],-x[3])): w.writerow(r)

# resumo por categoria
print("=== RESUMO QUANTITATIVO (modelo todo) ===")
for (cat,unit),v in sorted(bycat.items()):
    print(f"  {cat:26} {round(v,1):>12} {unit}  ({counts[cat]} elem)")

# Esquadrias por contagem
print("\nJanelas:",len(m.by_type("IfcWindow")),"| Portas:",len(m.by_type("IfcDoor")),"| Pilares:",len(m.by_type("IfcColumn")),"| Vigas:",len(m.by_type("IfcBeam")))

# area construida por edificio (espacos)
print("\n=== AREA DE ESPACOS POR EDIFICIO (m2 util) ===")
b_area=defaultdict(float)
for sp in m.by_type("IfcSpace"):
    b=building_of(sp); b_area[b]+=qty(sp,"NetFloorArea","GrossFloorArea")
tot=0
for b,a in sorted(b_area.items(),key=lambda x:-x[1]):
    print(f"  {b:24} {round(a,1):>10}"); tot+=a
print(f"  {'TOTAL':24} {round(tot,1):>10}")
json.dump({"bycat":{f"{k[0]}|{k[1]}":round(v,2) for k,v in bycat.items()},
           "b_area":{k:round(v,1) for k,v in b_area.items()}}, open("takeoff_summary.json","w"),ensure_ascii=False,indent=1)
