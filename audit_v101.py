"""Auditoria geometrica do v101: objetos fora de localizacao, geometria degenerada,
integridade. Gera estatisticas + vista em planta (footprint de cada elemento)."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np, time, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from collections import defaultdict, Counter

m=ifcopenshell.open("HVG_MASTER_v101_DIMENSIONADO.ifc")
t0=time.time()

# container building por elemento
def world_xy(el):
    x=y=z=0.0; p=el.ObjectPlacement
    while p:
        rp=p.RelativePlacement
        if rp and rp.is_a("IfcAxis2Placement3D"):
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]; z+=c[2]
        p=p.PlacementRelTo
    return x,y,z
def storey_build(st):
    for rel in m.by_type("IfcRelAggregates"):
        if st in (rel.RelatedObjects or []):
            par=rel.RelatingObject
            if par.is_a("IfcBuilding"): return par.Name
            if par.is_a("IfcBuildingStorey"): return storey_build(par)
    return None
elbuild={}
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    st=rel.RelatingStructure
    bn=st.Name if st.is_a("IfcSite") else (storey_build(st) if st.is_a("IfcBuildingStorey") else None)
    for el in rel.RelatedElements: elbuild[el.id()]=bn or "?"

s=geom.settings(); s.set(s.USE_WORLD_COORDS,True)
it=geom.iterator(s,m,8)
rows=[]  # (id, type, bx,by,bz size cx cy cz)
bad_inf=0; nshape=0
if it.initialize():
    while True:
        sh=it.get()
        try:
            v=np.array(sh.geometry.verts).reshape(-1,3)
        except Exception:
            v=np.empty((0,3))
        if len(v):
            if not np.isfinite(v).all(): bad_inf+=1
            else:
                mn=v.min(0); mx=v.max(0); c=(mn+mx)/2; sz=mx-mn
                rows.append((sh.id, sh.product.is_a(), c[0],c[1],c[2], sz[0],sz[1],sz[2]))
        nshape+=1
        if not it.next(): break
print(f"shapes processados: {nshape} em {time.time()-t0:.0f}s | com verts validos: {len(rows)} | inf/nan: {bad_inf}")

arr=np.array([[r[2],r[3],r[4],r[5],r[6],r[7]] for r in rows])
cx,cy,cz=arr[:,0],arr[:,1],arr[:,2]; sx,sy,sz=arr[:,3],arr[:,4],arr[:,5]
# centro robusto da implantacao
mx,my=np.median(cx),np.median(cy)
# dispersao
p1x,p99x=np.percentile(cx,[1,99]); p1y,p99y=np.percentile(cy,[1,99])
spanx=p99x-p1x; spany=p99y-p1y
print(f"\nImplantacao (1-99%): X[{p1x:.0f},{p99x:.0f}] Y[{p1y:.0f},{p99y:.0f}] -> {spanx:.0f} x {spany:.0f} m")
print(f"Z: min {cz.min():.1f} max {cz.max():.1f} (centros)")

# 1) OBJETOS FORA DE LOCALIZACAO: centro muito distante do cluster (alem de 3x o span)
limx=spanx*1.5; limy=spany*1.5
far=[(rows[i][0],rows[i][1],cx[i],cy[i],cz[i]) for i in range(len(rows))
     if abs(cx[i]-mx)>limx or abs(cy[i]-my)>limy]
print(f"\n[FORA DE LOCALIZACAO] elementos com centro alem de 1.5x o span da implantacao: {len(far)}")
for r in far[:20]: print(f"   {r[1]} #{r[0]}  centro=({r[2]:.0f},{r[3]:.0f},{r[4]:.1f})")

# 2) GEOMETRIA DEGENERADA: tamanho absurdo (>500m) ou zero
big=[(rows[i][0],rows[i][1],max(sx[i],sy[i],sz[i])) for i in range(len(rows)) if max(sx[i],sy[i],sz[i])>500]
zero=[(rows[i][0],rows[i][1]) for i in range(len(rows)) if max(sx[i],sy[i],sz[i])<1e-4]
print(f"\n[GEOMETRIA] elementos > 500 m (suspeito/explodido): {len(big)}")
for r in big[:15]: print(f"   {r[1]} #{r[0]}  maior_dim={r[2]:.0f} m")
print(f"[GEOMETRIA] elementos com dimensao ~0 (degenerado): {len(zero)}")

# 3) Z fora de faixa (edificios deveriam estar entre ~-10 e +60 m)
zfar=[(rows[i][0],rows[i][1],cz[i]) for i in range(len(rows)) if cz[i]<-20 or cz[i]>80]
print(f"\n[Z] elementos com Z fora de [-20,80] m: {len(zfar)}")
for r in zfar[:15]: print(f"   {r[1]} #{r[0]}  Z={r[2]:.1f}")

# ---- vista em planta (footprint de cada elemento, cor por tipo) ----
fig,ax=plt.subplots(figsize=(16,16))
typecol={}
import matplotlib.cm as cm
types=list({r[1] for r in rows})
cmap=cm.get_cmap("tab20",len(types))
for i,t in enumerate(types): typecol[t]=cmap(i)
patches=[]; colors=[]
for i in range(len(rows)):
    if max(sx[i],sy[i])>500: continue  # nao plota explodidos (distorce)
    patches.append(Rectangle((cx[i]-sx[i]/2,cy[i]-sy[i]/2),max(sx[i],0.3),max(sy[i],0.3)))
    colors.append(typecol[rows[i][1]])
pc=PatchCollection(patches,facecolor=colors,edgecolor="none",alpha=0.55)
ax.add_collection(pc)
# marca os fora-de-local em vermelho
if far:
    ax.scatter([r[2] for r in far],[r[3] for r in far],c="red",s=40,marker="x",label=f"fora de local ({len(far)})",zorder=5)
ax.set_xlim(mx-spanx*1.6,mx+spanx*1.6); ax.set_ylim(my-spany*1.6,my+spany*1.6)
ax.set_aspect("equal"); ax.set_title("HVG v101 - vista em planta (footprint por elemento; X=fora de local)")
ax.grid(alpha=0.2)
if far: ax.legend()
plt.savefig("HVG_v101_Auditoria_Planta.png",dpi=90,bbox_inches="tight")
print("\nsalvo HVG_v101_Auditoria_Planta.png")
