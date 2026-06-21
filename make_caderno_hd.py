#!/usr/bin/env python3
"""Caderno HD: fachadas/cortes por projecao de malhas reais (BP, A, B) + carimbo ABNT."""
import pickle, numpy as np, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle, Patch
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
data=pickle.load(open("meshes.pkl","rb"))
COL={"wall":"#9b9b9b","col":"#b5402f","beam":"#8e6e53","slab":"#7f8a93","win":"#6fb3de",
     "door":"#caa05a","roof":"#bb6b2a","cov":"#cdae86","rail":"#888","stair":"#a98fc4"}
BNAME={"BP":"BLOCO PRINCIPAL","A":"BLOCO DE APARTAMENTOS A","B":"BLOCO DE APARTAMENTOS B"}

def tris_of(bld):
    out=[]
    for b,st,cat,v,f in data:
        if b!=bld: continue
        for t in f: out.append((cat,v[t]))   # (cat, 3x3)
    return out

def scalebar(ax,x,y,L=10,label=None):
    ax.plot([x,x+L],[y,y],color="k",lw=2)
    for xx in (x,x+L): ax.plot([xx,xx],[y,y+0.4],color="k",lw=2)
    ax.text(x+L/2,y+0.6,(label or f"{L} m"),ha="center",va="bottom",fontsize=8)

def selo(fig,numero,conteudo,subtit=""):
    # moldura
    fig.patches.append(Rectangle((0.018,0.02),0.964,0.96,fill=False,lw=1.5,transform=fig.transFigure,zorder=1000))
    # carimbo inferior direito
    x,y,w,h=0.62,0.025,0.362,0.135
    fig.patches.append(Rectangle((x,y),w,h,fill=True,facecolor="white",edgecolor="k",lw=1.2,transform=fig.transFigure,zorder=1001))
    for fx in (0.0,): pass
    T=fig.transFigure
    fig.text(x+0.006,y+h-0.022,"VILA GALE COLLECTION - BRUMADINHO",fontsize=9,fontweight="bold",transform=T,zorder=1002)
    fig.text(x+0.006,y+h-0.040,"Country Resort Hotel das Artes, Conference & SPA",fontsize=6.5,transform=T,zorder=1002)
    fig.text(x+0.006,y+0.052,conteudo,fontsize=9,fontweight="bold",transform=T,zorder=1002)
    if subtit: fig.text(x+0.006,y+0.036,subtit,fontsize=6.8,transform=T,zorder=1002)
    fig.text(x+0.006,y+0.018,"Grupo Montex Ltda - CREA 2101818418",fontsize=6,transform=T,zorder=1002)
    fig.text(x+0.006,y+0.006,"Fase: Licenciamento   Data: 06/2026",fontsize=6,transform=T,zorder=1002)
    # divisorias
    fig.text(x+w-0.075,y+h-0.022,"PRANCHA",fontsize=6,transform=T,zorder=1002)
    fig.text(x+w-0.075,y+0.02,numero,fontsize=20,fontweight="bold",transform=T,zorder=1002)
    fig.text(x+w-0.20,y+0.006,"ESC: barra grafica",fontsize=6,transform=T,zorder=1002)

def draw_proj(ax,tris,plane,depthfn,cut_band=None,cutfn=None):
    polys=[]; cols=[]; order=[]
    for cat,tri in tris:
        if cat=="slab" and plane in("xz","yz") and cut_band is None: continue
        if plane=="xz": p2=tri[:,[0,2]]; d=depthfn(tri)
        elif plane=="yz": p2=tri[:,[1,2]]; d=depthfn(tri)
        else: p2=tri[:,[0,1]]; d=tri[:,2].mean()
        is_cut=False
        if cut_band is not None:
            cc=cutfn(tri)
            if not(cc.min()<=cut_band[1] and cc.max()>=cut_band[0]): continue
            is_cut = cc.min()<=cut_band[2]<=cc.max()
        polys.append(p2); 
        c=COL[cat]; cols.append(c); order.append((d,is_cut))
    idx=np.argsort([-o[0] for o in order])  # longe -> perto
    P=[polys[i] for i in idx]; C=[cols[i] for i in idx]; CUT=[order[i][1] for i in idx]
    pc=PolyCollection(P,facecolors=C,edgecolors=[(0,0,0,0.25) if not c else (0,0,0,0.9) for c in CUT],
                      linewidths=[0.15 if not c else 0.7 for c in CUT])
    ax.add_collection(pc)

def fachada(bld,view):
    tris=tris_of(bld)
    fig,ax=plt.subplots(figsize=(16,11))
    if view=="S": draw_proj(ax,tris,"xz",lambda t:t[:,1].mean()); hx="x"
    elif view=="E": draw_proj(ax,tris,"yz",lambda t:-t[:,0].mean()); hx="y"
    allv=np.vstack([t for _,t in tris])
    if view=="S": h0,h1=allv[:,0].min(),allv[:,0].max()
    else: h0,h1=allv[:,1].min(),allv[:,1].max()
    z0,z1=allv[:,2].min(),allv[:,2].max()
    ax.plot([h0-2,h1+2],[z0,z0],color="k",lw=1.3)
    ax.annotate("",(h1+3,z1),(h1+3,z0),arrowprops=dict(arrowstyle="<->",lw=1.0))
    ax.text(h1+3.8,(z0+z1)/2,f"H {z1-z0:.1f} m",rotation=90,va="center",fontsize=9,fontweight="bold")
    scalebar(ax,h0,z0-2.0,10)
    ax.set_aspect("equal"); ax.set_xlim(h0-7,h1+9); ax.set_ylim(z0-4,z1+3)
    ax.set_title(f"{BNAME[bld]} - FACHADA {'SUL' if view=='S' else 'LESTE'}",fontsize=13)
    ax.set_xlabel(f"{hx.upper()} (m)"); ax.set_ylabel("cota Z (m)"); ax.grid(False)
    plt.tight_layout(rect=[0.02,0.17,0.98,0.98]); return fig

def corte(bld,axis,pos,band=2.0):
    tris=tris_of(bld)
    fig,ax=plt.subplots(figsize=(16,11))
    if axis=="Y": draw_proj(ax,tris,"xz",lambda t:t[:,1].mean(),(pos-band,pos+band,pos),lambda t:t[:,1]); hx="x"; lab="LONGITUDINAL"
    else: draw_proj(ax,tris,"yz",lambda t:t[:,0].mean(),(pos-band,pos+band,pos),lambda t:t[:,0]); hx="y"; lab="TRANSVERSAL"
    allv=np.vstack([t for _,t in tris]); z0,z1=allv[:,2].min(),allv[:,2].max()
    h0,h1=(allv[:,0].min(),allv[:,0].max()) if axis=="Y" else (allv[:,1].min(),allv[:,1].max())
    ax.plot([h0-2,h1+2],[z0,z0],color="k",lw=1.3); scalebar(ax,h0,z0-2.0,10)
    ax.annotate("",(h1+3,z1),(h1+3,z0),arrowprops=dict(arrowstyle="<->",lw=1.0)); ax.text(h1+3.8,(z0+z1)/2,f"H {z1-z0:.1f} m",rotation=90,va="center",fontsize=9,fontweight="bold")
    ax.set_aspect("equal"); ax.set_xlim(h0-7,h1+9); ax.set_ylim(z0-4,z1+3)
    ax.set_title(f"{BNAME[bld]} - CORTE {lab} ({axis}={pos:.0f})",fontsize=13)
    ax.set_xlabel(f"{hx.upper()} (m)"); ax.set_ylabel("cota Z (m)")
    plt.tight_layout(rect=[0.02,0.17,0.98,0.98]); return fig

def img_page(path,title):
    fig,ax=plt.subplots(figsize=(16,11)); ax.imshow(mpimg.imread(path)); ax.axis("off"); ax.set_title(title,fontsize=12)
    plt.tight_layout(rect=[0.02,0.17,0.98,0.98]); return fig

def cover():
    fig=plt.figure(figsize=(16,11))
    fig.text(0.5,0.74,"VILA GALE COLLECTION - BRUMADINHO",ha="center",fontsize=26,fontweight="bold")
    fig.text(0.5,0.68,"Country Resort Hotel das Artes, Conference & SPA",ha="center",fontsize=15)
    fig.text(0.5,0.62,"CADERNO DE PRANCHAS - MODELO BIM v91 (alta fidelidade)",ha="center",fontsize=16,color="#3577c0")
    items=["01 BP - Planta de Eixos e Pilares","02 BP - Fachada Sul","03 BP - Fachada Leste",
           "04 BP - Corte Longitudinal","05 BP - Corte Transversal","06 Bloco A - Planta Tipo",
           "07 Bloco A - Fachada Sul","08 Bloco A - Corte Transversal","09 Bloco B - Planta Tipo",
           "10 Bloco B - Fachada Sul","11 Cronograma 4D"]
    for i,t in enumerate(items): fig.text(0.32,0.50-i*0.030,t,fontsize=11,family="monospace")
    return fig

with PdfPages("HVG_Caderno_de_Pranchas_HD.pdf") as pdf:
    f=cover(); pdf.savefig(f); plt.close()
    pages=[]
    pages.append((img_page("HVG_Prancha_BP_Planta_Eixos.png","BP - PLANTA DE EIXOS E PILARES"),"01","Planta de Eixos e Pilares - Bloco Principal"))
    pages.append((fachada("BP","S"),"02","Fachada Sul - Bloco Principal"))
    pages.append((fachada("BP","E"),"03","Fachada Leste - Bloco Principal"))
    pages.append((corte("BP","Y",245),"04","Corte Longitudinal - Bloco Principal"))
    pages.append((corte("BP","X",165),"05","Corte Transversal - Bloco Principal"))
    pages.append((img_page("HVG_Prancha_BlocoA_Planta_Tipo.png","BLOCO A - PLANTA TIPO"),"06","Planta Tipo - Bloco de Apartamentos A"))
    pages.append((fachada("A","S"),"07","Fachada Sul - Bloco de Apartamentos A"))
    pages.append((corte("A","X",60),"08","Corte Transversal - Bloco de Apartamentos A"))
    pages.append((img_page("HVG_Prancha_BlocoB_Planta_Tipo.png","BLOCO B - PLANTA TIPO"),"09","Planta Tipo - Bloco de Apartamentos B"))
    pages.append((fachada("B","S"),"10","Fachada Sul - Bloco de Apartamentos B"))
    pages.append((img_page("HVG_Cronograma_4D_Gantt.png","CRONOGRAMA 4D"),"11","Cronograma 4D - IfcWorkSchedule"))
    for fig,num,cont in pages:
        selo(fig,num,cont); pdf.savefig(fig); plt.close(fig)
print("Caderno HD gerado.")
