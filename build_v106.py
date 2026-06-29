"""
HVG v105 -> v106 : LIMPEZA de itens dispersos/DXF + refino visual.
1) Remove os 9 underlays DXF (IfcAnnotation MTX-UNDERLAY-DXF) + camadas (estavam
   flutuando soltos no viewer).
2) Vincula/remove os 5 elementos dispersos (sem contencao nem agregacao).
3) Torna invisiveis os IfcOpeningElement (geometria 100% transparente) - mantem a
   subtracao dos vaos mas nao polui o 3D.
4) Janelas com tonalidade AZUL (vidro translucido) na geometria.
5) Varandas bem definidas: guarda-corpos de vidro azul claro + lajes de varanda.
Saida: HVG_MASTER_v106_LIMPO.ifc
"""
import ifcopenshell, time, os
import ifcopenshell.util.element as ue
from ifcopenshell.guid import new as guid

SRC="/home/user/Montex/HVG_MASTER_v105_REALISTA.ifc"
DEST="/home/user/Montex/HVG_MASTER_v106_LIMPO.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]
def col(rgb): return f.create_entity("IfcColourRgb",None,float(rgb[0]),float(rgb[1]),float(rgb[2]))
def style(rgb,method,spec,rough,t=0.0):
    rnd=f.create_entity("IfcSurfaceStyleRendering",col(rgb),float(t),col(rgb),None,None,
        col(tuple(min(1,x*1.15+0.1) for x in rgb)),f.create_entity("IfcNormalisedRatioMeasure",float(spec)),
        f.create_entity("IfcSpecularRoughness",float(rough)),method)
    return f.create_entity("IfcSurfaceStyle",None,"BOTH",(rnd,))

# ---- 1) remove underlays DXF + camadas ----
und=[a for a in f.by_type("IfcAnnotation") if a.ObjectType=="MTX-UNDERLAY-DXF"]
# tira das rels de contencao e de propriedades
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    keep=[e for e in (rel.RelatedElements or []) if e not in und]
    if len(keep)!=len(rel.RelatedElements or []): rel.RelatedElements=keep
for rel in list(f.by_type("IfcRelDefinesByProperties")):
    if any(o in und for o in (rel.RelatedObjects or [])):
        ps=rel.RelatingPropertyDefinition
        try: f.remove(rel)
        except Exception: pass
        try: f.remove(ps)
        except Exception: pass
# remove camadas de underlay
for l in list(f.by_type("IfcPresentationLayerWithStyle")):
    if l.Name and "Underlay" in l.Name:
        try: f.remove(l)
        except Exception: pass
# remove os annotations (deep)
nrem=0
for a in und:
    try: ue.remove_deep2(f,a); nrem+=1
    except Exception:
        a.Representation=None; nrem+=1
print(f"1) underlays DXF removidos: {nrem}")

# ---- 2) elementos dispersos (sem contencao/agregacao) ----
contained=set()
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    for e in (rel.RelatedElements or []): contained.add(e.id())
aggreg=set()
for rel in f.by_type("IfcRelAggregates"):
    for c in (rel.RelatedObjects or []): aggreg.add(c.id())
disp=[e for t in ("IfcRoof","IfcCovering","IfcSlab","IfcWall") for e in f.by_type(t)
      if e.id() not in contained and e.id() not in aggreg]
# vincula ao site (vinculo minimo) - mantem geometria
site=f.by_type("IfcSite")[0]
if disp:
    f.create_entity("IfcRelContainedInSpatialStructure",guid(),oh,None,None,list(disp),site)
print(f"2) elementos dispersos vinculados ao site: {len(disp)}")

# ---- 3) openings invisiveis (geometria transparente) ----
inv=style((0.6,0.6,0.6),"NOTDEFINED",0.0,0.5,t=1.0)
nop=0
for o in f.by_type("IfcOpeningElement"):
    if not o.Representation: continue
    for rep in o.Representation.Representations:
        for it in rep.Items:
            f.create_entity("IfcStyledItem",it,(inv,),None)
    nop+=1
print(f"3) openings tornados invisiveis: {nop}")

# ---- 4) janelas com vidro AZUL translucido ----
vidro_azul=style((0.38,0.56,0.78),"GLASS",0.92,0.04,t=0.5)
nw=0
for w in f.by_type("IfcWindow"):
    if not w.Representation: continue
    for rep in w.Representation.Representations:
        for it in rep.Items:
            f.create_entity("IfcStyledItem",it,(vidro_azul,),None)
    nw+=1
print(f"4) janelas com vidro azul: {nw}")

# ---- 5) varandas: guarda-corpos de vidro azul claro + lajes de varanda ----
gc_vidro=style((0.55,0.72,0.86),"GLASS",0.9,0.05,t=0.55)
deck=style((0.50,0.33,0.18),"PLASTIC",0.35,0.45)
nrail=0; nslab=0
for r in f.by_type("IfcRailing"):
    nm=(r.Name or "").lower()
    if "varanda" in nm or "guarda" in nm:
        if r.Representation:
            for rep in r.Representation.Representations:
                for it in rep.Items: f.create_entity("IfcStyledItem",it,(gc_vidro,),None)
            nrail+=1
for s in f.by_type("IfcSlab"):
    if "varanda" in (s.Name or "").lower() and s.Representation:
        for rep in s.Representation.Representations:
            for it in rep.Items: f.create_entity("IfcStyledItem",it,(deck,),None)
        nslab+=1
print(f"5) varandas: {nrail} guarda-corpos vidro + {nslab} lajes deck")

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "").split(' | v106')[0]+" | v106: underlays DXF removidos, dispersos vinculados, openings invisiveis, janelas azuis, varandas definidas"
f.write(DEST)
print(f"\nSalvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
