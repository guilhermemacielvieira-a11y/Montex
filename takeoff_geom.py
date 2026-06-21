#!/usr/bin/env python3
"""Complementa o takeoff com comprimentos MEP e areas de telhado por geometria,
e separa lajes estruturais x pavimentacao de site. Gera CSV final + base p/ orcamento."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np, multiprocessing, csv, json
import ifcopenshell.util.element as E
from collections import defaultdict
m=ifcopenshell.open("HVG_MASTER_v90_LOD300.ifc")
def mat_name(el):
    for r in el.HasAssociations:
        if r.is_a("IfcRelAssociatesMaterial") and r.RelatingMaterial.is_a("IfcMaterial"):
            return r.RelatingMaterial.Name
    return "(sem material)"
def in_storey(el):
    c=E.get_container(el)
    return c is not None and c.is_a("IfcBuildingStorey")

s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count())
mep_len=defaultdict(lambda:[0.0,0]); roof_area=[0.0,0]; tri=lambda a,b,c:0.5*np.linalg.norm(np.cross(b-a,c-a))
slab_struct=defaultdict(lambda:[0.0,0]); slab_site=defaultdict(lambda:[0.0,0])
MEPlin={"IfcPipeSegment","IfcDuctSegment","IfcCableCarrierSegment","IfcCableSegment"}
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id); cls=el.is_a()
        v=np.array(sh.geometry.verts).reshape(-1,3)
        if cls in MEPlin and len(v):
            L=float((v.max(0)-v.min(0)).max()); mep_len[cls][0]+=L; mep_len[cls][1]+=1
        elif cls=="IfcRoof" and len(v):
            f=np.array(sh.geometry.faces).reshape(-1,3)
            # area das faces voltadas para cima
            A=0.0
            for t in f:
                a,b,c=v[t[0]],v[t[1]],v[t[2]]; n=np.cross(b-a,c-a)
                if n[2]>0: A+=0.5*np.linalg.norm(n)
            roof_area[0]+=A; roof_area[1]+=1
        elif cls=="IfcSlab" and len(v):
            # area projetada (planta) = (xmax-xmin)*(ymax-ymin) aproximada -> usar Qto se houver; aqui projetada
            dx,dy=(v.max(0)-v.min(0))[:2]; area=float(dx*dy)
            tgt=slab_struct if in_storey(el) else slab_site
            tgt[mat_name(el)][0]+=area; tgt[mat_name(el)][1]+=1
        if not it.next(): break

print("=== MEP - comprimentos (geometria) ===")
for k,(L,c) in mep_len.items(): print(f"  {k:24} {round(L,1):>8} m  ({c} seg)")
print(f"=== Telhado - area de superficie: {round(roof_area[0],1)} m2 ({roof_area[1]} telhados)")
print("\n=== Laje ESTRUTURAL (piso) por material [m2 projetada] ===")
tot_s=0
for mn,(a,c) in sorted(slab_struct.items(),key=lambda x:-x[1][0]): print(f"  {mn:34} {round(a,1):>9} ({c})"); tot_s+=a
print(f"  TOTAL estrutural: {round(tot_s,1)} m2")
print("\n=== Laje SITE/pavimentacao por material [m2] ===")
tot_e=0
for mn,(a,c) in sorted(slab_site.items(),key=lambda x:-x[1][0]): print(f"  {mn:34} {round(a,1):>9} ({c})"); tot_e+=a
print(f"  TOTAL pavimentacao site: {round(tot_e,1)} m2")

json.dump({"mep_len":{k:round(v[0],1) for k,v in mep_len.items()},
           "roof_area":round(roof_area[0],1),
           "slab_struct_m2":round(tot_s,1),"slab_site_m2":round(tot_e,1)},
          open("takeoff_geom.json","w"),ensure_ascii=False,indent=1)
