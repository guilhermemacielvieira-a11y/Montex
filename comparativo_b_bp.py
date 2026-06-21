#!/usr/bin/env python3
"""Comparativos IFC x desenho: Bloco B (corte - meio-nivel) e Bloco Principal (fachada)."""
import pickle, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
data=pickle.load(open("meshes.pkl","rb"))
COL={"wall":"#9b9b9b","col":"#b5402f","beam":"#8e6e53","slab":"#c08a3e","win":"#6fb3de",
     "door":"#caa05a","roof":"#7a7a7a","cov":"#cdae86","rail":"#7fc7e8","stair":"#a98fc4"}

def proj(tris,plane="xz"):
    polys=[];cols=[];dep=[]
    for cat,tri in tris:
        if plane=="xz": polys.append(tri[:,[0,2]]); dep.append(tri[:,1].mean())
        else: polys.append(tri[:,[1,2]]); dep.append(-tri[:,0].mean())
        cols.append(COL.get(cat,"#ccc"))
    idx=np.argsort([-d for d in dep])
    return PolyCollection([polys[i] for i in idx],facecolors=[cols[i] for i in idx],edgecolors=(0,0,0,0.2),linewidths=0.15)

# ---------- BLOCO B: CORTE (meio-nivel) projetando YZ (perfil) ----------
trisB=[(cat,v[t]) for bld,st,cat,v,f in data if bld=="B" for t in f]
allB=np.vstack([t for _,t in trisB])
fig,ax=plt.subplots(figsize=(15,11))
ax.add_collection(proj(trisB,"yz"))
y0,y1=allB[:,1].min(),allB[:,1].max(); z0,z1=allB[:,2].min(),allB[:,2].max()
pisos=[1.8,4.6,7.4]; nomes=["SubSolo (N -2.80)","Terreo (N 0.00)","Pav.1 (N +2.80)"]
for z,nm in zip(pisos,nomes):
    ax.axhline(z,color="#1b6",lw=0.8,ls="--",alpha=0.6); ax.text(y1+0.5,z,f"PISO {nm}",fontsize=8,color="#1b6",va="center")
yb=y0-2
for i in range(len(pisos)-1):
    ax.annotate("",(yb,pisos[i+1]),(yb,pisos[i]),arrowprops=dict(arrowstyle="<->",lw=0.9)); ax.text(yb-0.6,(pisos[i]+pisos[i+1])/2,"2.80\n(2.60+0.20)",ha="right",va="center",fontsize=8,fontweight="bold")
ax.plot([y0,y0+10],[z0-1.2,z0-1.2],color="k",lw=2); ax.text(y0+5,z0-0.9,"10 m",ha="center",fontsize=8)
ax.set_aspect("equal"); ax.set_xlim(y0-6,y1+8); ax.set_ylim(z0-2.5,z1+2)
ax.set_title("COMPARATIVO IFC x DESENHO - BLOCO B (CORTE/PERFIL)\nMeio-nivel: SubSolo a montante, Pav.1 a jusante - conforme Cortes A-B/C-D do projeto",fontsize=12)
ax.set_xlabel("Y (m) - profundidade/encosta"); ax.set_ylabel("cota Z (m)")
ax.legend(handles=[Patch(facecolor=COL["win"],label="Esquadrias"),Patch(facecolor=COL["rail"],label="Guarda-corpo (corrigido)"),
                   Patch(facecolor=COL["col"],label="Pilares"),Patch(facecolor=COL["slab"],label="Laje"),Patch(facecolor=COL["roof"],label="Cobertura plana")],loc="upper right",fontsize=8)
plt.tight_layout(); plt.savefig("HVG_Comparativo_BlocoB_Corte.pdf",dpi=150); plt.savefig("HVG_Comparativo_BlocoB_Corte.png",dpi=120); plt.close()

# ---------- BLOCO PRINCIPAL: FACHADA (pavilhao + cobertura piramidal) ----------
trisP=[(cat,v[t]) for bld,st,cat,v,f in data if bld=="BP" for t in f]
allP=np.vstack([t for _,t in trisP])
fig,ax=plt.subplots(figsize=(17,10))
ax.add_collection(proj(trisP,"xz"))
x0,x1=allP[:,0].min(),allP[:,0].max(); z0,z1=allP[:,2].min(),allP[:,2].max()
pisos=[13.05,16.05]; nomes=["Subsolo (N -3.00)","Terreo (N 0.00)"]
for z,nm in zip(pisos,nomes):
    ax.axhline(z,color="#1b6",lw=0.8,ls="--",alpha=0.6); ax.text(x1+1,z,f"PISO {nm}",fontsize=8,color="#1b6",va="center")
ax.annotate("",(x0-2.5,16.05),(x0-2.5,13.05),arrowprops=dict(arrowstyle="<->",lw=0.9)); ax.text(x0-3.2,14.5,"3.00",ha="right",va="center",fontsize=9,fontweight="bold")
ax.annotate("",(x1+4,z1),(x1+4,16.05),arrowprops=dict(arrowstyle="<->",lw=1.0)); ax.text(x1+4.8,(16.05+z1)/2,f"Cobertura\npiramidal\nH={z1-16.05:.1f}m",ha="left",va="center",fontsize=8,fontweight="bold")
ax.plot([x0,x0+10],[z0-1.5,z0-1.5],color="k",lw=2); ax.text(x0+5,z0-1.1,"10 m",ha="center",fontsize=8)
ax.plot([x0-3.5,x1+1],[13.05,13.05],color="k",lw=1.2)
ax.set_aspect("equal"); ax.set_xlim(x0-7,x1+10); ax.set_ylim(z0-3,z1+2)
ax.set_title("COMPARATIVO IFC x DESENHO - BLOCO PRINCIPAL FACHADA\nPavilhao aberto (malha de pilares) + cobertura piramidal ceramica - pe-direito 3.00m",fontsize=12)
ax.set_xlabel("X (m)"); ax.set_ylabel("cota Z (m)")
ax.legend(handles=[Patch(facecolor=COL["col"],label="Pilares (malha 4.97m)"),Patch(facecolor=COL["roof"],label="Cobertura piramidal"),
                   Patch(facecolor=COL["win"],label="Esquadrias"),Patch(facecolor=COL["wall"],label="Vedacoes")],loc="upper left",fontsize=8)
plt.tight_layout(); plt.savefig("HVG_Comparativo_BP_Fachada.pdf",dpi=150); plt.savefig("HVG_Comparativo_BP_Fachada.png",dpi=120); plt.close()
print("Comparativos B e BP gerados.")
print(f"Bloco B: Y[{y0:.0f},{y1:.0f}] Z[{z0:.1f},{z1:.1f}] | BP: X[{x0:.0f},{x1:.0f}] Z[{z0:.1f},{z1:.1f}]")
