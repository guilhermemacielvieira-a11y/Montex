import ifcopenshell, ifcopenshell.geom as geom, numpy as np, multiprocessing, pickle
import ifcopenshell.util.element as E
m=ifcopenshell.open("HVG_MASTER_v92_alinhado.ifc")
TARGET={"SPA":"SPA","Restaurante da Piscina":"RP","Clube NEP":"NEP","Guarita":"GUA"}
emap={}
for b in m.by_type("IfcBuilding"):
    if b.Name in TARGET:
        for st in m.by_type("IfcBuildingStorey"):
            if E.get_aggregate(st)==b:
                for r in st.ContainsElements:
                    for el in r.RelatedElements: emap[el.id()]=TARGET[b.Name]
CAT={"IfcWall":"wall","IfcColumn":"col","IfcBeam":"beam","IfcSlab":"slab","IfcWindow":"win","IfcDoor":"door","IfcRoof":"roof","IfcRailing":"rail","IfcStair":"stair","IfcStairFlight":"stair"}
s=geom.settings(); s.set("use-world-coords",True)
it=geom.iterator(s,m,multiprocessing.cpu_count()); data=[]; bad=0
if it.initialize():
    while True:
        sh=it.get(); el=m.by_id(sh.id)
        if el.id() in emap and el.is_a() in CAT:
            v=np.array(sh.geometry.verts,dtype=np.float32).reshape(-1,3); f=np.array(sh.geometry.faces,dtype=np.int32).reshape(-1,3)
            if len(v) and len(f):
                if (v.max(0)-v.min(0)).max()>60: bad+=1
                data.append((emap[el.id()],CAT[el.is_a()],v,f))
        if not it.next(): break
pickle.dump(data,open("meshes4.pkl","wb"))
print("Elementos:",len(data),"| corrompidos>60m:",bad)
