"""
HVG v104 -> v105 : ULTRA-REALISMO visual.
- Paleta premium por material com ReflectanceMethod correto (GLASS/METAL/MATT/
  PLASTIC/PHONG), transparencia, especularidade, brilho e cor de reflexao.
  Corrige: vidro opaco -> vidro translucido; 39 materiais NOTDEFINED -> metodo certo.
- Vegetacao colorida POR ESPECIE (tronco marrom + copa da cor da especie:
  Ipe amarelo, Quaresmeira/Jacaranda roxo, Araucaria verde-escuro, etc).
- Agua translucida azul em piscinas/lagos; gramado verde.
Saida: HVG_MASTER_v105_REALISTA.ifc
"""
import ifcopenshell, time, os
from ifcopenshell.guid import new as guid

SRC="/home/user/Montex/HVG_MASTER_v104_NIVELADO_OK.ifc"
DEST="/home/user/Montex/HVG_MASTER_v105_REALISTA.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]
ctx=None
for c in f.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType=="Model": ctx=c
ctx=ctx or f.by_type("IfcGeometricRepresentationContext")[0]

def col(rgb,name=None): return f.create_entity("IfcColourRgb",name,float(rgb[0]),float(rgb[1]),float(rgb[2]))

# paleta: (keywords, rgb, method, transparency, specular(0-1), roughness(0-1))
# ordem importa: especifico antes de generico
PAL=[
 (["vidro","janela","esquadria alum","aluminio","alumínio"],None,None,None,None,None),  # placeholder reorder below
]
PAL=[
 # --- VIDRO ---
 (["vidro"], (0.52,0.70,0.82), "GLASS", 0.58, 0.95, 0.04),
 # --- ESQUADRIA / ALUMINIO ---
 (["esquadria","aluminio","alumínio"], (0.88,0.89,0.91), "METAL", 0.0, 0.7, 0.12),
 # --- METAIS ESPECIFICOS ---
 (["inox"], (0.78,0.79,0.81), "METAL", 0.0, 0.9, 0.08),
 (["cobre"], (0.72,0.45,0.20), "METAL", 0.0, 0.8, 0.18),
 (["bronze","latao","latão"], (0.78,0.60,0.32), "METAL", 0.0, 0.8, 0.2),
 (["galvaniz","galvan"], (0.66,0.68,0.70), "METAL", 0.0, 0.55, 0.3),
 (["aço estrutural","aco estrutural","aço","aco ","aço ","perfil","captor","spda","sprinkler","tubo aco","tubo aço"], (0.52,0.54,0.58), "METAL", 0.0, 0.75, 0.22),
 (["duto","avac","bandeja","eletrocalha","chapa aco","quadro","transformador","tank","tanque"], (0.80,0.81,0.84), "METAL", 0.0, 0.55, 0.25),
 (["bomba"], (0.20,0.34,0.58), "METAL", 0.0, 0.6, 0.2),
 # --- CONCRETO / ESTRUTURA ---
 (["steel deck"], (0.60,0.61,0.63), "METAL", 0.0, 0.4, 0.4),
 (["concreto","platibanda"], (0.66,0.66,0.64), "MATT", 0.0, 0.08, 0.95),
 # --- PEDRA / ALVENARIA / GESSO ---
 (["pedra"], (0.74,0.69,0.59), "MATT", 0.0, 0.12, 0.85),
 (["alvenaria"], (0.86,0.82,0.74), "MATT", 0.0, 0.06, 0.9),
 (["drywall","gesso","acartonado","lã de rocha","la de rocha","rocha"], (0.94,0.94,0.92), "MATT", 0.0, 0.05, 0.95),
 (["reboc"], (0.90,0.88,0.84), "MATT", 0.0, 0.06, 0.9),
 # --- PAINEL TERMICO / PIR ---
 (["pir","thermcold","núcleo","nucleo"], (0.94,0.93,0.90), "PHONG", 0.0, 0.25, 0.4),
 # --- MADEIRA ---
 (["cumaru","peroba","madeira","deck"], (0.48,0.30,0.16), "PLASTIC", 0.0, 0.35, 0.45),
 (["mobili"], (0.55,0.40,0.27), "PLASTIC", 0.0, 0.3, 0.5),
 (["estofado","tecido"], (0.30,0.34,0.46), "MATT", 0.0, 0.1, 0.8),
 # --- TELHA / COBERTURA (prioridade sobre ceramica) ---
 (["telha"], (0.69,0.30,0.19), "MATT", 0.0, 0.2, 0.7),
 (["onduline"], (0.32,0.27,0.23), "MATT", 0.0, 0.15, 0.8),
 (["manta","impermeab"], (0.26,0.25,0.24), "MATT", 0.0, 0.12, 0.85),
 (["forro"], (0.95,0.95,0.94), "MATT", 0.0, 0.05, 0.95),
 # --- CERAMICA / PORCELANATO ---
 (["porcelanato"], (0.87,0.84,0.79), "PLASTIC", 0.0, 0.55, 0.18),
 (["ceramica de piscina","azulejo"], (0.35,0.62,0.78), "PLASTIC", 0.0, 0.6, 0.15),
 (["ceramica","cerâmica","louca","louça"], (0.93,0.92,0.90), "PLASTIC", 0.0, 0.5, 0.2),
 # --- PISOS / PAVIMENTO ---
 (["asfalt","cbuq"], (0.16,0.16,0.18), "MATT", 0.0, 0.08, 0.92),
 (["poliuretano","esportivo"], (0.16,0.42,0.70), "PLASTIC", 0.0, 0.4, 0.3),
 (["saibro"], (0.82,0.70,0.46), "MATT", 0.0, 0.06, 0.95),
 (["univerde","permeavel","permeável"], (0.45,0.58,0.40), "MATT", 0.0, 0.05, 0.95),
 (["termoplastico","termoplástico","sinaliza"], (0.96,0.96,0.95), "MATT", 0.0, 0.1, 0.85),
 # --- VEGETACAO / TERRENO ---
 (["grama sintetica","grama sintética","sintetica"], (0.26,0.52,0.30), "MATT", 0.0, 0.05, 0.95),
 (["grama","gramado","esmeralda"], (0.34,0.55,0.24), "MATT", 0.0, 0.04, 0.97),
 (["paisag","vegeta","folhagem"], (0.30,0.50,0.22), "MATT", 0.0, 0.04, 0.97),
 (["terra"], (0.32,0.22,0.14), "MATT", 0.0, 0.04, 0.97),
 # --- MEP (cores funcionais com brilho plastico) ---
 (["pvc hidr","tubo pvc hidr","hidráulica","hidraulica"], (0.20,0.55,0.80), "PLASTIC", 0.0, 0.35, 0.3),
 (["pvc esgoto","esgoto"], (0.40,0.40,0.43), "PLASTIC", 0.0, 0.3, 0.35),
 (["incendio","incêndio","tubo aço sch40 inc"], (0.82,0.10,0.10), "PLASTIC", 0.0, 0.4, 0.3),
 (["gas","gás"], (0.92,0.80,0.12), "PLASTIC", 0.0, 0.4, 0.3),
 (["pvc","rede polietileno","polietileno"], (0.85,0.85,0.85), "PLASTIC", 0.0, 0.3, 0.35),
 (["led","refletor"], (0.99,0.97,0.86), "PHONG", 0.0, 0.8, 0.1),
 (["cabo","fibra"], (0.25,0.25,0.28), "PLASTIC", 0.0, 0.2, 0.5),
 (["reservat","prfv"], (0.46,0.56,0.66), "PLASTIC", 0.0, 0.3, 0.4),
 (["difusor","grelha"], (0.82,0.82,0.85), "METAL", 0.0, 0.5, 0.3),
 (["alambrado","rede"], (0.55,0.58,0.55), "METAL", 0.0, 0.4, 0.4),
 # --- AGUA ---
 (["agua","água","piscina","lago"], (0.13,0.42,0.62), "GLASS", 0.45, 0.95, 0.03),
]
def style_for(name):
    nl=(name or "").lower()
    for kws,rgb,method,t,spec,rough in PAL:
        if rgb is None: continue
        for kw in kws:
            if kw in nl: return rgb,method,t,spec,rough
    return (0.74,0.73,0.71),"MATT",0.0,0.1,0.85  # default fosco neutro

def apply_render(st, name):
    rgb,method,t,spec,rough=style_for(name)
    c=col(rgb,name); st.SurfaceColour=c; st.DiffuseColour=c; st.Transparency=float(t)
    st.ReflectanceMethod=method
    st.SpecularColour=f.create_entity("IfcNormalisedRatioMeasure",float(spec))
    st.SpecularHighlight=f.create_entity("IfcSpecularRoughness",float(rough))
    refl=tuple(min(1.0,x*1.25+0.12) for x in rgb) if method in ("METAL","GLASS") else tuple(min(1.0,x*1.1) for x in rgb)
    st.ReflectionColour=col(refl,"refl-"+(name or ""))
    return method

# ---- 1) atualiza TODOS os estilos existentes (material + geometria) pelo nome ----
from collections import Counter
mat_rendering={}
methods=Counter(); ntot=0
for ss in f.by_type("IfcSurfaceStyle"):
    for st in (ss.Styles or []):
        if not st.is_a("IfcSurfaceStyleRendering"): continue
        nm=ss.Name or (st.SurfaceColour.Name if st.SurfaceColour else None) or ""
        methods[apply_render(st,nm)]+=1; ntot+=1
        mat_rendering.setdefault(nm,st)
# garante que materiais tenham matdefrep (mapa por nome de material)
for mdr in f.by_type("IfcMaterialDefinitionRepresentation"):
    mat_rendering.setdefault(mdr.RepresentedMaterial.Name,True)

# materiais sem rendering (ex Grama Paisagem) -> cria
def make_matdefrep(mat):
    rnd=f.create_entity("IfcSurfaceStyleRendering",col((0.7,0.7,0.7)),0.0,None,None,None,None,None,None,"NOTDEFINED")
    apply_render(rnd,mat.Name)
    stl=f.create_entity("IfcSurfaceStyle",mat.Name,"BOTH",(rnd,))
    si=f.create_entity("IfcStyledItem",None,(stl,),None)
    sr=f.create_entity("IfcStyledRepresentation",ctx,"Style","Material",(si,))
    f.create_entity("IfcMaterialDefinitionRepresentation",None,None,(sr,),mat)
for mat in f.by_type("IfcMaterial"):
    if mat.Name not in mat_rendering: make_matdefrep(mat)

# ---- 2) vegetacao por especie: tronco marrom + copa colorida (estilo na geometria) ----
ESPECIE={
 "ipe":(0.96,0.80,0.14),"ipê":(0.96,0.80,0.14),          # Ipe amarelo
 "quaresmeira":(0.58,0.30,0.66),                          # roxo
 "jacaranda":(0.46,0.42,0.72),"jacarandá":(0.46,0.42,0.72),# roxo-azulado
 "araucaria":(0.12,0.30,0.18),"araucária":(0.12,0.30,0.18),# verde escuro
 "palmeira":(0.24,0.46,0.22),
 "arvore":(0.27,0.50,0.24),"árvore":(0.27,0.50,0.24),
 "arbusto":(0.30,0.52,0.26),
 "tufo":(0.46,0.55,0.28),"graminea":(0.46,0.55,0.28),"gramínea":(0.46,0.55,0.28),
 "nenufar":(0.28,0.50,0.30),"nymphaea":(0.28,0.50,0.30),
}
TRONCO=(0.34,0.23,0.14)
def especie_cor(nm):
    nl=(nm or "").lower()
    for k,v in ESPECIE.items():
        if k in nl: return v
    return None
def style(rgb,method,spec,rough,t=0.0):
    rnd=f.create_entity("IfcSurfaceStyleRendering",col(rgb),float(t),col(rgb),None,None,
        col(tuple(min(1,x*1.1) for x in rgb)),f.create_entity("IfcNormalisedRatioMeasure",float(spec)),
        f.create_entity("IfcSpecularRoughness",float(rough)),method)
    return f.create_entity("IfcSurfaceStyle",None,"BOTH",(rnd,))
copa_styles={}
tronco_style=style(TRONCO,"MATT",0.1,0.7)
nveg=0
for g in f.by_type("IfcGeographicElement"):
    cor=especie_cor(g.Name)
    if cor is None or not g.Representation: continue
    if cor not in copa_styles: copa_styles[cor]=style(cor,"MATT",0.05,0.95)
    # coletar solids (tronco = menor secao; copa = demais)
    solids=[]
    for rep in g.Representation.Representations:
        for it in rep.Items:
            if it.is_a("IfcExtrudedAreaSolid"):
                p=it.SweptArea
                area=(getattr(p,"XDim",0) or 0)*(getattr(p,"YDim",0) or 0) or ((getattr(p,"Radius",0) or 0)**2*3.14)
                solids.append((area,it))
    if not solids: continue
    solids.sort()
    for i,(area,sol) in enumerate(solids):
        s=tronco_style if i==0 and len(solids)>1 else copa_styles[cor]
        f.create_entity("IfcStyledItem",sol,(s,),None)
    nveg+=1

# ---- 3) agua nas piscinas/lagos (reatribui material agua translucida) ----
agua=f.create_entity("IfcMaterial","Agua",None,None)
make_matdefrep(agua)  # ja entra na paleta (GLASS azul) via style_for('Agua')? nome 'Agua' -> agua kw
nag=0
water_style=style((0.13,0.42,0.62),"GLASS",0.95,0.03,t=0.45)
for el in f.by_type("IfcCovering")+f.by_type("IfcSlab"):
    nl=(el.Name or "").lower()
    if ("piscina" in nl or "lago" in nl or "espelho" in nl) and el.Representation:
        for rep in el.Representation.Representations:
            for it in rep.Items:
                if it.is_a("IfcExtrudedAreaSolid"): f.create_entity("IfcStyledItem",it,(water_style,),None)
        nag+=1

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "").split(' | v105')[0]+" | v105: ultra-realismo (paleta premium, vidro translucido, metais, vegetacao por especie, agua)"
f.write(DEST)
print(f"1) Materiais estilizados: {len(mat_rendering)} | metodos: {dict(methods)}")
print(f"2) Vegetacao colorida por especie: {nveg} (copas: {len(copa_styles)} cores)")
print(f"3) Agua (piscinas/lagos): {nag}")
print(f"Salvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
