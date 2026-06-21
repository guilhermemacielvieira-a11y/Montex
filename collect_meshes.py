#!/usr/bin/env python3
"""Coleta malhas completas (verts+faces+categoria) dos edificios para desenhos de alta fidelidade."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np, multiprocessing, pickle
import ifcopenshell.util.element as E
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
TARGET={"Bloco Principal":"BP","Bloco-A-01":"A","Bloco-B-13":"B"}
# mapa elemento -> (sigla, storey)
emap={}
for b in m.by_type("IfcBuilding"):
    if b.Name not in TARGET: continue
    for st in m.by_type("IfcBuildingStorey"):
        if E.get_aggregate(st)==b:
            for r in st.ContainsElements:
                for el in r.RelatedElements: emap[el.id()]=(TARGET[b.Name],st.Name)
CAT={"IfcWall":"wall","IfcColumn":"col","IfcBeam":"beam","IfcSlab":"slab","IfcWindow":"win",
     "IfcDoor":"door","IfcRoof":"roof","IfcCovering":"cov","IfcRailing":"rail","IfcStairFlight":"stair","IfcStair":"stair"}
s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
data=[]
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        if el.id() in emap and el.is_a() in CAT:
            v=np.array(sh.geometry.verts,dtype=np.float32).reshape(-1,3)
            f=np.array(sh.geometry.faces,dtype=np.int32).reshape(-1,3)
            if len(v) and len(f):
                bld,st=emap[el.id()]
                data.append((bld,st,CAT[el.is_a()],v,f))
        if not it.next(): break
pickle.dump(data,open("meshes.pkl","wb"))
from collections import Counter
print("Elementos com malha:",len(data))
for bld in ("BP","A","B"):
    sub=[d for d in data if d[0]==bld]
    ntri=sum(len(d[4]) for d in sub)
    print(f"  {bld}: {len(sub)} elem, {ntri} triangulos, cats={dict(Counter(d[2] for d in sub))}")
