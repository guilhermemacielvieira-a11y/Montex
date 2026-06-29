"""Perfil/corte do terreno x edificios para validacao visual do assentamento."""
import ifcopenshell, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from collections import defaultdict

m=ifcopenshell.open("HVG_MASTER_v101_DIMENSIONADO.ifc")
def pxyz(el):
    x=y=z=0.0; p=el.ObjectPlacement
    while p:
        rp=getattr(p,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location:
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]; z+=c[2]
        p=getattr(p,"PlacementRelTo",None)
    return np.array([x,y,z])
site=m.by_type("IfcSite")[0]; soff=pxyz(site)
tfs=[it for r in site.Representation.Representations for it in r.Items if it.is_a("IfcTriangulatedFaceSet")][0]
V=np.array(tfs.Coordinates.CoordList,float)+soff
tx,ty,tz=V[:,0],V[:,1],V[:,2]
def tz_at(x,y):
    z=griddata((tx,ty),tz,(x,y),method="linear")
    return float(z) if not np.isnan(z) else float(griddata((tx,ty),tz,(x,y),method="nearest"))

def find_building(o):
    for rel in m.by_type("IfcRelAggregates"):
        if o in (rel.RelatedObjects or []):
            p=rel.RelatingObject; return p if p.is_a("IfcBuilding") else find_building(p)
    return None
b_st=defaultdict(list); b_xy=defaultdict(list)
for st in m.by_type("IfcBuildingStorey"):
    b=find_building(st);
    if b: b_st[b.Name].append(st)
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    s=rel.RelatingStructure
    if not s.is_a("IfcBuildingStorey"): continue
    b=find_building(s)
    if b:
        for el in rel.RelatedElements:
            if el.ObjectPlacement and not el.is_a("IfcAnnotation"): b_xy[b.Name].append(pxyz(el)[:2])
def info(bn):
    sts=b_st[bn]; xy=np.array(b_xy[bn]); xy=xy[(np.abs(xy[:,0])>.01)|(np.abs(xy[:,1])>.01)]
    cx,cy=np.median(xy[:,0]),np.median(xy[:,1])
    zb=min(pxyz(s)[2] for s in sts); zt=max(pxyz(s)[2] for s in sts)
    ter=[s for s in sts if abs(s.Elevation or 0)<.01]
    z0=pxyz(ter[0])[2] if ter else zb
    return cx,cy,zb,zt,z0

# corte N-S em X~180 (A-03, A-06, A-09, Bloco Principal) + B-13
line=[("Bloco-A-03"),("Bloco-A-06"),("Bloco-A-09"),("Bloco Principal"),("Bloco-B-13")]
pts=[info(b) for b in line]
# eixo do corte = Y (todos perto de X 165-180)
order=sorted(range(len(pts)),key=lambda i:pts[i][1])
ys=np.linspace(100,460,200); xs=np.full_like(ys,175.0)
zter=[tz_at(x,y) for x,y in zip(xs,ys)]

fig,ax=plt.subplots(figsize=(15,7))
ax.fill_between(ys,zter,min(zter)-3,color="#caa472",alpha=0.6,label="terreno natural")
ax.plot(ys,zter,color="#7a5a2e",lw=2)
for i in order:
    cx,cy,zb,zt,z0=pts[i]
    bn=line[i]; zt_solo=tz_at(cx,cy)
    w=18
    # caixa do edificio (base a topo)
    ax.add_patch(plt.Rectangle((cy-w/2,zb),w,zt-zb,fill=True,fc="#9db4c0",ec="#33495a",lw=1.5,alpha=0.85,zorder=3))
    ax.plot([cy-w/2,cy+w/2],[z0,z0],color="darkblue",lw=2,zorder=4)  # piso terreo
    ax.plot(cy,zt_solo,"v",color="red",ms=9,zorder=5)
    ax.annotate(f"{bn.replace('Bloco-','')}\nterreo {z0:.1f}\nsolo {zt_solo:.1f}\n(+{z0-zt_solo:.1f}m)",
                (cy,zt+1),fontsize=7,ha="center",va="bottom")
ax.set_xlabel("Y (m) - corte N-S em X=175"); ax.set_ylabel("cota Z (m)")
ax.set_title("Perfil terreno x edificios — piso terreo (azul) fica +2,0 m acima do terreno natural (V vermelho)")
ax.legend(loc="upper left"); ax.grid(alpha=0.3)
plt.savefig("HVG_v101_Perfil_Terreno.png",dpi=95,bbox_inches="tight")
print("salvo HVG_v101_Perfil_Terreno.png")
for i in order:
    cx,cy,zb,zt,z0=pts[i]; print(f"{line[i]:18s} terreo={z0:.1f} base={zb:.1f} solo={tz_at(cx,cy):.1f} desnivel=+{z0-tz_at(cx,cy):.1f}m")
