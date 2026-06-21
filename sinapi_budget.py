#!/usr/bin/env python3
"""Orcamento por composicao (estilo SINAPI) - HVG v91. Valores de REFERENCIA (base 2026),
codigos ilustrativos; substituir pela composicao/cotacao vigente. Quantidades do modelo IFC."""
import json, csv
q=json.load(open("q5d.json"))
geom={"pipe":4200.1,"duct":1120.3,"tray":1142.3}
# takeoff areas confiaveis (v91)
laje_area=26436.6; wall=q["wall"]; win=q["win"]; door=q["door"]; cov=q["cov"]; conc=q["conc"]
pav=30610.4

# ---- COMPOSICOES (servico, [ (cod, descricao, un, coef_por_un_servico, custo_unit_insumo) ], un_servico, qtd_servico)
COMP=[
 ("Estrutura de concreto armado","m3",conc,[
   ("94965","Concreto FCK=25MPa, usinado, lancado/adensado","m3",1.05,560),
   ("92270","Forma em chapa compensada resinada","m2",10.0,98),
   ("92791","Armacao aco CA-50/CA-60 (corte/dobra/montagem)","kg",90.0,13.2)]),
 ("Lajes de piso (deck/concreto+capa)","m2",laje_area,[
   ("CST-LAJE","Laje (estrutura+capa+regularizacao)","m2",1.0,300)]),
 ("Alvenaria de vedacao + revestimento","m2",wall,[
   ("87474","Alvenaria bloco ceramico 14cm","m2",1.0,78),
   ("87879","Chapisco + emboco/reboco (2 faces)","m2",1.0,92),
   ("88489","Pintura latex (2 faces, massa+2 demaos)","m2",1.0,38)]),
 ("Esquadrias (aluminio+vidro)","m2",win,[
   ("CST-ESQ","Esquadria aluminio com vidro laminado","m2",1.0,950)]),
 ("Portas internas (madeira)","un",door,[
   ("90843","Porta madeira semi-oca + batente + ferragens","un",1.0,1300)]),
 ("Cobertura e revestimentos de teto/parede","m2",cov,[
   ("CST-COB","Cobertura/revestimento (telha/forro/acab.)","m2",1.0,165)]),
 ("Instalacao hidrossanitaria/incendio","m",geom["pipe"],[
   ("CST-HID","Tubulacao + conexoes + suportes","m",1.0,95)]),
 ("Instalacao AVAC (dutos)","m",geom["duct"],[
   ("CST-AVAC","Duto galvanizado + isolamento + suportes","m",1.0,240)]),
 ("Instalacao eletrica (eletrocalhas/infra)","m",geom["tray"],[
   ("CST-ELE","Eletrocalha + cabos + infra","m",1.0,150)]),
 ("Pavimentacao externa e urbanismo","m2",pav,[
   ("CST-PAV","Pavimentos (concreto/asfalto/univerde/grama) medio","m2",1.0,135)]),
]
rows=[]; direto=0
for serv,un,qty,ins in COMP:
    serv_sub=0
    for cod,desc,uni,coef,cu in ins:
        q_ins=qty*coef; sub=q_ins*cu; serv_sub+=sub
        rows.append([serv,cod,desc,uni,round(q_ins,1),cu,round(sub,2)])
    rows.append([serv,"","SUBTOTAL "+serv,un,round(qty,1),"",round(serv_sub,2)])
    direto+=serv_sub

# complementos (allowances) - estimativas % sobre custo direto
fundacoes=direto*0.08
inst_compl=direto*0.10  # complementacao de instalacoes nao modeladas
canteiro=direto*0.03
total_direto=direto+fundacoes+inst_compl+canteiro
bdi=total_direto*0.25
total=total_direto+bdi

with open("HVG_v91_Orcamento_SINAPI_Composicao.csv","w",newline='',encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["Servico","Cod_Ref","Descricao_Insumo","Un","Quantidade","Custo_Unit_BRL","Subtotal_BRL"])
    for r in rows: w.writerow(r)
    w.writerow([])
    w.writerow(["","","CUSTO DIRETO (servicos modelados)","","","",round(direto,2)])
    w.writerow(["","","Fundacoes (estimado 8%)","","","",round(fundacoes,2)])
    w.writerow(["","","Complementacao de instalacoes (10%)","","","",round(inst_compl,2)])
    w.writerow(["","","Canteiro/administracao local (3%)","","","",round(canteiro,2)])
    w.writerow(["","","CUSTO DIRETO TOTAL","","","",round(total_direto,2)])
    w.writerow(["","","BDI (25%)","","","",round(bdi,2)])
    w.writerow(["","","TOTAL GERAL ESTIMADO (REFERENCIA)","","","",round(total,2)])

print("=== ORCAMENTO POR COMPOSICAO (SINAPI - referencia) ===")
cur=None
for serv,cod,desc,uni,qy,cu,sub in rows:
    if serv!=cur: cur=serv
    if desc.startswith("SUBTOTAL"):
        print(f"  {desc:48} R$ {sub:>14,.0f}")
print("  "+"-"*66)
print(f"  {'CUSTO DIRETO (modelado)':48} R$ {direto:>14,.0f}")
print(f"  {'+ Fundacoes (8%)':48} R$ {fundacoes:>14,.0f}")
print(f"  {'+ Complementacao instalacoes (10%)':48} R$ {inst_compl:>14,.0f}")
print(f"  {'+ Canteiro/adm local (3%)':48} R$ {canteiro:>14,.0f}")
print(f"  {'+ BDI (25%)':48} R$ {bdi:>14,.0f}")
print(f"  {'TOTAL GERAL ESTIMADO':48} R$ {total:>14,.0f}")
print(f"  Area util 31.585 m2  ->  R$ {total/31585:,.0f}/m2")
