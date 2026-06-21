import pickle, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
data=pickle.load(open("meshes4.pkl","rb"))
COL={"wall":"#9b9b9b","col":"#b5402f","beam":"#8e6e53","slab":"#c08a3e","win":"#6fb3de","door":"#caa05a","roof":"#7a7a7a","rail":"#7fc7e8","stair":"#a98fc4"}
NAMES={"SPA":"SPA (c/ piscina interior)","RP":"Restaurante da Piscina","NEP":"Clube NEP (Kids)","GUA":"Guarita"}
fig,axs=plt.subplots(2,2,figsize=(18,11))
for ax,(key,title) in zip(axs.flat,NAMES.items()):
    tris=[(cat,v[t]) for bld,cat,v,f in data if bld==key for t in f]
    if not tris: ax.set_visible(False); continue
    allv=np.vstack([t for _,t in tris]); ycen=np.median(allv[:,1])
    front=[(cat,tri) for cat,tri in tris if tri[:,1].mean()<=ycen+1.0]
    polys=[];cols=[];dep=[]
    for cat,tri in front: polys.append(tri[:,[0,2]]);cols.append(COL.get(cat,"#ccc"));dep.append(tri[:,1].mean())
    idx=np.argsort([-d for d in dep])
    ax.add_collection(PolyCollection([polys[i] for i in idx],facecolors=[cols[i] for i in idx],edgecolors=(0,0,0,0.25),linewidths=0.2))
    x0,x1=allv[:,0].min(),allv[:,0].max(); z0,z1=allv[:,2].min(),allv[:,2].max()
    ax.plot([x0,x0+5],[z0-0.7,z0-0.7],color="k",lw=2); ax.text(x0+2.5,z0-0.5,"5 m",ha="center",fontsize=7)
    ax.plot([x0-1,x1+1],[z0,z0],color="k",lw=1)
    ax.set_aspect("equal"); ax.set_xlim(x0-2,x1+2); ax.set_ylim(z0-1.5,z1+1)
    nwin=sum(1 for c,_ in tris if c=="win")
    ax.set_title(f"{title}  (H={z1-z0:.1f}m)",fontsize=11); ax.set_xlabel("X (m)"); ax.set_ylabel("Z (m)")
fig.suptitle("COMPARATIVO IFC - EDIFICIOS COMUNS: SPA, Restaurante da Piscina, Clube NEP, Guarita\n(janelas adicionadas a NEP e Guarita; coberturas e cotas verificadas)",fontsize=13)
fig.legend(handles=[Patch(facecolor=COL["col"],label="Pilares"),Patch(facecolor=COL["wall"],label="Paredes"),Patch(facecolor=COL["win"],label="Janelas (novas)"),Patch(facecolor=COL["roof"],label="Cobertura"),Patch(facecolor=COL["slab"],label="Laje")],loc="lower center",ncol=5,fontsize=9)
plt.tight_layout(rect=[0,0.04,1,0.96]); plt.savefig("HVG_Comparativo_Comuns_SPA_RP_NEP_Guarita.pdf",dpi=150); plt.savefig("HVG_Comparativo_Comuns_SPA_RP_NEP_Guarita.png",dpi=110)
print("Comparativo dos 4 edificios comuns gerado.")
