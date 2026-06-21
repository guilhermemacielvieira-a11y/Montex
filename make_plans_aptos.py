#!/usr/bin/env python3
"""Pranchas cotadas dos blocos de apartamentos A e B (planta tipo)."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np
import ifcopenshell.util.element as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")
s=geom.settings(); s.set("use-world-coords",True)
def foot(el):
    try:
        sh=geom.create_shape(s,el); v=np.array(sh.geometry.verts).reshape(-1,3)
        return [float(v[:,0].min()),float(v[:,1].min()),float(v[:,0].max()),float(v[:,1].max())]
    except: return None
def sarea(sp):
    for r in sp.IsDefinedBy:
        if r.is_a("IfcRelDefinesByProperties") and r.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
            for q in r.RelatingPropertyDefinition.Quantities:
                if q.is_a("IfcQuantityArea") and "Net" in q.Name: return q.AreaValue
    return 0

def plan(blockname, storeyname, outname):
    b=[x for x in m.by_type("IfcBuilding") if x.Name==blockname][0]
    sts=[st for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==b]
    st=[x for x in sts if x.Name==storeyname][0]
    sub=[x for x in sts if "SubSolo" in (x.Name or "")]
    cols=[]
    for cs in (sub or [st]):
        cols+=[foot(e) for r in cs.ContainsElements for e in r.RelatedElements if e.is_a()=="IfcColumn"]
    cols=[c for c in cols if c]
    walls=[foot(e) for r in st.ContainsElements for e in r.RelatedElements if e.is_a()=="IfcWall"]; walls=[w for w in walls if w]
    spaces=[(sp,foot(sp)) for sp in m.by_type("IfcSpace") if E.get_aggregate(sp)==st]
    spaces=[(sp,f) for sp,f in spaces if f]
    allf=cols+walls+[f for _,f in spaces]
    X0=min(f[0] for f in allf); Y0=min(f[1] for f in allf); X1=max(f[2] for f in allf); Y1=max(f[3] for f in allf)
    fig,ax=plt.subplots(figsize=(15,11))
    cmap={"APT":"#cfe8cf","VAR":"#cfe0f5","IS":"#f5dccf","HALL":"#f0eccf"}
    for sp,f in spaces:
        nm=(sp.Name or ""); key=nm.split("-")[0][:3].upper()
        col=cmap.get(key,"#eeeeee")
        ax.add_patch(Rectangle((f[0],f[1]),f[2]-f[0],f[3]-f[1],facecolor=col,edgecolor="#999",lw=0.4,alpha=0.7))
        cx,cy=(f[0]+f[2])/2,(f[1]+f[3])/2
        lbl=(sp.LongName or sp.Name or "")[:14]
        ax.text(cx,cy,f"{lbl}\n{sarea(sp):.0f}m2",ha="center",va="center",fontsize=5.5)
    for a,bb,c,d in walls:
        ax.add_patch(Rectangle((a,bb),c-a,d-bb,facecolor="#555",edgecolor="#333",lw=0.3))
    for a,bb,c,d in cols:
        ax.add_patch(Rectangle((a,bb),c-a,d-bb,facecolor="#c0392b",edgecolor="k",lw=0.4))
    # eixos derivados das colunas
    xs=sorted(set(round((c[0]+c[2])/2,1) for c in cols)); ys=sorted(set(round((c[1]+c[3])/2,1) for c in cols))
    import string
    for i,x in enumerate(xs):
        ax.plot([x,x],[Y0-3,Y1+3],color="#3577c0",lw=0.5,ls=(0,(6,4)))
        ax.text(x,Y1+3.5,string.ascii_uppercase[i] if i<26 else f"A{i}",ha="center",va="bottom",color="#3577c0",fontsize=8,fontweight="bold")
    for i,y in enumerate(ys):
        ax.plot([X0-3,X1+3],[y,y],color="#3577c0",lw=0.5,ls=(0,(6,4)))
        ax.text(X0-3.5,y,str(i+1),ha="right",va="center",color="#3577c0",fontsize=8,fontweight="bold")
    # cotas X
    yb=Y0-5
    for i in range(len(xs)-1):
        ax.annotate("",(xs[i+1],yb),(xs[i],yb),arrowprops=dict(arrowstyle="<->",color="k",lw=0.5))
        ax.text((xs[i]+xs[i+1])/2,yb-0.6,f"{xs[i+1]-xs[i]:.2f}",ha="center",va="top",fontsize=6)
    if len(xs)>1:
        ax.annotate("",(xs[-1],yb-2.5),(xs[0],yb-2.5),arrowprops=dict(arrowstyle="<->",color="k",lw=0.9))
        ax.text((xs[0]+xs[-1])/2,yb-3.2,f"TOTAL {xs[-1]-xs[0]:.2f} m",ha="center",va="top",fontsize=8,fontweight="bold")
    # cotas Y
    xr=X1+5
    for i in range(len(ys)-1):
        ax.annotate("",(xr,ys[i+1]),(xr,ys[i]),arrowprops=dict(arrowstyle="<->",color="k",lw=0.5))
        ax.text(xr+0.6,(ys[i]+ys[i+1])/2,f"{ys[i+1]-ys[i]:.2f}",ha="left",va="center",fontsize=6,rotation=90)
    ax.set_aspect("equal"); ax.set_xlim(X0-9,X1+9); ax.set_ylim(Y0-9,Y1+7)
    ax.set_title(f"HVG BRUMADINHO - {blockname} - PLANTA TIPO ({storeyname}) cotada\nAmbientes, eixos e pilares - medidas em metros",fontsize=12)
    ax.legend(handles=[Patch(facecolor="#cfe8cf",label="Apartamento"),Patch(facecolor="#cfe0f5",label="Varanda"),
                       Patch(facecolor="#f5dccf",label="I.S."),Patch(facecolor="#f0eccf",label="Hall"),
                       Patch(facecolor="#c0392b",label="Pilar"),Patch(facecolor="#555",label="Parede")],loc="upper right",fontsize=7,ncol=2)
    plt.tight_layout(); plt.savefig(outname+".pdf",dpi=150); plt.savefig(outname+".png",dpi=120); plt.close()
    print(f"{outname}: {len(cols)} pilares, {len(walls)} paredes, {len(spaces)} ambientes, eixos {len(xs)}x{len(ys)}")

plan("Bloco-A-01","A01-Terreo","HVG_Prancha_BlocoA_Planta_Tipo")
plan("Bloco-B-13","B13-Terreo","HVG_Prancha_BlocoB_Planta_Tipo")
