#!/usr/bin/env python3
import ifcopenshell, ifcopenshell.geom as geom
import numpy as np, multiprocessing, json, time
from collections import Counter, defaultdict
SRC="/root/.claude/uploads/df8eb48a-3536-58ee-9b8f-4a4c5930a696/ee25662c-HVGMASTERINTEGRADOv87.ifc"
m=ifcopenshell.open(SRC)
print("Schema",m.schema,"| Entities",len(list(m)))
print("Site bbox ref / Project:",m.by_type("IfcProject")[0].Name[:60])

s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
rec={}  # id-> dict
t0=time.time(); ok=0
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        v=np.array(sh.geometry.verts,dtype=float).reshape(-1,3)
        f=np.array(sh.geometry.faces,dtype=int).reshape(-1,3)
        if len(v):
            mn=v.min(0); mx=v.max(0); ctr=(mn+mx)/2; size=mx-mn
            vol=0.0
            if len(f):
                a=v[f[:,0]]; b=v[f[:,1]]; c=v[f[:,2]]
                vol=float(np.sum(np.einsum('ij,ij->i',a,np.cross(b,c)))/6.0)
            rec[sh.id]=dict(t=el.is_a(),name=el.Name,ctr=ctr.tolist(),size=size.tolist(),
                            vol=vol,nan=bool(np.isnan(v).any()),nv=len(v))
            ok+=1
        if not it.next(): break
print(f"Meshed {ok} elements in {round(time.time()-t0,1)}s")
json.dump(rec, open("diag_geom.json","w"))

# elements that have a body representation but FAILED to mesh (render issues)
meshed=set(rec.keys())
have_rep=[e for e in m.by_type("IfcElement") if e.Representation]
failed=[e for e in have_rep if e.id() not in meshed and not e.is_a("IfcOpeningElement")]
print("Elementos com representacao que FALHARAM ao gerar malha:",len(failed))
print("  por tipo:",dict(Counter(e.is_a() for e in failed)))
json.dump([e.id() for e in failed], open("diag_failed.json","w"))
