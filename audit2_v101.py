"""Auditoria leve do v101 via PLACEMENTS (posicao mundial por cadeia de IfcLocalPlacement).
Detecta objetos fora de localizacao + integridade. Gera vista em planta por tipo."""
import ifcopenshell, numpy as np, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

m=ifcopenshell.open("HVG_MASTER_v101_DIMENSIONADO.ifc")

def world(el):
    """origem mundial com rotacao acumulada (translacao)."""
    x=y=z=0.0; p=el.ObjectPlacement
    while p:
        rp=getattr(p,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location:
            c=rp.Location.Coordinates; x+=c[0]; y+=c[1]; z+=c[2]
        p=getattr(p,"PlacementRelTo",None)
    return x,y,z

# tipos fisicos 3D (ignora annotation/underlay 2D e elementos espaciais)
SKIP=("IfcAnnotation","IfcSpace","IfcSite","IfcBuilding","IfcBuildingStorey","IfcOpeningElement",
      "IfcGrid","IfcGridAxis")
prods=[e for e in m.by_type("IfcProduct") if e.ObjectPlacement and e.is_a() not in SKIP]
rows=[]
for e in prods:
    try:
        x,y,z=world(e);
        if all(map(math.isfinite,(x,y,z))): rows.append((e.id(),e.is_a(),x,y,z))
    except Exception: pass
arr=np.array([[r[2],r[3],r[4]] for r in rows]); types=[r[1] for r in rows]
cx,cy,cz=arr[:,0],arr[:,1],arr[:,2]
print(f"produtos 3D com placement: {len(rows)}")
mx,my=np.median(cx),np.median(cy)
p1x,p99x=np.percentile(cx,[1,99]); p1y,p99y=np.percentile(cy,[1,99])
spanx=p99x-p1x; spany=p99y-p1y
print(f"Implantacao (1-99%): X[{p1x:.0f},{p99x:.0f}] Y[{p1y:.0f},{p99y:.0f}] = {spanx:.0f} x {spany:.0f} m")
print(f"X total[{cx.min():.0f},{cx.max():.0f}] Y total[{cy.min():.0f},{cy.max():.0f}] Z[{cz.min():.1f},{cz.max():.1f}]")

# OUTLIERS de localizacao (alem de 1.5x span do centro)
limx=max(spanx*1.5,50); limy=max(spany*1.5,50)
far=[(rows[i][0],rows[i][1],cx[i],cy[i],cz[i]) for i in range(len(rows))
     if abs(cx[i]-mx)>limx or abs(cy[i]-my)>limy]
print(f"\n[FORA DE LOCALIZACAO] (>1.5x span): {len(far)}")
ft=Counter(r[1] for r in far)
for t,c in ft.most_common(): print(f"   {c:4d}  {t}")
for r in far[:15]: print(f"     #{r[0]} {r[1]} ({r[2]:.0f},{r[3]:.0f},{r[4]:.1f})")

# Z suspeito
zfar=[(rows[i][0],rows[i][1],cz[i]) for i in range(len(rows)) if cz[i]<-15 or cz[i]>70]
print(f"\n[Z fora de [-15,70]]: {len(zfar)}")
for r in zfar[:15]: print(f"   #{r[0]} {r[1]} Z={r[2]:.1f}")

# integridade
import math as _m
pts=m.by_type("IfcCartesianPoint")
badp=sum(1 for p in pts if any((v is None or not _m.isfinite(v)) for v in (p.Coordinates or [])))
print(f"\n[INTEGRIDADE] IfcCartesianPoint invalidos: {badp} / {len(pts)}")
gs=[e.GlobalId for e in m.by_type("IfcRoot")]
print(f"GUIDs unicos: {len(gs)==len(set(gs))}")

# vista em planta
fig,ax=plt.subplots(figsize=(15,15))
tps=sorted(set(types)); cmap=plt.get_cmap("tab20",len(tps))
ci={t:cmap(i) for i,t in enumerate(tps)}
ax.scatter(cx,cy,s=3,c=[ci[t] for t in types],alpha=0.5)
if far: ax.scatter([r[2] for r in far],[r[3] for r in far],c="red",s=60,marker="x",label=f"fora de local ({len(far)})",zorder=5)
ax.set_aspect("equal"); ax.grid(alpha=0.2)
ax.set_title("HVG v101 - posicao (placement) de cada elemento em planta")
if far: ax.legend()
plt.savefig("HVG_v101_Auditoria_Planta.png",dpi=90,bbox_inches="tight")
print("salvo HVG_v101_Auditoria_Planta.png")
