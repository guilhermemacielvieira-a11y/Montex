"""Render isometrico rapido (faces sombreadas) de edificios selecionados do v101,
para inspecao visual da geometria. Usa iterador limitado aos elementos do edificio."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np, sys, time
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

m=ifcopenshell.open("HVG_MASTER_v101_DIMENSIONADO.ifc")
TARGETS=sys.argv[1:] or ["Bloco Principal","A-01"]

def storeys_of(bname):
    out=set()
    def rec(o):
        for rel in m.by_type("IfcRelAggregates"):
            if rel.RelatingObject==o:
                for c in rel.RelatedObjects:
                    if c.is_a("IfcBuildingStorey"): out.add(c.id())
                    elif c.is_a("IfcBuilding"): rec(c)
    for b in m.by_type("IfcBuilding"):
        if b.Name==bname: rec(b)
    return out

fig,axs=plt.subplots(1,len(TARGETS),figsize=(11*len(TARGETS),11))
if len(TARGETS)==1: axs=[axs]
s=geom.settings(); s.set(s.USE_WORLD_COORDS,True)
for ax,bname in zip(axs,TARGETS):
    sids=storeys_of(bname)
    inc=[]
    for rel in m.by_type("IfcRelContainedInSpatialStructure"):
        if rel.RelatingStructure.id() in sids:
            inc+=[e for e in rel.RelatedElements if e.Representation and not e.is_a("IfcAnnotation")]
    tris=[]; t0=time.time()
    if inc:
        it=geom.iterator(s,m,4,include=inc)
        if it.initialize():
            while True:
                sh=it.get()
                try:
                    v=np.array(sh.geometry.verts).reshape(-1,3)
                    f=np.array(sh.geometry.faces).reshape(-1,3)
                    if len(v) and len(f) and np.isfinite(v).all():
                        tris.append(v[f])
                except Exception: pass
                if not it.next(): break
    if not tris:
        ax.set_title(f"{bname}: sem geometria"); continue
    T=np.concatenate(tris)  # (N,3,3)
    # projecao isometrica
    az=np.radians(35); el=np.radians(25)
    # direcao de visao
    dx,dy,dz=np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)
    # eixos de tela
    rx=np.array([-np.sin(az),np.cos(az),0])
    ry=np.array([-np.sin(el)*np.cos(az),-np.sin(el)*np.sin(az),np.cos(el)])
    C=T.mean(1)  # centro de cada triangulo
    su=T@rx; sv=T@ry  # (N,3)
    depth=C@np.array([dx,dy,dz])
    # normal e shading
    n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); ln=np.linalg.norm(n,axis=1); ln[ln==0]=1
    n=n/ln[:,None]
    light=np.array([0.3,0.4,0.85]); sh=np.clip(np.abs(n@light),0.25,1.0)
    order=np.argsort(depth)
    polys=[np.column_stack([su[i],sv[i]]) for i in order]
    base=np.array([0.72,0.74,0.78])
    cols=[base*sh[i] for i in order]
    ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors="none"))
    ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{bname} — {len(inc)} elem, {len(T)} faces ({time.time()-t0:.0f}s)",fontsize=12)
plt.tight_layout(); plt.savefig("HVG_v101_Render_Iso.png",dpi=85,bbox_inches="tight")
print("salvo HVG_v101_Render_Iso.png")
