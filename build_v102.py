"""
HVG v101 -> v102 : remove o terreno topografico (morro) como referencia de nivel,
nivela todas as edificacoes e a paisagem ao plano Z=0 e adiciona um gramado plano
(terreno so como paisagem). A cota real deixa de ser referencia (pedido do usuario).
Saida: HVG_MASTER_v102_NIVELADO.ifc
"""
import ifcopenshell, time, os
from ifcopenshell.guid import new as guid

SRC="/home/user/Montex/HVG_MASTER_v101_DIMENSIONADO.ifc"
DEST="/home/user/Montex/HVG_MASTER_v102_NIVELADO.ifc"
t0=time.time()
f=ifcopenshell.open(SRC); oh=f.by_type("IfcOwnerHistory")[0]
site=f.by_type("IfcSite")[0]

def z_above(p):
    """Z acumulado dos placements ACIMA de p (na cadeia PlacementRelTo)."""
    z=0.0; q=p.PlacementRelTo
    while q:
        rp=getattr(q,"RelativePlacement",None)
        if rp and rp.is_a("IfcAxis2Placement3D") and rp.Location: z+=rp.Location.Coordinates[2]
        q=getattr(q,"PlacementRelTo",None)
    return z
def level_zero(el):
    """Ajusta o Z do placement do elemento para que sua cota mundial vire 0."""
    p=getattr(el,"ObjectPlacement",None)
    if not p: return False
    rp=getattr(p,"RelativePlacement",None)
    if not (rp and rp.is_a("IfcAxis2Placement3D") and rp.Location): return False
    x,y,_=rp.Location.Coordinates
    rp.Location.Coordinates=(float(x),float(y),float(-z_above(p)))
    return True

# 1) nivela todos os IfcBuilding (terreos -> Z=0; storeys/elementos acompanham)
nb=sum(level_zero(b) for b in f.by_type("IfcBuilding"))

# 2) nivela elementos contidos direto no Site (pavimentacao, quadras, vegetacao, muros...)
site_elems=[]
for rel in f.by_type("IfcRelContainedInSpatialStructure"):
    if rel.RelatingStructure==site: site_elems+=list(rel.RelatedElements)
ns=sum(level_zero(e) for e in site_elems)

# 3) remove a malha topografica (morro) e os terrenos complementares (viram so paisagem)
removed_terr=0
for r in list(site.Representation.Representations):
    pass
site.Representation=None  # remove malha do morro do IfcSite
for g in f.by_type("IfcGeographicElement"):
    ot=(g.ObjectType or "")+(g.Name or "")
    if "TERRENO" in ot.upper():
        g.Representation=None; removed_terr+=1  # remove geometria de terreno/plataforma

# 4) adiciona gramado plano (paisagem) em Z=0
def P3(x,y,z): return f.create_entity("IfcCartesianPoint",(float(x),float(y),float(z)))
def D3(x,y,z): return f.create_entity("IfcDirection",(float(x),float(y),float(z)))
ctx=None
for c in f.by_type("IfcGeometricRepresentationContext"):
    if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType=="Model": ctx=c
ctx=ctx or f.by_type("IfcGeometricRepresentationContext")[0]
# retangulo grande cobrindo a area do empreendimento (com folga)
X0,Y0,X1,Y1=-40,-40,460,540
prof=f.create_entity("IfcRectangleProfileDef","AREA",None,
    f.create_entity("IfcAxis2Placement2D",f.create_entity("IfcCartesianPoint",((X0+X1)/2,(Y0+Y1)/2)),
    f.create_entity("IfcDirection",(1.,0.))),float(X1-X0),float(Y1-Y0))
solid=f.create_entity("IfcExtrudedAreaSolid",prof,
    f.create_entity("IfcAxis2Placement3D",P3(0,0,-0.30),D3(0,0,1),D3(1,0,0)),D3(0,0,1),0.30)
rep=f.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",(solid,))
pds=f.create_entity("IfcProductDefinitionShape",None,None,(rep,))
place=f.create_entity("IfcLocalPlacement",site.ObjectPlacement,
    f.create_entity("IfcAxis2Placement3D",P3(0,0,0),D3(0,0,1),D3(1,0,0)))
grama=f.create_entity("IfcGeographicElement",guid(),oh,"Gramado-Paisagem",
    "Terreno plano (paisagem) - nivel de referencia removido",None,place,pds,None,"TERRAIN")
# material + cor verde
mat=f.create_entity("IfcMaterial","Grama Paisagem",None,None)
col=f.create_entity("IfcColourRgb",None,0.36,0.55,0.27)
rnd=f.create_entity("IfcSurfaceStyleRendering",col,0.0,None,None,None,None,None,None,"NOTDEFINED")
stl=f.create_entity("IfcSurfaceStyle","Grama Paisagem","BOTH",(rnd,))
si=f.create_entity("IfcStyledItem",solid,(stl,),None)
f.create_entity("IfcRelAssociatesMaterial",guid(),oh,None,None,[grama],mat)
f.create_entity("IfcRelContainedInSpatialStructure",guid(),oh,None,None,[grama],site)

proj=f.by_type("IfcProject")[0]
proj.Description=(proj.Description or "")+" | v102: terreno topografico removido, edificacoes niveladas ao plano 0, terreno so como paisagem (gramado)"
f.write(DEST)
print(f"1) Buildings nivelados (Z->0): {nb}")
print(f"2) Elementos de site nivelados: {ns}/{len(site_elems)}")
print(f"3) Malha do morro removida + {removed_terr} terrenos complementares")
print(f"4) Gramado plano adicionado em Z=0 ({X1-X0}x{Y1-Y0} m)")
print(f"\nSalvo {DEST} ({os.path.getsize(DEST)/1e6:.1f} MB) em {time.time()-t0:.1f}s")
