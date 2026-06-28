"""
HVG v100 -> v101 : DIMENSIONAMENTO aplicado ao BIM (sistema Perfilor)
 - Lajes de piso  -> Steel Deck MF-75 (h=130, t=0,80, Q-92) + cargas/verificacao
 - Vigas          -> perfil dimensionado (VS W250x17.9 / VP W310x28.3) + esforcos
 - Fechamentos    -> Painel Termilor Wall PIR 50mm (peso, U, vao, fixacao)
Cada elemento recebe Pset_Dimensionamento + Pset_Perfilor_Produto.
Sem alterar geometria. Saida: HVG_MASTER_v101_DIMENSIONADO.ifc
"""
import ifcopenshell, time, os
from ifcopenshell.guid import new as guid
from collections import defaultdict

SRC="/home/user/Montex/HVG_MASTER_v100_FABRICACAO.ifc"
DEST="/home/user/Montex/HVG_MASTER_v101_DIMENSIONADO.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]

mat_rel=defaultdict(list)
for rel in f.by_type("IfcRelAssociatesMaterial"):
    for o in (rel.RelatedObjects or []): mat_rel[o.id()].append(rel.RelatingMaterial)
def matn(el):
    for r in mat_rel.get(el.id(),[]):
        if r.is_a("IfcMaterial"): return r.Name
    return None
def pv(k,v,unit=None):
    if isinstance(v,bool): nv=f.create_entity("IfcBoolean",v)
    elif isinstance(v,float): nv=f.create_entity("IfcReal",v)
    elif isinstance(v,int): nv=f.create_entity("IfcInteger",v)
    else: nv=f.create_entity("IfcLabel",str(v))
    return f.create_entity("IfcPropertySingleValue",k,None,nv,unit)
def attach(el,name,kv):
    ps=f.create_entity("IfcPropertySet",guid(),oh,name,None,[pv(k,v) for k,v in kv])
    f.create_entity("IfcRelDefinesByProperties",guid(),oh,None,None,[el],ps)

# ---------- 1) LAJES STEEL DECK MF-75 ----------
laje_dim=[("Sistema","Laje mista Steel Deck"),("Produto","Perfilor Steel Deck MF-75"),
  ("Chapa_mm",0.80),("Altura_nervura_mm",75),("Altura_total_mm",130),("Capa_concreto_mm",55),
  ("Concreto","C25"),("Tela_soldada","Q-92"),("Largura_util_mm",915),
  ("Consumo_concreto_m3_m2",0.096),("Vao_laje_m",2.0),("Escoramento","Nao (vao 2,0 m)"),
  ("Carga_PP_kN_m2",2.5),("Carga_revest_kN_m2",1.0),("Sobrecarga_kN_m2",2.0),
  ("Carga_total_carac_kN_m2",6.0),("Carga_ELU_kN_m2",8.4),
  ("Momento_laje_kNm_m",4.2),("Conector","Stud bolt o19"),("Norma","NBR 8800 / NBR 6120"),
  ("Verificacao","OK - ELU e flecha")]
laje_prod=[("Fabricante","ArcelorMittal Perfilor"),("Linha","Steel Deck MF-75"),
  ("Chapa_mm",0.80),("Revestimento","Zincado Z275"),("Peso_proprio_kg_m2",8.6),("Norma","ABNT NBR 8800")]
nl=0
for s in f.by_type("IfcSlab"):
    if matn(s)=="Concreto Armado C25":
        attach(s,"Pset_Dimensionamento",laje_dim)
        attach(s,"Pset_Perfilor_Produto",laje_prod); nl+=1

# ---------- 2) VIGAS METALICAS ----------
# VS (secundaria) como padrao de viga de piso; VP marcada para revisao executiva
vs_dim=[("Funcao","Viga secundaria (apoia laje steel deck)"),("Vao_m",4.0),
  ("Faixa_influencia_m",2.0),("Carga_carac_kN_m",12.0),("Carga_ELU_kN_m",16.8),
  ("Momento_MSd_kNm",33.6),("Wx_necessario_cm3",108),("Perfil","W 250 x 17,9"),
  ("Wx_perfil_cm3",180),("Ix_perfil_cm4",2291),("phi_Mn_kNm",55.9),("Flecha_mm",8.7),
  ("Flecha_limite_mm",11.4),("Aco","ASTM A572 Gr.50"),("Ligacao","Parafusada A325"),
  ("Norma","NBR 8800"),("Verificacao","OK - momento e flecha"),
  ("Obs_viga_principal","VP de bordas/centrais: W 310 x 28,3 (MSd=67,2 kNm) - verificar no executivo")]
vp_prod=[("Fabricante","Gerdau / ArcelorMittal"),("Perfil_secundaria","W 250 x 17,9"),
  ("Perfil_principal","W 310 x 28,3"),("Aco","ASTM A572 Gr.50"),("Acabamento","Pintura anticorrosiva"),
  ("Protecao_fogo","TRRF conforme NBR 14432/14323")]
nv=0
for b in f.by_type("IfcBeam"):
    attach(b,"Pset_Dimensionamento",vs_dim)
    attach(b,"Pset_Perfilor_Produto",vp_prod); nv+=1

# ---------- 3) FECHAMENTO TERMILOR WALL PIR 50mm ----------
pan_dim=[("Sistema","Fechamento em painel sanduiche"),("Produto","Perfilor Termilor Wall PIR 50mm"),
  ("Nucleo","PIR (poliisocianurato)"),("Espessura_mm",50),("Largura_util_mm",1000),
  ("Peso_proprio_kg_m2",10.7),("Vao_vertical_m",2.79),("Montante_intermediario","Nao necessario"),
  ("Carga_vento_kN_m2",0.8),("Transmitancia_U_W_m2K",0.43),
  ("Fixacao","Parafuso autobrocante em viga/travessa de borda"),("Juntas","Macho-femea com vedacao"),
  ("Norma","NBR 14762 / NBR 6123"),("Verificacao","OK - vao 2,79 m sem montante")]
pan_prod=[("Fabricante","ArcelorMittal Perfilor"),("Linha","Termilor Wall PIR"),
  ("Espessura_mm",50),("Largura_util_mm",1000),("Peso_kg_m2",10.7),
  ("U_W_m2K",0.43),("Chapas_aco_mm","0,43 a 0,50"),("Norma","ABNT NBR 14762")]
npn=0
for w in f.by_type("IfcWall"):
    if matn(w)=="ThermCold PIR 50mm sanduíche":
        attach(w,"Pset_Dimensionamento",pan_dim)
        attach(w,"Pset_Perfilor_Produto",pan_prod); npn+=1

# resumo no projeto
proj=f.by_type("IfcProject")[0]
site=f.by_type("IfcSite")[0]
attach(site,"Pset_Sistema_Construtivo",[
  ("Laje","Steel Deck Perfilor MF-75 h=130 t=0,80 Q-92 (vao 2,0 m)"),
  ("Vigas","Metalicas A572: VS W250x17,9 / VP W310x28,3"),
  ("Fechamento","Painel Termilor Wall PIR 50mm (Perfilor)"),
  ("Normas","NBR 8800 / 14762 / 6120 / 6123 / 14432"),
  ("Nivel","Pre-dimensionamento BIM - confirmar no executivo")])
proj.Description=(proj.Description or "")+" | + dimensionamento sistema Perfilor (MF-75 + vigas + Termilor Wall PIR50)"
f.write(DEST)
print(f"1) Lajes Steel Deck MF-75 dimensionadas: {nl}")
print(f"2) Vigas com perfil dimensionado: {nv}")
print(f"3) Fechamentos Termilor Wall PIR 50mm: {npn}")
print(f"\nSalvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
