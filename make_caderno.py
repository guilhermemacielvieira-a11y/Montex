#!/usr/bin/env python3
"""Gera fachadas/cortes/plantas do Bloco Principal e compila o CADERNO DE PRANCHAS (PDF unico)."""
import pickle, numpy as np, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
recs=pickle.load(open("bp_geom.pkl","rb"))
COL={"wall":"#777","col":"#c0392b","beam":"#8e6e53","slab":"#9aa0a6","win":"#5fa8d3",
     "door":"#caa05a","roof":"#b5651d","cov":"#cdae86","rail":"#999","stair":"#aa88cc"}
ZNAMES={"BP-Subsolo":13.05,"BP-Terreo":16.05}

def elevation(view):
    """view: 'S'(X vs Z, olha -Y), 'E'(Y vs Z, olha +X)"""
    fig,ax=plt.subplots(figsize=(16,9))
    if view=="S": ha,a0,a1="x", "x0","x1"; depth0,depth1="y0","y1"
    else: ha,a0,a1="y","y0","y1"; depth0,depth1="x0","x1"
    order=sorted(recs,key=lambda r:r[depth0])  # fundo->frente
    for r in order:
        if r['cat']=='slab': continue
        x=r[a0]; w=r[a1]-r[a0]; z=r['z0']; h=r['z1']-r['z0']
        ax.add_patch(Rectangle((x,z),max(w,0.05),max(h,0.05),facecolor=COL[r['cat']],edgecolor="#333",lw=0.3,alpha=0.9))
    allx=[r[a0] for r in recs]+[r[a1] for r in recs]; zmin=min(r['z0'] for r in recs); zmax=max(r['z1'] for r in recs)
    x0,x1=min(allx),max(allx)
    # cota de altura (pe-direito + total)
    xb=x0-3
    ax.annotate("",(xb,16.05),(xb,13.05),arrowprops=dict(arrowstyle="<->",lw=0.8)); ax.text(xb-1,14.5,"3.00",rotation=90,va="center",fontsize=8)
    ax.annotate("",(xb,zmax),(xb,16.05),arrowprops=dict(arrowstyle="<->",lw=0.8)); ax.text(xb-1,(16.05+zmax)/2,f"{zmax-16.05:.1f}",rotation=90,va="center",fontsize=8)
    ax.annotate("",(x1+3,zmax),(x1+3,zmin),arrowprops=dict(arrowstyle="<->",lw=1.2)); ax.text(x1+4,(zmin+zmax)/2,f"H TOTAL {zmax-zmin:.1f} m",rotation=90,va="center",fontsize=9,fontweight="bold")
    # linha de terreno
    ax.plot([x0-2,x1+2],[13.05,13.05],color="k",lw=1.2)
    ax.set_aspect("equal"); ax.set_xlim(x0-7,x1+8); ax.set_ylim(zmin-2,zmax+3)
    nm="FACHADA SUL" if view=="S" else "FACHADA LESTE"
    ax.set_title(f"HVG BRUMADINHO - BLOCO PRINCIPAL - {nm} (esquematica, cotas em m)",fontsize=13)
    ax.set_xlabel(f"{ha.upper()} (m)"); ax.set_ylabel("Z / cota (m)")
    leg=[Patch(facecolor=COL[k],label=v) for k,v in [("col","Pilares"),("roof","Cobertura"),("wall","Paredes"),("win","Esquadrias")]]
    ax.legend(handles=leg,loc="upper right",fontsize=8)
    plt.tight_layout(); return fig

def section(axis,pos,band=3.0):
    """axis='Y'(corte longitudinal, plano Y=pos, projeta X vs Z); 'X'(transversal, Y vs Z)"""
    fig,ax=plt.subplots(figsize=(16,9))
    if axis=="Y": a0,a1,c0,c1="x0","x1","y0","y1"; lab="LONGITUDINAL"
    else: a0,a1,c0,c1="y0","y1","x0","x1"; lab="TRANSVERSAL"
    sel=[r for r in recs if r[c0]<=pos+band and r[c1]>=pos-band]
    for r in sel:
        cut = r[c0]<=pos<=r[c1] and r['cat'] in ("slab","roof","beam")
        x=r[a0]; w=r[a1]-r[a0]; z=r['z0']; h=r['z1']-r['z0']
        ax.add_patch(Rectangle((x,z),max(w,0.05),max(h,0.05),facecolor=COL[r['cat']],
                     edgecolor="k" if cut else "#555",lw=1.4 if cut else 0.3,alpha=0.95 if cut else 0.75,
                     hatch="//" if cut and r['cat'] in ("slab","beam") else None))
    allx=[r[a0] for r in sel]+[r[a1] for r in sel]; zs=[r['z0'] for r in sel]+[r['z1'] for r in sel]
    x0,x1=min(allx),max(allx); zmin,zmax=min(zs),max(zs)
    ax.plot([x0-2,x1+2],[13.05,13.05],color="k",lw=1.2)
    ax.annotate("",(x1+3,zmax),(x1+3,zmin),arrowprops=dict(arrowstyle="<->",lw=1.2)); ax.text(x1+4,(zmin+zmax)/2,f"H {zmax-zmin:.1f} m",rotation=90,va="center",fontsize=9,fontweight="bold")
    ax.set_aspect("equal"); ax.set_xlim(x0-7,x1+8); ax.set_ylim(zmin-2,zmax+3)
    ax.set_title(f"HVG BRUMADINHO - BLOCO PRINCIPAL - CORTE {lab} ({axis}={pos:.0f}) cotas em m",fontsize=13)
    ax.set_ylabel("Z / cota (m)")
    plt.tight_layout(); return fig

def planta(storey):
    fig,ax=plt.subplots(figsize=(13,12))
    sel=[r for r in recs if r['storey']==storey]
    for r in sel:
        if r['cat']=='roof' and storey!="BP-Terreo": continue
        ax.add_patch(Rectangle((r['x0'],r['y0']),r['x1']-r['x0'],r['y1']-r['y0'],
                     facecolor=COL[r['cat']],edgecolor="#444",lw=0.3,alpha=0.8))
    ax.set_aspect("equal")
    ax.set_title(f"HVG BRUMADINHO - BLOCO PRINCIPAL - PLANTA {storey}",fontsize=13)
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")
    plt.tight_layout(); return fig

def cover_page():
    fig=plt.figure(figsize=(16,11)); fig.text(0.5,0.72,"VILA GALE COLLECTION - BRUMADINHO",ha="center",fontsize=26,fontweight="bold")
    fig.text(0.5,0.66,"Country Resort Hotel das Artes, Conference & SPA",ha="center",fontsize=16)
    fig.text(0.5,0.60,"CADERNO DE PRANCHAS - MODELO BIM CONSOLIDADO v91",ha="center",fontsize=18,color="#3577c0")
    idx=["01  Bloco Principal - Planta de Eixos e Pilares (cotada)","02  Bloco Principal - Planta Subsolo",
         "03  Bloco Principal - Planta Terreo/Cobertura","04  Bloco Principal - Fachada Sul",
         "05  Bloco Principal - Fachada Leste","06  Bloco Principal - Corte Longitudinal",
         "07  Bloco Principal - Corte Transversal","08  Bloco de Apartamentos A - Planta Tipo (cotada)",
         "09  Bloco de Apartamentos B - Planta Tipo (cotada)","10  Cronograma 4D (Gantt)"]
    for i,t in enumerate(idx): fig.text(0.30,0.46-i*0.032,t,fontsize=12,family="monospace")
    fig.text(0.5,0.06,"Grupo Montex Ltda - CNPJ 10.798.894/0001-60  |  Fase: Licenciamento  |  2026",ha="center",fontsize=10,color="#666")
    return fig

def img_page(path,title):
    fig,ax=plt.subplots(figsize=(16,11)); ax.imshow(mpimg.imread(path)); ax.axis("off")
    ax.set_title(title,fontsize=12); plt.tight_layout(); return fig

with PdfPages("HVG_Caderno_de_Pranchas.pdf") as pdf:
    pdf.savefig(cover_page()); plt.close()
    for p,t in [("HVG_Prancha_BP_Planta_Eixos.png","01 - BP Planta de Eixos e Pilares")]:
        pdf.savefig(img_page(p,t)); plt.close()
    pdf.savefig(planta("BP-Subsolo")); plt.close()
    pdf.savefig(planta("BP-Terreo")); plt.close()
    pdf.savefig(elevation("S")); plt.close()
    pdf.savefig(elevation("E")); plt.close()
    pdf.savefig(section("Y",245)); plt.close()
    pdf.savefig(section("X",165)); plt.close()
    for p,t in [("HVG_Prancha_BlocoA_Planta_Tipo.png","08 - Bloco A Planta Tipo"),
                ("HVG_Prancha_BlocoB_Planta_Tipo.png","09 - Bloco B Planta Tipo"),
                ("HVG_Cronograma_4D_Gantt.png","10 - Cronograma 4D")]:
        if glob.glob(p): pdf.savefig(img_page(p,t)); plt.close()
print("Caderno gerado: HVG_Caderno_de_Pranchas.pdf")
