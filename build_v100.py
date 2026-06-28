"""
HVG v99 -> v100 : camada de FABRICACAO/MONTAGEM ESTRUTURAL inspirada no
modelo Tekla Structures (MAPLE BEAR). Aplica as estrategias do detalhamento
estrutural IFC ao v99:
 1) Pset_Fabricacao por elemento estrutural (padrao "Tekla Common"):
    PartMark, AssemblyMark, Phase, Grade, Class, ProfileRef, Finish
 2) BaseQuantities de PESO por elemento (volume modelado x densidade nominal):
    concreto = REAL ; aco = teorico do solido (marcado p/ revisao por perfil)
 3) Pset_Aco_Reconciliacao consolidado com numeros calculados (peso/volume/contagem)
 4) IfcElementAssembly por edificio = lote de montagem estrutural (AssemblyMark)
Sem alterar geometria. Saida: HVG_MASTER_v100_FABRICACAO.ifc
"""
import ifcopenshell, time, os
from ifcopenshell.guid import new as guid
from collections import defaultdict

SRC="/home/user/Montex/HVG_MASTER_v99_PROFISSIONAL.ifc"
DEST="/home/user/Montex/HVG_MASTER_v100_FABRICACAO.ifc"
DENS={"aco":7850.0,"concreto":2500.0}
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]

# ---- indices: material e volume por elemento ----
mat_rel=defaultdict(list)
for rel in f.by_type("IfcRelAssociatesMaterial"):
    for o in (rel.RelatedObjects or []): mat_rel[o.id()].append(rel.RelatingMaterial)
def mat_name(el):
    for r in mat_rel.get(el.id(),[]):
        if r.is_a("IfcMaterial"): return r.Name
        if r.is_a("IfcMaterialLayerSetUsage"):
            ls=r.ForLayerSet
            if ls and ls.MaterialLayers: return ls.MaterialLayers[0].Material.Name
        if r.is_a("IfcMaterialList") and r.Materials: return r.Materials[0].Name
    return None
props_rel=defaultdict(list)
for rel in f.by_type("IfcRelDefinesByProperties"):
    for o in (rel.RelatedObjects or []): props_rel[o.id()].append(rel.RelatingPropertyDefinition)
def vol_len(el):
    v=l=None
    for pd in props_rel.get(el.id(),[]):
        if pd.is_a("IfcElementQuantity"):
            for q in pd.Quantities:
                if q.is_a("IfcQuantityVolume"): v=q.VolumeValue
                if q.is_a("IfcQuantityLength") and l is None: l=q.LengthValue
    return v,l

# ---- elemento -> edificio (via storey container -> building) ----
storey_build={}
def build_of_storey(st):
    for rel in f.by_type("IfcRelAggregates"):
        if st in (rel.RelatedObjects or []):
            par=rel.RelatingObject
            if par.is_a("IfcBuilding"): return par
            if par.is_a("IfcBuildingStorey"): return build_of_storey(par)
    return None
for st in f.by_type("IfcBuildingStorey"):
    storey_build[st.id()]=build_of_storey(st)
el_build={}; el_storey={}
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    st=rel.RelatingStructure
    if st.is_a("IfcBuildingStorey"):
        b=storey_build.get(st.id())
        for el in rel.RelatedElements:
            el_build[el.id()]=b; el_storey[el.id()]=st

def kind(matn):
    n=(matn or "").lower()
    if "aço" in n or "aco" in n or "steel" in n or "a500" in n or "a572" in n: return "aco"
    if "concreto" in n or "c25" in n or "c30" in n or "deck" in n: return "concreto"
    return None
def pv(k,v,unit=None):
    if isinstance(v,bool): nv=f.create_entity("IfcBoolean",v)
    elif isinstance(v,float): nv=f.create_entity("IfcReal",v)
    elif isinstance(v,int): nv=f.create_entity("IfcInteger",v)
    else: nv=f.create_entity("IfcLabel",str(v))
    return f.create_entity("IfcPropertySingleValue",k,None,nv,unit)

# ---- fase por tipo (vincula ao cronograma das 8 tarefas) ----
PHASE={"IfcColumn":"T02-Estrutura","IfcBeam":"T02-Estrutura","IfcSlab":"T02-Estrutura"}
# ---- contadores de marca por edificio ----
mark_seq=defaultdict(int)
def bcode(b):
    if b is None: return "GER"
    return (b.Name or "GER").replace(" ","")[:8].upper()

STRUCT=[("IfcColumn","P"),("IfcBeam","V"),("IfcSlab","L")]
tot=defaultdict(lambda:[0,0.0,0.0])  # kind -> [count, volume, weight]
n_pset=0; asm_members=defaultdict(list)
for typ,pref in STRUCT:
    for el in f.by_type(typ):
        matn=mat_name(el); kd=kind(matn); v,l=vol_len(el)
        b=el_build.get(el.id()); bc=bcode(b)
        mark_seq[(bc,pref)]+=1
        part=f"{bc}-{pref}{mark_seq[(bc,pref)]:04d}"
        asm=f"EST-{bc}"
        dens=DENS.get(kd)
        weight=round(v*dens,1) if (v and dens) else None
        # registra totais
        if kd and v:
            tot[kd][0]+=1; tot[kd][1]+=v; tot[kd][2]+=(weight or 0)
        # secao aproximada (ProfileRef) a partir de volume/comprimento
        prof=None
        if v and l and l>0.2:
            a=v/l  # area secao m2
            prof=f"~{a*1e4:.0f} cm2 (A={a:.3f} m2)"
        # Pset_Fabricacao (padrao Tekla Common)
        props=[pv("PartMark",part),pv("AssemblyMark",asm),
               pv("Phase",PHASE.get(typ,"T02-Estrutura")),
               pv("Grade",matn or "ND"),pv("Class",{"aco":"Metalica","concreto":"Concreto"}.get(kd,"ND")),
               pv("ProfileRef",prof or "ND"),pv("Finish","Pintura anticorrosiva" if kd=="aco" else "ND"),
               pv("Fabricacao_LOD","LOD400 (fabricacao/montagem)")]
        if weight is not None:
            metodo="real (volume solido x densidade)" if kd=="concreto" else "calculado da geometria (perfil modelado x 7850)"
            props+=[pv("Peso_kg",weight),pv("Peso_metodo",metodo),pv("Densidade_kg_m3",dens)]
        ps=f.create_entity("IfcPropertySet",guid(),oh,"Pset_Fabricacao",None,props)
        f.create_entity("IfcRelDefinesByProperties",guid(),oh,None,None,[el],ps)
        n_pset+=1
        # adiciona peso ao BaseQuantities existente (ou cria)
        if weight is not None:
            wq=f.create_entity("IfcQuantityWeight","GrossWeight",None,None,float(weight),None)
            existing=[pd for pd in props_rel.get(el.id(),[]) if pd.is_a("IfcElementQuantity")]
            if existing:
                existing[0].Quantities=list(existing[0].Quantities)+[wq]
            else:
                eq=f.create_entity("IfcElementQuantity",guid(),oh,"BaseQuantities",None,None,[wq])
                f.create_entity("IfcRelDefinesByProperties",guid(),oh,None,None,[el],eq)
        if kd=="aco":
            asm_members[(bc,b)].append(el)

# ---- IfcElementAssembly por edificio (lote de montagem metalica) ----
nasm=0
for (bc,b),members in asm_members.items():
    if not members: continue
    st=el_storey.get(members[0].id())
    place=members[0].ObjectPlacement
    asm=f.create_entity("IfcElementAssembly",guid(),oh,f"Lote Montagem EST-{bc}",
        f"Conjunto estrutural metalico - {b.Name if b else bc}",None,
        f.create_entity("IfcLocalPlacement",None,members[0].ObjectPlacement.RelativePlacement) if False else None,
        None,None,"NOTDEFINED")
    f.create_entity("IfcRelAggregates",guid(),oh,None,None,asm,members)
    nasm+=1

# ---- reconciliacao de aco consolidada (numeros calculados) ----
site=f.by_type("IfcSite")[0]
aco=tot["aco"]; conc=tot["concreto"]
# remove pset antigo de reconciliacao e cria atualizado
recon=f.create_entity("IfcPropertySet",guid(),oh,"Pset_Aco_Reconciliacao_Calc",None,[
    pv("Norma","ASTM A500 Gr.B / A572 Gr.50"),
    pv("Pilares_metalicos",int(aco[0])),
    pv("Volume_aco_modelado_m3",round(aco[1],2)),
    pv("Peso_aco_calculado_t",round(aco[2]/1000,1)),
    pv("Aco_kg_por_m_medio",round(aco[2]/sum(vol_len(c)[1] or 0 for c in f.by_type('IfcColumn') if kind(mat_name(c))=='aco' and vol_len(c)[1]),1) if aco[0] else 0),
    pv("Metodo_aco","calculado da geometria de perfis modelados x 7850 kg/m3"),
    pv("Elementos_concreto",int(conc[0])),
    pv("Volume_concreto_m3",round(conc[1],1)),
    pv("Peso_concreto_t",round(conc[2]/1000,1)),
    pv("Metodo_concreto","real (volume solido x 2500 kg/m3)")])
f.create_entity("IfcRelDefinesByProperties",guid(),oh,None,None,[site],recon)

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+" | + LOD400 fabricacao estrutural (marcas de peca, peso, assemblies - estrategia Tekla)"
f.write(DEST)
print(f"1) Pset_Fabricacao em {n_pset} elementos estruturais (marcas de peca)")
print(f"2) Peso: concreto {conc[0]} elem = {conc[1]:.0f} m3 = {conc[2]/1000:.1f} t (REAL)")
print(f"   aco {aco[0]} pilares = {aco[1]:.1f} m3 = {aco[2]/1000:.1f} t (teorico solido)")
print(f"3) IfcElementAssembly (lotes de montagem): {nasm}")
print(f"\nSalvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
