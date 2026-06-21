#!/usr/bin/env python3
"""Gera pranchas cotadas (planta) a partir do IfcGrid e da geometria - PDF/PNG."""
import ifcopenshell, ifcopenshell.geom as geom, ifcopenshell.util.placement as Pl
import numpy as np, multiprocessing
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
s=geom.settings(); s.set("use-world-coords",True)

# grid axes
grid=m.by_type("IfcGrid")[0]
def axline(ax): 
    p=ax.AxisCurve.Points; return (np.array(p[0].Coordinates),np.array(p[1].Coordinates))
U=[(a.AxisTag,axline(a)) for a in grid.UAxes]  # verticais (X const)
Vv=[(a.AxisTag,axline(a)) for a in grid.VAxes] # horizontais (Y const)

# elementos do BP-Terreo (e subsolo p/ pilares) - footprints
def storey(n): return [st for st in m.by_type("IfcBuildingStorey") if st.Name==n][0]
def contained(stn):
    st=storey(stn); out=[]
    for r in st.ContainsElements: out+=list(r.RelatedElements)
    return out
def foot(el):
    try:
        sh=geom.create_shape(s,el); v=np.array(sh.geometry.verts).reshape(-1,3)
        return v[:,0].min(),v[:,1].min(),v[:,0].max(),v[:,1].max()
    except: return None

cols=[foot(c) for c in m.by_type("IfcColumn") if any(r.RelatingStructure.Name=="BP-Subsolo" for r in c.ContainedInStructure)]
cols=[c for c in cols if c]
walls=[foot(w) for w in contained("BP-Terreo") if w.is_a("IfcWall")]; walls=[w for w in walls if w]

xs=sorted(set(round(float(u[1][0][0]),2) for u in U))
ys=sorted(set(round(float(v[1][0][1]),2) for v in Vv))
x0,x1=min(u[1][0][0] for u in U),max(u[1][0][0] for u in U)
y0,y1=min(v[1][0][1] for v in Vv),max(v[1][0][1] for v in Vv)

fig,ax=plt.subplots(figsize=(16,16))
# walls
for a,b,c,d in walls:
    ax.add_patch(Rectangle((a,b),c-a,d-b,facecolor="#888",edgecolor="#444",lw=0.4))
# columns
for a,b,c,d in cols:
    ax.add_patch(Rectangle((a,b),c-a,d-b,facecolor="#c0392b",edgecolor="k",lw=0.5))
# grid lines + labels
for tag,(p1,p2) in U:
    ax.plot([p1[0],p2[0]],[y0-4,y1+4],color="#3577c0",lw=0.6,ls=(0,(8,4)))
    ax.text(p1[0],y1+5,tag,ha="center",va="bottom",color="#3577c0",fontsize=9,fontweight="bold")
    ax.text(p1[0],y0-5,tag,ha="center",va="top",color="#3577c0",fontsize=9,fontweight="bold")
for tag,(p1,p2) in Vv:
    ax.plot([x0-4,x1+4],[p1[1],p2[1]],color="#3577c0",lw=0.6,ls=(0,(8,4)))
    ax.text(x0-5,p1[1],tag,ha="right",va="center",color="#3577c0",fontsize=9,fontweight="bold")
    ax.text(x1+5,p1[1],tag,ha="left",va="center",color="#3577c0",fontsize=9,fontweight="bold")
# cotas (espacamento entre eixos X)  na base
yb=y0-9
for i in range(len(xs)-1):
    xa,xc=xs[i],xs[i+1]
    ax.annotate("",(xc,yb),(xa,yb),arrowprops=dict(arrowstyle="<->",color="k",lw=0.6))
    ax.text((xa+xc)/2,yb-1.2,f"{xc-xa:.2f}",ha="center",va="top",fontsize=7)
# cota total X
ax.annotate("",(xs[-1],yb-4),(xs[0],yb-4),arrowprops=dict(arrowstyle="<->",color="k",lw=1.0))
ax.text((xs[0]+xs[-1])/2,yb-5.5,f"TOTAL {xs[-1]-xs[0]:.2f} m",ha="center",va="top",fontsize=9,fontweight="bold")
# cotas Y na lateral
xb=x1+9
for i in range(len(ys)-1):
    ya,yc=ys[i],ys[i+1]
    ax.annotate("",(xb,yc),(xb,ya),arrowprops=dict(arrowstyle="<->",color="k",lw=0.6))
    ax.text(xb+1.2,(ya+yc)/2,f"{yc-ya:.2f}",ha="left",va="center",fontsize=7,rotation=90)
ax.set_aspect("equal"); ax.set_xlim(x0-16,x1+18); ax.set_ylim(y0-16,y1+10)
ax.set_title("HVG BRUMADINHO - BLOCO PRINCIPAL - PLANTA DE EIXOS E PILARES (cotada)\nEscala grafica em metros - eixos IfcGrid BP-EIXOS",fontsize=12)
ax.set_xlabel("X (m) - UTM SIRGAS 2000 23S relativo"); ax.set_ylabel("Y (m)")
ax.grid(False)
# legenda
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor="#c0392b",label="Pilares 30x30"),Patch(facecolor="#888",label="Paredes BP-Terreo"),
                   plt.Line2D([0],[0],color="#3577c0",ls="--",label="Eixos estruturais")],loc="upper right",fontsize=9)
plt.tight_layout()
plt.savefig("HVG_Prancha_BP_Planta_Eixos.pdf",dpi=150)
plt.savefig("HVG_Prancha_BP_Planta_Eixos.png",dpi=130)
print("Pranchas geradas: HVG_Prancha_BP_Planta_Eixos.pdf / .png")
print(f"Pilares plotados:{len(cols)} | paredes:{len(walls)} | eixos {len(U)}U x {len(Vv)}V")
print(f"Malha X: {xs[0]:.1f}..{xs[-1]:.1f} ({xs[-1]-xs[0]:.1f}m) | Y: {ys[0]:.1f}..{ys[-1]:.1f} ({ys[-1]-ys[0]:.1f}m)")
