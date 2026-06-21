#!/usr/bin/env python3
"""Clash detection multidisciplinar no v90 (broad AABB + narrow interpenetracao).
Foco: confirmar que o novo programa (equipamentos/edificios) nao gera conflito."""
import ifcopenshell, ifcopenshell.geom as geom
import numpy as np, multiprocessing, json, csv
from collections import defaultdict, Counter
m=ifcopenshell.open("HVG_MASTER_v90_LOD300.ifc")
MEP=["IfcPipeSegment","IfcDuctSegment","IfcCableCarrierSegment","IfcCableSegment","IfcAirTerminal",
     "IfcFireSuppressionTerminal","IfcLightFixture","IfcCommunicationsAppliance","IfcElectricDistributionBoard",
     "IfcTransformer","IfcTank","IfcValve","IfcFlowController"]
STR=["IfcColumn","IfcBeam","IfcSlab","IfcWall","IfcRoof","IfcStairFlight","IfcMember"]
want=set(MEP+STR)
NEW_MARK=("SUB-","GAS-","Quadra-","Alambrado","Estacionamento","Pista-","APQ-","SPA-Anexo")
def is_new(el): return bool(el.Name and any(k in el.Name for k in NEW_MARK))

s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
data={}
def sysn(el):
    for r in (el.HasAssignments or []):
        if r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup and r.RelatingGroup.is_a("IfcDistributionSystem"):
            return r.RelatingGroup.Name
    return None
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        if el.is_a() in want:
            v=np.array(sh.geometry.verts,dtype=float).reshape(-1,3)
            if len(v): data[sh.id]=(el.is_a(),el.Name,sysn(el),v.min(0),v.max(0),v,is_new(el))
        if not it.next(): break
print("Geometrias:",len(data))
CELL=3.0; grid=defaultdict(list)
for eid,(t,nm,sy,mn,mx,v,nw) in data.items():
    for i in range(int(mn[0]//CELL),int(mx[0]//CELL)+1):
        for j in range(int(mn[1]//CELL),int(mx[1]//CELL)+1):
            for k in range(int(mn[2]//CELL),int(mx[2]//CELL)+1):
                grid[(i,j,k)].append(eid)
MEPs=set(MEP); STRs=set(STR); TOL=0.01; seen=set(); clashes=[]
for cell,mem in grid.items():
    for a in range(len(mem)):
        for b in range(a+1,len(mem)):
            x,y=mem[a],mem[b]; key=(x,y) if x<y else (y,x)
            if key in seen: continue
            seen.add(key)
            ta,tb=data[x][0],data[y][0]
            pair=None
            if (ta in MEPs and tb in STRs) or (tb in MEPs and ta in STRs): pair="MEPxEstrut"
            elif ta in MEPs and tb in MEPs and data[x][2]!=data[y][2]: pair="MEPxMEP"
            if not pair: continue
            amn,amx,bmn,bmx=data[x][3],data[x][4],data[y][3],data[y][4]
            omn=np.maximum(amn,bmn); omx=np.minimum(amx,bmx)
            if np.any(omx-omn<=TOL): continue
            va,vb=data[x][5],data[y][5]; pad=0.02
            if not(np.all((va>=omn-pad)&(va<=omx+pad),axis=1).any() and np.all((vb>=omn-pad)&(vb<=omx+pad),axis=1).any()): continue
            ov=omx-omn
            clashes.append((pair,data[x],data[y],float(ov.min()),[round(float((omn[d]+omx[d])/2),1) for d in range(3)]))
print("Interferencias reais:",len(clashes))
involving_new=[c for c in clashes if c[1][6] or c[2][6]]
print("Envolvendo NOVO programa:",len(involving_new))
for c in clashes:
    tag="<NOVO>" if (c[1][6] or c[2][6]) else ""
    print(f"  [{c[0]}] {c[1][0]}:{c[1][1]} x {c[2][0]}:{c[2][1]} pen={c[3]:.3f} centro={c[4]} {tag}")
# write register
with open("HVG_v90_Clash_Report.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["Categoria","Elem_A","Elem_B","Penetracao_m","Centro","Novo_Programa"])
    for c in clashes: w.writerow([c[0],f"{c[1][0]}:{c[1][1]}",f"{c[2][0]}:{c[2][1]}",round(c[3],3),c[4],"SIM" if(c[1][6]or c[2][6])else"nao"])
