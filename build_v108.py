"""
HVG v107 -> v108 : calibra a paleta ao projeto REAL (Hotel Vila Gale Inhotim),
a partir da analise de cores dos renders oficiais:
  - VIDRO e PISCINAS em TEAL/turquesa (assinatura Vila Gale), nao azul frio
  - PAREDES externas em tons QUENTES (areia/creme), nao cinza/branco frio
  - MADEIRA/deck/brises em marrom quente; PEDRA em taupe; TELHA terracota
  - Metais/concreto/vegetacao mantidos coerentes
Saida: HVG_MASTER_v108_VILAGALE.ifc
"""
import ifcopenshell, time, os
from collections import Counter
SRC="/home/user/Montex/HVG_MASTER_v107_VARANDAS.ifc"
DEST="/home/user/Montex/HVG_MASTER_v108_VILAGALE.ifc"
t0=time.time()
f=ifcopenshell.open(SRC)
def col(rgb,name=None): return f.create_entity("IfcColourRgb",name,float(rgb[0]),float(rgb[1]),float(rgb[2]))

# paleta calibrada Vila Gale Inhotim (keywords -> rgb, method, transp, spec, rough)
PAL=[
 # AGUA (piscinas/lagos) -> teal profundo
 (["agua","água","piscina","lago","espelho"], (0.10,0.45,0.53), "GLASS", 0.42, 0.95, 0.03),
 # VIDRO / janelas / guarda-corpo -> teal claro translucido (assinatura)
 (["vidro","janela","portajanela","porta-janela"], (0.28,0.58,0.60), "GLASS", 0.5, 0.92, 0.04),
 # ESQUADRIA aluminio -> grafite quente (Vila Gale usa esquadria escura)
 (["esquadria","aluminio","alumínio","caixilho"], (0.30,0.31,0.32), "METAL", 0.0, 0.6, 0.18),
 # METAIS
 (["inox"], (0.78,0.79,0.81), "METAL", 0.0, 0.9, 0.08),
 (["cobre"], (0.72,0.45,0.20), "METAL", 0.0, 0.8, 0.18),
 (["bronze","latao","latão"], (0.78,0.60,0.32), "METAL", 0.0, 0.8, 0.2),
 (["galvaniz","galvan"], (0.64,0.66,0.68), "METAL", 0.0, 0.55, 0.3),
 (["aço estrutural","aco estrutural","aço","aco ","perfil","captor","spda","sprinkler","tubo aco","tubo aço"], (0.46,0.47,0.50), "METAL", 0.0, 0.72, 0.24),
 (["duto","avac","bandeja","eletrocalha","chapa aco","quadro","transformador","tank","tanque","difusor"], (0.74,0.74,0.76), "METAL", 0.0, 0.5, 0.28),
 (["bomba"], (0.22,0.36,0.55), "METAL", 0.0, 0.55, 0.25),
 # TELHA terracota (Vila Gale)
 (["telha"], (0.71,0.36,0.19), "MATT", 0.0, 0.2, 0.7),
 (["onduline"], (0.34,0.27,0.21), "MATT", 0.0, 0.15, 0.8),
 (["manta","impermeab"], (0.27,0.25,0.23), "MATT", 0.0, 0.12, 0.85),
 (["forro"], (0.95,0.94,0.91), "MATT", 0.0, 0.05, 0.95),
 # CONCRETO / STEEL DECK
 (["steel deck"], (0.60,0.59,0.56), "METAL", 0.0, 0.4, 0.42),
 (["concreto","platibanda"], (0.67,0.65,0.61), "MATT", 0.0, 0.08, 0.92),
 # PEDRA / ALVENARIA / PAREDES QUENTES
 (["pedra"], (0.56,0.50,0.41), "MATT", 0.0, 0.12, 0.82),
 (["alvenaria + pedra","alvenaria+pedra"], (0.62,0.55,0.45), "MATT", 0.0, 0.1, 0.82),
 (["thermcold","pir","núcleo","nucleo","lã de rocha","la de rocha"], (0.86,0.81,0.70), "PHONG", 0.0, 0.2, 0.45),  # painel fachada creme quente
 (["alvenaria","reboc"], (0.84,0.78,0.67), "MATT", 0.0, 0.06, 0.9),  # parede areia/creme
 (["drywall","gesso","acartonado","rocha"], (0.93,0.92,0.89), "MATT", 0.0, 0.05, 0.95),
 # MADEIRA / DECK (marrom quente)
 (["cumaru","peroba","madeira","deck"], (0.45,0.31,0.17), "PLASTIC", 0.0, 0.35, 0.45),
 (["mobili"], (0.52,0.38,0.24), "PLASTIC", 0.0, 0.3, 0.5),
 (["estofado","tecido"], (0.34,0.30,0.26), "MATT", 0.0, 0.1, 0.8),
 # CERAMICA / PORCELANATO (bege quente)
 (["porcelanato"], (0.84,0.79,0.71), "PLASTIC", 0.0, 0.5, 0.2),
 (["ceramica de piscina","azulejo"], (0.20,0.55,0.60), "PLASTIC", 0.0, 0.6, 0.15),
 (["ceramica","cerâmica","louca","louça"], (0.92,0.90,0.86), "PLASTIC", 0.0, 0.5, 0.2),
 # PISOS EXTERNOS
 (["asfalt","cbuq"], (0.20,0.19,0.19), "MATT", 0.0, 0.08, 0.92),
 (["poliuretano","esportivo"], (0.16,0.45,0.55), "PLASTIC", 0.0, 0.4, 0.3),
 (["saibro"], (0.80,0.68,0.46), "MATT", 0.0, 0.06, 0.95),
 (["univerde","permeavel","permeável"], (0.46,0.56,0.38), "MATT", 0.0, 0.05, 0.95),
 (["termoplastico","termoplástico","sinaliza"], (0.95,0.95,0.93), "MATT", 0.0, 0.1, 0.85),
 # VEGETACAO / TERRENO
 (["grama sintetica","grama sintética","sintetica"], (0.28,0.50,0.30), "MATT", 0.0, 0.05, 0.95),
 (["grama","gramado","esmeralda"], (0.36,0.54,0.26), "MATT", 0.0, 0.04, 0.97),
 (["paisag","vegeta","folhagem"], (0.32,0.50,0.24), "MATT", 0.0, 0.04, 0.97),
 (["terra"], (0.34,0.24,0.16), "MATT", 0.0, 0.04, 0.97),
 # MEP
 (["pvc hidr","hidráulica","hidraulica"], (0.20,0.55,0.78), "PLASTIC", 0.0, 0.35, 0.3),
 (["esgoto"], (0.40,0.40,0.43), "PLASTIC", 0.0, 0.3, 0.35),
 (["incendio","incêndio"], (0.80,0.12,0.12), "PLASTIC", 0.0, 0.4, 0.3),
 (["gas","gás"], (0.90,0.78,0.14), "PLASTIC", 0.0, 0.4, 0.3),
 (["pvc","polietileno"], (0.85,0.85,0.84), "PLASTIC", 0.0, 0.3, 0.35),
 (["led","refletor"], (0.99,0.97,0.86), "PHONG", 0.0, 0.8, 0.1),
 (["cabo","fibra"], (0.25,0.25,0.27), "PLASTIC", 0.0, 0.2, 0.5),
 (["reservat","prfv"], (0.48,0.56,0.62), "PLASTIC", 0.0, 0.3, 0.4),
 (["alambrado","rede"], (0.55,0.58,0.55), "METAL", 0.0, 0.4, 0.4),
]
TEAL_GLASS=(0.28,0.58,0.60)
def style_for(name):
    nl=(name or "").lower()
    for kws,rgb,method,t,spec,rough in PAL:
        for kw in kws:
            if kw in nl: return rgb,method,t,spec,rough
    return None
def apply(st,name):
    r=style_for(name)
    if r is None:
        # sem nome reconhecido: se ja era GLASS -> teal; senao mantem cor, garante metodo
        if st.ReflectanceMethod=="GLASS":
            rgb,method,t,spec,rough=TEAL_GLASS,"GLASS",0.5,0.92,0.04
        else:
            return st.ReflectanceMethod or "MATT"
    else:
        rgb,method,t,spec,rough=r
    c=col(rgb,name); st.SurfaceColour=c; st.DiffuseColour=c; st.Transparency=float(t)
    st.ReflectanceMethod=method
    st.SpecularColour=f.create_entity("IfcNormalisedRatioMeasure",float(spec))
    st.SpecularHighlight=f.create_entity("IfcSpecularRoughness",float(rough))
    refl=tuple(min(1.0,x*1.2+0.12) for x in rgb) if method in("METAL","GLASS") else tuple(min(1.0,x*1.1) for x in rgb)
    st.ReflectionColour=col(refl); return method

methods=Counter(); n=0
for ss in f.by_type("IfcSurfaceStyle"):
    nm=ss.Name or ""
    for st in (ss.Styles or []):
        if not st.is_a("IfcSurfaceStyleRendering"): continue
        name=nm or (st.SurfaceColour.Name if st.SurfaceColour else "")
        methods[apply(st,name)]+=1; n+=1

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "").split(' | v108')[0]+" | v108: paleta calibrada ao Hotel Vila Gale Inhotim (teal nas piscinas/vidros, paredes quentes, madeira, telha terracota)"
f.write(DEST)
print(f"Estilos recalibrados: {n} | metodos: {dict(methods)}")
print(f"Salvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
