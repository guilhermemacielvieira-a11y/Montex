#!/usr/bin/env python3
"""Auditoria de alinhamento: pe-direito, empilhamento de janelas/paredes/varandas por edificio."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np
import ifcopenshell.util.element as E, ifcopenshell.util.placement as Pl
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
s=geom.settings(); s.set("use-world-coords",True)
def ctr(el):
    sh=geom.create_shape(s,el); v=np.array(sh.geometry.verts).reshape(-1,3)
    return np.array([(v[:,0].min()+v[:,0].max())/2,(v[:,1].min()+v[:,1].max())/2,v[:,2].min()])
issues=[]
for b in m.by_type("IfcBuilding"):
    sts=[(Pl.get_local_placement(st.ObjectPlacement)[2,3],st) for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==b]
    sts.sort()
    # pe-direito
    zs=[z for z,_ in sts]
    difs=[round(zs[i+1]-zs[i],2) for i in range(len(zs)-1)]
    if difs and (max(difs)-min(difs))>0.05:
        issues.append((b.Name,"PE-DIREITO irregular",difs))
    # window stacking: for each floor get window XY set; compare across floors
    floor_wins={}
    for z,st in sts:
        ws=[e for r in st.ContainsElements for e in r.RelatedElements if e.is_a()=="IfcWindow"]
        floor_wins[st.Name]=sorted([tuple(np.round(ctr(w)[:2],1)) for w in ws])
    names=list(floor_wins.keys())
    # compara conjuntos XY entre pavimentos com janelas
    nonempty=[n for n in names if floor_wins[n]]
    if len(nonempty)>=2:
        base=set(floor_wins[nonempty[0]])
        for n in nonempty[1:]:
            cur=set(floor_wins[n])
            # quantas alinham (mesma XY +-0.3)
            aligned=sum(1 for p in cur if any(abs(p[0]-q[0])<0.3 and abs(p[1]-q[1])<0.3 for q in base))
            if cur and aligned/len(cur)<0.8:
                issues.append((b.Name,f"JANELAS desalinhadas {n} vs {nonempty[0]}",f"{aligned}/{len(cur)}"))
print(f"Edificios auditados: {len(m.by_type('IfcBuilding'))}")
print(f"Problemas encontrados: {len(issues)}")
for nm,t,d in issues[:40]: print(f"  [{nm}] {t}: {d}")
# resumo pe-direito por tipologia
from collections import Counter
pd=Counter()
for b in m.by_type("IfcBuilding"):
    zs=sorted(Pl.get_local_placement(st.ObjectPlacement)[2,3] for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==b)
    for i in range(len(zs)-1): pd[round(zs[i+1]-zs[i],2)]+=1
print("Distribuicao de pe-direito (m):",dict(pd))
