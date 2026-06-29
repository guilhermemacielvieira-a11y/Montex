"""Verificacao de coordenacao TERRENO x EDIFICACOES (via dados, sem motor de geometria).
Extrai a malha do terreno (IfcTriangulatedFaceSet do IfcSite), interpola a cota do
terreno na posicao de cada edificio e compara com a cota de implantacao (storey terreo).
Gera relatorio + planta de cotas + perfil."""
import ifcopenshell, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from collections import defaultdict

m=ifcopenshell.open("HVG_MASTER_v101_DIMENSIONADO.ifc")

def place_xyz(el):
    x=y=z=0.0; p=el.ObjectPlacement
    while p:
        rp=getattr(p,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location:
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]; z+=c[2]
        p=getattr(p,"PlacementRelTo",None)
    return np.array([x,y,z])

# ---- malha do terreno ----
site=m.by_type("IfcSite")[0]
site_off=place_xyz(site)
tfs=None
for r in site.Representation.Representations:
    for it in r.Items:
        if it.is_a("IfcTriangulatedFaceSet"): tfs=it
verts=np.array(tfs.Coordinates.CoordList,float)+site_off[:3]
print(f"Terreno: {len(verts)} vertices | X[{verts[:,0].min():.0f},{verts[:,0].max():.0f}] "
      f"Y[{verts[:,1].min():.0f},{verts[:,1].max():.0f}] Z[{verts[:,2].min():.1f},{verts[:,2].max():.1f}]")
tx,ty,tz=verts[:,0],verts[:,1],verts[:,2]

def terreno_z(x,y):
    z=griddata((tx,ty),tz,(x,y),method="linear")
    if np.isnan(z): z=griddata((tx,ty),tz,(x,y),method="nearest")
    return float(z)

# ---- edificios: cota de implantacao (storey mais baixo = base) e XY (centroide elementos) ----
def find_building(obj):
    for rel in m.by_type("IfcRelAggregates"):
        if obj in (rel.RelatedObjects or []):
            par=rel.RelatingObject
            return par if par.is_a("IfcBuilding") else find_building(par)
    return None
# storeys por edificio
b_storeys=defaultdict(list)
for st in m.by_type("IfcBuildingStorey"):
    b=find_building(st)
    if b: b_storeys[b.Name].append(st)
# XY dos elementos por edificio
b_xy=defaultdict(list)
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    stt=rel.RelatingStructure
    if not stt.is_a("IfcBuildingStorey"): continue
    b=find_building(stt)
    if not b: continue
    for el in rel.RelatedElements:
        if el.ObjectPlacement and not el.is_a("IfcAnnotation"):
            p=place_xyz(el); b_xy[b.Name].append(p[:2])

EDIF=["Bloco Principal","Centro de Convenções","Boite Soul & Blues","Restaurante da Piscina",
      "SPA","Clube NEP","Guarita"]+[f"Bloco-A-{i:02d}" for i in range(1,13)]+[f"Bloco-B-{i}" for i in range(13,17)]
rows=[]
for bn in EDIF:
    sts=b_storeys.get(bn,[])
    if not sts: continue
    base=min(sts,key=lambda s:(s.Elevation if s.Elevation is not None else 0))
    base_world=place_xyz(base)[2]  # cota base (subsolo/terreo mais baixo)
    terreo=[s for s in sts if abs((s.Elevation or 0))<0.01]
    terreo_world=place_xyz(terreo[0])[2] if terreo else base_world
    xy=np.array(b_xy.get(bn,[]))
    xy=xy[(np.abs(xy[:,0])>0.01)|(np.abs(xy[:,1])>0.01)] if len(xy) else xy
    if not len(xy): continue
    cx,cy=np.median(xy[:,0]),np.median(xy[:,1])
    zt=terreno_z(cx,cy)
    # desnivel: cota do terreo do edificio vs terreno natural
    delta=terreo_world-zt
    rows.append((bn,cx,cy,terreo_world,base_world,zt,delta))

print(f"\n{'Edificio':24s} {'X':>7s} {'Y':>7s} {'Terreo':>7s} {'Base':>7s} {'Terreno':>8s} {'Desnivel':>9s}  Situacao")
print("-"*92)
alerts=[]
for bn,cx,cy,tw,bw,zt,d in rows:
    if d>1.5: sit=f"ATERRO {d:+.1f}m (terreo acima do solo)"; alerts.append((bn,d))
    elif d<-1.5: sit=f"CORTE {d:+.1f}m (terreo abaixo do solo)"; alerts.append((bn,d))
    else: sit="OK (na cota do terreno)"
    print(f"{bn:24s} {cx:7.0f} {cy:7.0f} {tw:7.1f} {bw:7.1f} {zt:8.1f} {d:+9.1f}  {sit}")
print(f"\nEdificios com desnivel > 1,5 m: {len(alerts)}")

# ---- planta de cotas ----
fig,ax=plt.subplots(figsize=(13,12))
sc=ax.scatter(tx,ty,c=tz,s=4,cmap="terrain",alpha=0.6)
plt.colorbar(sc,label="cota terreno (m)")
for bn,cx,cy,tw,bw,zt,d in rows:
    col="red" if abs(d)>1.5 else "black"
    ax.plot(cx,cy,"s",ms=8,mfc="none",mec=col,mew=2)
    ax.annotate(f"{bn.replace('Bloco-','').replace(' ','')[:8]}\n{d:+.1f}m",(cx,cy),
                fontsize=6,color=col,ha="center",va="bottom")
ax.set_aspect("equal"); ax.set_title("Cota do terreno x implantacao dos edificios (desnivel terreo-terreno)")
plt.savefig("HVG_v101_Verif_Terreno.png",dpi=95,bbox_inches="tight")
print("salvo HVG_v101_Verif_Terreno.png")
