#!/usr/bin/env python3
"""Fase 2 - Deteccao de interferencias multidisciplinar (MEP x Estrutura e MEP x MEP).
Fase ampla: AABB mundo via motor de geometria. Fase estreita: ambos os solidos com
vertices dentro da caixa de sobreposicao (reduz falso-positivo de elementos lineares)."""
import ifcopenshell, ifcopenshell.geom as geom
import numpy as np, time, json, csv, multiprocessing
from collections import defaultdict

m=ifcopenshell.open("HVG_MASTER_v87_Arq_MEP_coordenado.ifc")
MEP=["IfcPipeSegment","IfcDuctSegment","IfcCableCarrierSegment","IfcCableSegment",
     "IfcAirTerminal","IfcFireSuppressionTerminal","IfcLightFixture",
     "IfcCommunicationsAppliance","IfcElectricDistributionBoard"]
STR=["IfcColumn","IfcBeam","IfcSlab","IfcWall","IfcRoof","IfcStairFlight"]
want=set(MEP+STR)

s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s, m, multiprocessing.cpu_count())
data={}  # id -> (ifc_type, name, sys, vmin, vmax, verts)
def system_of(el):
    for r in getattr(el,'HasAssignments',[]) or []:
        if r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup.is_a("IfcDistributionSystem"):
            return r.RelatingGroup.Name
    return None
t0=time.time(); n=0
if it.initialize():
    while True:
        sh=it.get()
        el=m.by_id(sh.id)
        if el.is_a() in want:
            v=np.array(sh.geometry.verts,dtype=float).reshape(-1,3)
            if len(v):
                data[sh.id]=(el.is_a(), el.Name, system_of(el),
                             v.min(0), v.max(0), v)
                n+=1
        if not it.next(): break
print(f"Geometrias computadas: {n} em {round(time.time()-t0,1)}s")

# broad-phase via spatial hash (celula 3m)
CELL=3.0
grid=defaultdict(list)
def cells(vmin,vmax):
    for i in range(int(np.floor(vmin[0]/CELL)),int(np.floor(vmax[0]/CELL))+1):
        for j in range(int(np.floor(vmin[1]/CELL)),int(np.floor(vmax[1]/CELL))+1):
            for k in range(int(np.floor(vmin[2]/CELL)),int(np.floor(vmax[2]/CELL))+1):
                yield (i,j,k)
ids=list(data.keys())
for eid in ids:
    _,_,_,vmin,vmax,_=data[eid]
    for c in cells(vmin,vmax): grid[c].append(eid)

def aabb_overlap(a,b,tol=0.0):
    return all(a[0][d] < b[1][d]-(-tol) and b[0][d] < a[1][d]-(-tol) for d in range(3))

MEPset=set(MEP); STRset=set(STR)
TOL=0.01  # 1 cm minimo de penetracao
checked=set(); clashes=[]
for c,members in grid.items():
    for x in range(len(members)):
        for y in range(x+1,len(members)):
            a,b=members[x],members[y]
            key=(a,b) if a<b else (b,a)
            if key in checked: continue
            checked.add(key)
            ta=data[a][0]; tb=data[b][0]
            # interessa MEPxSTR ou MEPxMEP (sistemas diferentes)
            pair=None
            if ta in MEPset and tb in STRset: pair="MEPxEstrutura"
            elif tb in MEPset and ta in STRset: pair="MEPxEstrutura"
            elif ta in MEPset and tb in MEPset:
                if data[a][2]!=data[b][2]: pair="MEPxMEP"
            if not pair: continue
            amin,amax=data[a][3],data[a][4]; bmin,bmax=data[b][3],data[b][4]
            # caixa de sobreposicao
            omin=np.maximum(amin,bmin); omax=np.minimum(amax,bmax)
            if np.any(omax-omin <= TOL): continue
            # narrow: ambos com vertice dentro da caixa de sobreposicao (margem pequena)
            pad=0.02
            va=data[a][5]; vb=data[b][5]
            ina=np.all((va>=omin-pad)&(va<=omax+pad),axis=1).any()
            inb=np.all((vb>=omin-pad)&(vb<=omax+pad),axis=1).any()
            if not(ina and inb): continue
            ov=(omax-omin)
            clashes.append({"pair":pair,"a_id":a,"b_id":b,
                "a_type":ta,"a_name":data[a][1],"a_sys":data[a][2],
                "b_type":tb,"b_name":data[b][1],"b_sys":data[b][2],
                "overlap_xyz":[round(float(o),3) for o in ov],
                "penetracao_min_m":round(float(ov.min()),3),
                "centro":[round(float((omin[d]+omax[d])/2),2) for d in range(3)]})
print(f"Interferencias reais detectadas: {len(clashes)}")
from collections import Counter
print("Por categoria:", dict(Counter(c['pair'] for c in clashes)))
print("MEPxEstrutura por tipo estrutural:",
      dict(Counter((c['b_type'] if c['a_type'] in MEPset else c['a_type']) for c in clashes if c['pair']=='MEPxEstrutura')))

clashes.sort(key=lambda c:-c['penetracao_min_m'])
json.dump(clashes, open("clash_full_report.json","w"), indent=1, ensure_ascii=False)
with open("HVG_v88_Clash_Report_Multidisciplinar.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(["ID","Categoria","Elemento_A","Sistema_A","Elemento_B","Sistema_B",
                "Penetracao_min_m","Overlap_X","Overlap_Y","Overlap_Z","Centro_X","Centro_Y","Centro_Z","Prioridade"])
    for i,c in enumerate(clashes,1):
        pen=c['penetracao_min_m']
        prio="Alta" if pen>=0.10 else ("Media" if pen>=0.03 else "Baixa")
        w.writerow([f"CL2-{i:03d}",c['pair'],f"{c['a_type']}:{c['a_name']}",c['a_sys'] or "-",
                    f"{c['b_type']}:{c['b_name']}",c['b_sys'] or "-",pen,
                    *c['overlap_xyz'],*c['centro'],prio])
print("Gravado: HVG_v88_Clash_Report_Multidisciplinar.csv")
