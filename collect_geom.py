#!/usr/bin/env python3
"""Coleta bbox+categoria de todos os elementos do Bloco Principal (e storeys) para desenhos 2D."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np, multiprocessing, json, pickle
import ifcopenshell.util.element as E
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
bp=[b for b in m.by_type("IfcBuilding") if b.Name=="Bloco Principal"][0]
bp_storeys={st.id():st.Name for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==bp}
# ids dos elementos contidos no BP
bp_elem={}
for st in m.by_type("IfcBuildingStorey"):
    if st.id() in bp_storeys:
        for r in st.ContainsElements:
            for el in r.RelatedElements: bp_elem[el.id()]=bp_storeys[st.id()]
print("BP elementos:",len(bp_elem),"storeys:",list(bp_storeys.values()))
s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
recs=[]
CAT={"IfcWall":"wall","IfcColumn":"col","IfcBeam":"beam","IfcSlab":"slab","IfcWindow":"win",
     "IfcDoor":"door","IfcRoof":"roof","IfcCovering":"cov","IfcRailing":"rail","IfcStair":"stair","IfcStairFlight":"stair"}
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        if el.id() in bp_elem and el.is_a() in CAT:
            v=np.array(sh.geometry.verts).reshape(-1,3)
            if len(v):
                recs.append(dict(cat=CAT[el.is_a()],storey=bp_elem[el.id()],
                    x0=float(v[:,0].min()),y0=float(v[:,1].min()),z0=float(v[:,2].min()),
                    x1=float(v[:,0].max()),y1=float(v[:,1].max()),z1=float(v[:,2].max())))
        if not it.next(): break
pickle.dump(recs,open("bp_geom.pkl","wb"))
zs=[r['z0'] for r in recs]+[r['z1'] for r in recs]
xs=[r['x0'] for r in recs]+[r['x1'] for r in recs]
ys=[r['y0'] for r in recs]+[r['y1'] for r in recs]
from collections import Counter
print("Recs:",len(recs),"cats:",dict(Counter(r['cat'] for r in recs)))
print(f"X[{min(xs):.0f},{max(xs):.0f}] Y[{min(ys):.0f},{max(ys):.0f}] Z[{min(zs):.1f},{max(zs):.1f}]")
