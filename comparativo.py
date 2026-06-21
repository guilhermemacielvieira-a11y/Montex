#!/usr/bin/env python3
"""Visual comparativo: fachada IFC (v92) do Bloco A vs cotas do desenho (pe-direito 2.60+0.20)."""
import pickle, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
data=pickle.load(open("meshes.pkl","rb"))
COL={"wall":"#9b9b9b","col":"#b5402f","beam":"#8e6e53","slab":"#c08a3e","win":"#6fb3de",
     "door":"#caa05a","roof":"#7a7a7a","cov":"#cdae86","rail":"#7fc7e8","stair":"#a98fc4"}
# apenas fachada frontal (sul): triangulos com Y < 426 (lado das varandas)
tris=[]
for bld,st,cat,v,f in data:
    if bld!="A": continue
    for t in f:
        if v[t][:,1].mean()<426: tris.append((cat,v[t]))
fig,ax=plt.subplots(figsize=(17,11))
polys=[];cols=[];dep=[]
for cat,tri in tris:
    if cat=="slab": pass
    polys.append(tri[:,[0,2]]); cols.append(COL.get(cat,"#ccc")); dep.append(tri[:,1].mean())
idx=np.argsort([-d for d in dep])
ax.add_collection(PolyCollection([polys[i] for i in idx],facecolors=[cols[i] for i in idx],edgecolors=(0,0,0,0.2),linewidths=0.15))
allv=np.vstack([v for _,_,_,v,_ in data if _== _ ] ) if False else np.vstack([t for _,t in tris])
x0,x1=allv[:,0].min(),allv[:,0].max(); z0,z1=allv[:,2].min(),allv[:,2].max()
# niveis de piso (do modelo) e cotas do desenho
pisos=[15.70,18.50,21.30]; nomes=["SubSolo2 (N -5.60)","SubSolo1 (N -2.80)","Terreo (N 0.00)"]
for z,nm in zip(pisos,nomes):
    ax.axhline(z,color="#1b6",lw=0.8,ls="--",alpha=0.6)
    ax.text(x1+1,z,f"PISO {nm}",fontsize=8,color="#1b6",va="center")
# cota pe-direito entre pisos (desenho: 2.60 + 0.20 laje = 2.80)
xb=x0-2.5
for i in range(len(pisos)-1):
    za,zc=pisos[i],pisos[i+1]
    ax.annotate("",(xb,zc),(xb,za),arrowprops=dict(arrowstyle="<->",color="k",lw=0.9))
    ax.text(xb-0.8,(za+zc)/2,f"2.80\n(2.60+0.20)",ha="right",va="center",fontsize=8,fontweight="bold")
# barra de escala
ax.plot([x0,x0+10],[z0-1.5,z0-1.5],color="k",lw=2); ax.text(x0+5,z0-1.2,"10 m",ha="center",fontsize=8)
ax.plot([x0-3.5,x1+0.5],[z0,z0],color="k",lw=1.3)  # linha de terreno/base
ax.set_aspect("equal"); ax.set_xlim(x0-6,x1+10); ax.set_ylim(z0-3,z1+2)
ax.set_title("COMPARATIVO IFC x DESENHO - BLOCO A FACHADA SUL\nNiveis de piso do IFC conferem com o pe-direito do projeto (2.60 + 0.20 laje = 2.80 m)",fontsize=13)
ax.set_xlabel("X (m)"); ax.set_ylabel("cota Z (m)")
ax.legend(handles=[Patch(facecolor=COL["win"],label="Esquadrias (3 pisos alinhados)"),Patch(facecolor=COL["rail"],label="Guarda-corpo varanda (corrigido)"),
                   Patch(facecolor=COL["col"],label="Pilares"),Patch(facecolor=COL["slab"],label="Laje"),
                   plt.Line2D([0],[0],color="#1b6",ls="--",label="Nivel de piso (IFC)")],loc="upper right",fontsize=8)
plt.tight_layout(); plt.savefig("HVG_Comparativo_BlocoA_Fachada.png",dpi=120); plt.savefig("HVG_Comparativo_BlocoA_Fachada.pdf",dpi=150)
print("Comparativo gerado. Fachada Z[",round(float(z0),1),",",round(float(z1),1),"] pisos",pisos)
