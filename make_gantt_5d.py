#!/usr/bin/env python3
"""Gantt do cronograma 4D + recalculo 5D sobre v91 (materiais completos)."""
import ifcopenshell, csv, json
from datetime import datetime
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
m=ifcopenshell.open("HVG_MASTER_v91_consolidado.ifc")

# ---- GANTT ----
tasks=[]
for t in m.by_type("IfcTask"):
    tt=t.TaskTime
    st=datetime.fromisoformat(tt.ScheduleStart); fi=datetime.fromisoformat(tt.ScheduleFinish)
    # n elementos vinculados
    n=0
    for r in m.by_type("IfcRelAssignsToProcess"):
        if r.RelatingProcess==t: n=len(r.RelatedObjects)
    tasks.append((t.Identification,t.Name,st,fi,n))
tasks.sort(key=lambda x:x[2])
fig,ax=plt.subplots(figsize=(14,6))
colors=plt.cm.tab10.colors
for i,(tid,nm,st,fi,n) in enumerate(tasks):
    ax.barh(i,(fi-st).days,left=st,height=0.55,color=colors[i%10],edgecolor="k",lw=0.5)
    ax.text(st,i,f" {tid} {nm} ({n} elem)",va="center",ha="left",fontsize=8,fontweight="bold")
ax.set_yticks(range(len(tasks))); ax.set_yticklabels([t[0] for t in tasks])
ax.invert_yaxis()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
plt.xticks(rotation=45,fontsize=8)
ax.set_title("HVG BRUMADINHO - CRONOGRAMA 4D (IfcWorkSchedule)\nFases construtivas - elementos vinculados ao IFC",fontsize=12)
ax.grid(axis="x",ls=":",alpha=0.5)
plt.tight_layout(); plt.savefig("HVG_Cronograma_4D_Gantt.pdf",dpi=150); plt.savefig("HVG_Cronograma_4D_Gantt.png",dpi=130)
print("Gantt gerado.")
# csv cronograma
with open("HVG_v91_Cronograma_4D.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["ID","Fase","Inicio","Fim","Dias","N_Elementos"])
    for tid,nm,st,fi,n in tasks: w.writerow([tid,nm,st.date(),fi.date(),(fi-st).days,n])

# ---- 5D RECALC (materiais completos) ----
def qty(el,*names):
    want=set(names)
    for r in el.IsDefinedBy:
        if r.is_a("IfcRelDefinesByProperties") and r.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
            for q in r.RelatingPropertyDefinition.Quantities:
                if q.Name in want:
                    for a in ("VolumeValue","AreaValue","LengthValue"):
                        v=getattr(q,a,None)
                        if v is not None: return float(v)
    return 0.0
def matn(el):
    for r in el.HasAssociations:
        if r.is_a("IfcRelAssociatesMaterial") and r.RelatingMaterial.is_a("IfcMaterial"): return r.RelatingMaterial.Name
    return "(sem material)"
import ifcopenshell.util.element as E
def in_storey(el):
    c=E.get_container(el); return c is not None and c.is_a("IfcBuildingStorey")
geomj=json.load(open("takeoff_geom_v91.json")) if False else None
# pavimentacao por material agora (deveria ter 0 sem material)
from collections import defaultdict
site_pav=defaultdict(float); nm=0
for sl in m.by_type("IfcSlab"):
    if not in_storey(sl):
        site_pav[matn(sl)]+=qty(sl,"GrossArea","NetArea")
        if matn(sl)=="(sem material)": nm+=1
print("\n=== Pavimentacao de site por material (v91) ===")
for k,v in sorted(site_pav.items(),key=lambda x:-x[1]): print(f"  {k:34} {round(v,1):>9} m2")
print("Lajes site sem material:",nm)
