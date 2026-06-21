#!/usr/bin/env python3
"""HVG v90 -> v91 CONSOLIDADO: completa materiais, cria IfcGrid e cronograma 4D
(IfcWorkSchedule + IfcTask por fase, com elementos vinculados via IfcRelAssignsToProcess)."""
import ifcopenshell, ifcopenshell.util.element as E, ifcopenshell.util.placement as Pl
import numpy as np, string
m=ifcopenshell.open("HVG_MASTER_v90_LOD300.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
def g(): return ifcopenshell.guid.new()

# ============ 1) MATERIAIS ============
def find_mat(name):
    for mt in m.by_type("IfcMaterial"):
        if mt.Name==name: return mt
    return m.create_entity("IfcMaterial",name)
def no_mat(el): return not any(r.is_a("IfcRelAssociatesMaterial") for r in el.HasAssociations)
def assoc(els,mat):
    if els: m.create_entity("IfcRelAssociatesMaterial",g(),oh,None,None,list(els),mat)
c25=find_mat("Concreto Armado C25"); c30=find_mat("Concreto Armado C30")
asf=find_mat("Pavimento Asfaltico CBUQ"); termo=find_mat("Termoplastico Sinalizacao Viaria"); terra=find_mat("Terra Vegetal Adubada")
assoc([w for w in m.by_type("IfcWall") if no_mat(w)],c30)
buckets={}
for s in m.by_type("IfcSlab"):
    if no_mat(s):
        ot=(s.ObjectType or "").lower()
        if "asfalt" in ot: k=asf
        elif "guia" in ot or "meio-fio" in ot or "plataforma" in ot: k=c25
        elif "faixa" in ot or "sinaliza" in ot: k=termo
        elif "canteiro" in ot or "horta" in ot: k=terra
        else: k=c25
        buckets.setdefault(k.id(),[]).append(s)
nmat=0
for mid,els in buckets.items(): assoc(els,m.by_id(mid)); nmat+=len(els)
print(f"[1] Materiais: paredes+{nmat} lajes associadas; pendencias agora:",
      sum(1 for s in m.by_type("IfcSlab") if no_mat(s))+sum(1 for w in m.by_type("IfcWall") if no_mat(w)))

# ============ 2) IfcGrid (Bloco Principal) ============
site_pl=m.by_type("IfcSite")[0].ObjectPlacement
def wpos(e): x=Pl.get_local_placement(e.ObjectPlacement)[:3,3]; return (round(float(x[0]),2),round(float(x[1]),2))
bp=[c for c in m.by_type("IfcColumn") if any(r.RelatingStructure.Name in("BP-Subsolo","BP-Terreo") for r in c.ContainedInStructure)]
xs=sorted({wpos(c)[0] for c in bp}); ys=sorted({wpos(c)[1] for c in bp})
def axis(tag,p1,p2):
    pl=m.create_entity("IfcPolyline",[m.create_entity("IfcCartesianPoint",[float(p1[0]),float(p1[1])]),
                                      m.create_entity("IfcCartesianPoint",[float(p2[0]),float(p2[1])])])
    return m.create_entity("IfcGridAxis",AxisTag=tag,AxisCurve=pl,SameSense=True)
y0,y1,x0,x1=min(ys)-2,max(ys)+2,min(xs)-2,max(xs)+2
uax=[axis(string.ascii_uppercase[i] if i<26 else f"A{i}",(x,y0),(x,y1)) for i,x in enumerate(xs)]
vax=[axis(str(i+1),(x0,y),(x1,y)) for i,y in enumerate(ys)]
gp=m.create_entity("IfcLocalPlacement",None,m.create_entity("IfcAxis2Placement3D",m.create_entity("IfcCartesianPoint",[0.,0.,0.]),None,None))
grid=m.create_entity("IfcGrid",GlobalId=g(),OwnerHistory=oh,Name="BP-EIXOS",Description="Malha estrutural Bloco Principal ~4.97m",ObjectPlacement=gp,UAxes=uax,VAxes=vax)
bpt=[s for s in m.by_type("IfcBuildingStorey") if s.Name=="BP-Terreo"][0]
rel=next((r for r in bpt.ContainsElements),None)
if rel: rel.RelatedElements=list(rel.RelatedElements)+[grid]
else: m.create_entity("IfcRelContainedInSpatialStructure",g(),oh,None,None,[grid],bpt)
print(f"[2] IfcGrid: {len(uax)}U x {len(vax)}V")

# ============ 3) CRONOGRAMA 4D ============
def date(y,mo,d): return f"{y:04d}-{mo:02d}-{d:02d}T08:00:00"
def tasktime(start,finish,days):
    return m.create_entity("IfcTaskTime",DurationType="WORKTIME",ScheduleDuration=f"P{days}D",
                           ScheduleStart=date(*start),ScheduleFinish=date(*finish))
wp=m.create_entity("IfcWorkPlan",GlobalId=g(),OwnerHistory=oh,Name="HVG-PlanejamentoObra",
                   Description="Planejamento de execucao HVG Brumadinho",Identification="WP-HVG",
                   CreationDate=date(2026,9,1),StartTime=date(2026,9,1),FinishTime=date(2028,10,31),PredefinedType="PLANNED")
ws=m.create_entity("IfcWorkSchedule",GlobalId=g(),OwnerHistory=oh,Name="HVG-Cronograma",
                   Description="Cronograma 4D por fase",Identification="CRON-HVG",
                   CreationDate=date(2026,9,1),StartTime=date(2026,9,1),FinishTime=date(2028,10,31),PredefinedType="PLANNED")
m.create_entity("IfcRelAggregates",g(),oh,None,None,wp,[ws])

# fases (nome, inicio(y,m,d), dur_dias, classificador de elementos)
def in_storey(el):
    c=E.get_container(el); return c is not None and c.is_a("IfcBuildingStorey")
def cls_phase(el):
    t=el.is_a()
    if t=="IfcWall" and (el.ObjectType or "").lower().find("retaining")>=0: return "Terraplenagem"
    if t=="IfcSlab" and not in_storey(el): return "Urbanismo"
    if t in("IfcColumn","IfcBeam"): return "Estrutura"
    if t=="IfcSlab": return "Estrutura"
    if t=="IfcWall": return "Vedacoes"
    if t in("IfcRoof",): return "Cobertura"
    if t in("IfcWindow","IfcDoor"): return "Esquadrias"
    if t in("IfcPipeSegment","IfcDuctSegment","IfcCableCarrierSegment","IfcCableSegment","IfcAirTerminal",
            "IfcFireSuppressionTerminal","IfcLightFixture","IfcElectricDistributionBoard","IfcCommunicationsAppliance",
            "IfcTransformer","IfcTank","IfcValve","IfcFlowController","IfcMember"): return "MEP"
    if t=="IfcCovering": return "Acabamentos"
    if t in("IfcGeographicElement","IfcFurniture","IfcRailing"): return "Urbanismo"
    return None
phases=[("Terraplenagem e Fundacoes",(2026,9,1),(2027,1,31),150),
        ("Estrutura",(2026,11,1),(2027,8,31),300),
        ("Vedacoes",(2027,3,1),(2027,12,31),300),
        ("Cobertura",(2027,6,1),(2028,1,31),240),
        ("Esquadrias",(2027,9,1),(2028,3,31),210),
        ("Instalacoes MEP",(2027,7,1),(2028,5,31),330),
        ("Acabamentos",(2027,11,1),(2028,8,31),270),
        ("Urbanismo e Paisagismo",(2028,3,1),(2028,10,31),240)]
# bucketize elements
elem_by_phase={p[0]:[] for p in phases}
namemap={"Terraplenagem":"Terraplenagem e Fundacoes","Estrutura":"Estrutura","Vedacoes":"Vedacoes",
         "Cobertura":"Cobertura","Esquadrias":"Esquadrias","MEP":"Instalacoes MEP","Acabamentos":"Acabamentos","Urbanismo":"Urbanismo e Paisagismo"}
for el in m.by_type("IfcElement"):
    if el.is_a("IfcOpeningElement"): continue
    ph=cls_phase(el)
    if ph and namemap[ph] in elem_by_phase: elem_by_phase[namemap[ph]].append(el)
tasks=[]
for i,(nm,st,fi,days) in enumerate(phases,1):
    tk=m.create_entity("IfcTask",GlobalId=g(),OwnerHistory=oh,Name=nm,Identification=f"T{i:02d}",
                       IsMilestone=False,TaskTime=tasktime(st,fi,days),PredefinedType="CONSTRUCTION")
    tasks.append((tk,nm))
    els=elem_by_phase[nm]
    if els: m.create_entity("IfcRelAssignsToProcess",g(),oh,None,None,els,None,tk,None)
m.create_entity("IfcRelAssignsToControl",g(),oh,None,None,[t for t,_ in tasks],None,ws)
print(f"[3] Cronograma 4D: {len(tasks)} fases, elementos vinculados:",{nm:len(elem_by_phase[nm]) for _,nm in tasks})

proj=m.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+(" | v91 CONSOLIDADO: materiais completados (0 pendencias), IfcGrid de eixos (BP), "
   "e cronograma 4D (IfcWorkSchedule + 8 IfcTask com elementos vinculados via IfcRelAssignsToProcess).")
m.write("HVG_MASTER_v91_consolidado.ifc")
print("Gravado: HVG_MASTER_v91_consolidado.ifc")
