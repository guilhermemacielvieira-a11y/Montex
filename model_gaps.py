#!/usr/bin/env python3
"""HVG - Modelagem das lacunas do Quadro Sinoptico + correcao de area do SPA (v88 -> v89).
Cria: estacionamentos (168+2 vagas), area desportiva (polidesportivo/padel/beach tennis),
pista de carros infantil, subestacao, central de gas, apoio quadras; e amplia o SPA."""
import ifcopenshell, ifcopenshell.geom as geom
import numpy as np
m=ifcopenshell.open("HVG_MASTER_v88_render_corrigido.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
site=m.by_type("IfcSite")[0]
site_pl=site.ObjectPlacement
ctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier=="Body"]
ctx=ctx[0] if ctx else m.by_type("IfcGeometricRepresentationContext")[0]
def g(): return ifcopenshell.guid.new()

# terrain sampler
s=geom.settings(); s.set("use-world-coords",True)
V=np.array(geom.create_shape(s,site).geometry.verts).reshape(-1,3)
def tz(x,y):
    d=(V[:,0]-x)**2+(V[:,1]-y)**2; return float(V[np.argsort(d)[:8],2].mean())

# ---- helpers ----
def dirn(t): return m.create_entity("IfcDirection",[float(a) for a in t])
def pt(t): return m.create_entity("IfcCartesianPoint",[float(a) for a in t])
def placement(x,y,z,relto):
    return m.create_entity("IfcLocalPlacement",relto,
        m.create_entity("IfcAxis2Placement3D",pt((x,y,z)),dirn((0,0,1)),dirn((1,0,0))))
_mat={}
def material(name,rgb):
    if name in _mat: return _mat[name]
    mt=m.create_entity("IfcMaterial",name); _mat[name]=(mt,rgb); return (mt,rgb)
def style_for(rgb):
    col=m.create_entity("IfcColourRgb",None,*[float(c) for c in rgb])
    rend=m.create_entity("IfcSurfaceStyleRendering",col,0.0,None,None,None,None,None,None,"NOTDEFINED")
    ss=m.create_entity("IfcSurfaceStyle",None,"BOTH",[rend])
    return m.create_entity("IfcPresentationStyleAssignment",[ss])
def rect_solid(w,d,th,zoff=0.0):
    prof=m.create_entity("IfcRectangleProfileDef","AREA",None,
        m.create_entity("IfcAxis2Placement2D",pt((0.,0.)),dirn((1.,0.))),float(w),float(d))
    pos=m.create_entity("IfcAxis2Placement3D",pt((0.,0.,float(zoff))),dirn((0,0,1)),dirn((1,0,0)))
    return m.create_entity("IfcExtrudedAreaSolid",prof,pos,dirn((0,0,1)),float(th))
def shape(solid):
    return m.create_entity("IfcProductDefinitionShape",None,None,
        [m.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",[solid])])
def assoc_mat(el,matrgb):
    m.create_entity("IfcRelAssociatesMaterial",g(),oh,None,None,[el],matrgb[0])
def style_solid(solid,rgb):
    m.create_entity("IfcStyledItem",solid,[style_for(rgb)],None)
def add_area_qto(el,area,setname="Qto_SlabBaseQuantities"):
    q=m.create_entity("IfcQuantityArea","GrossArea",None,None,float(area),None)
    m.create_entity("IfcRelDefinesByProperties",g(),oh,None,None,[el],
        m.create_entity("IfcElementQuantity",g(),oh,setname,None,None,[q]))
def add_pset(el,name,props):
    pv=[m.create_entity("IfcPropertySingleValue",k,None,m.create_entity("IfcText",str(v)) if isinstance(v,str) else m.create_entity("IfcInteger",int(v)) if isinstance(v,int) else m.create_entity("IfcReal",float(v)),None) for k,v in props.items()]
    m.create_entity("IfcRelDefinesByProperties",g(),oh,None,None,[el],
        m.create_entity("IfcPropertySet",g(),oh,name,None,pv))
def contain(el,struct):
    rel=next((r for r in struct.ContainsElements),None)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+[el]
    else: m.create_entity("IfcRelContainedInSpatialStructure",g(),oh,None,None,[el],struct)

def make_slab(name,objtype,predef,cx,cy,z,w,d,th,matrgb,container,below=True):
    zoff=-th if below else 0.0
    sol=rect_solid(w,d,th,zoff)
    sl=m.create_entity("IfcSlab",g(),oh,name,None,objtype,placement(cx,cy,z,site_pl),shape(sol),None,predef)
    style_solid(sol,matrgb[1]); assoc_mat(sl,matrgb); add_area_qto(sl,w*d); contain(sl,container)
    return sl
def make_space(name,longname,cx,cy,z,w,d,h,container,extra=None):
    sol=rect_solid(w,d,h,0.0)
    sp=m.create_entity("IfcSpace",g(),oh,name,None,None,placement(cx,cy,z,
        container.ObjectPlacement if container.is_a("IfcBuildingStorey") else site_pl),
        shape(sol),longname,"ELEMENT","INTERNAL" if container.is_a("IfcBuildingStorey") else "EXTERNAL",None)
    style_solid(sol,(0.6,0.85,0.95)); 
    qn=m.create_entity("IfcQuantityArea","NetFloorArea",None,None,float(w*d),None)
    qg=m.create_entity("IfcQuantityArea","GrossFloorArea",None,None,float(w*d),None)
    m.create_entity("IfcRelDefinesByProperties",g(),oh,None,None,[sp],
        m.create_entity("IfcElementQuantity",g(),oh,"Qto_SpaceBaseQuantities",None,None,[qn,qg]))
    add_pset(sp,"Pset_SpaceCommon",{"Reference":name,"IsExternal":"FALSE" if container.is_a("IfcBuildingStorey") else "TRUE","PubliclyAccessible":"TRUE"})
    if extra: add_pset(sp,"Pset_HVG_Ambiente",extra)
    # aggregate to storey or contain in site
    if container.is_a("IfcBuildingStorey"):
        rel=next((r for r in container.IsDecomposedBy if r.is_a("IfcRelAggregates")),None)
        if rel: rel.RelatedObjects=list(rel.RelatedObjects)+[sp]
        else: m.create_entity("IfcRelAggregates",g(),oh,None,None,container,[sp])
    else:
        m.create_entity("IfcRelAggregates",g(),oh,None,None,container,[sp])
    return sp
def make_wall(name,cx,cy,z,w,d,h,matrgb,storey):
    sol=rect_solid(w,d,h,0.0)
    wl=m.create_entity("IfcWall",g(),oh,name,None,None,placement(cx,cy,z,site_pl),shape(sol),None,"STANDARD")
    style_solid(sol,matrgb[1]); assoc_mat(wl,matrgb); contain(wl,storey); return wl
def make_building(name,desc,cx,cy,z,storeyname):
    b=m.create_entity("IfcBuilding",g(),oh,name,desc,None,placement(cx,cy,z,site_pl),None,None,"ELEMENT",None,None,None)
    m.create_entity("IfcRelAggregates",g(),oh,None,None,site,[b])
    st=m.create_entity("IfcBuildingStorey",g(),oh,storeyname,None,None,placement(0,0,0,b.ObjectPlacement),None,None,"ELEMENT",0.0)
    m.create_entity("IfcRelAggregates",g(),oh,None,None,b,[st])
    return b,st

# materials/colors
M_PAV =material("Pavimento Univerde Permeavel",(0.55,0.6,0.5))
M_POLI=material("Piso Esportivo Poliuretano",(0.15,0.4,0.7))
M_BEACH=material("Saibro Beach Tennis",(0.85,0.72,0.45))
M_PADEL=material("Grama Sintetica Padel",(0.2,0.55,0.3))
M_ASF =material("Asfalto Pista CBUQ",(0.2,0.2,0.22))
M_CONC=material("Concreto Armado C25",(0.7,0.7,0.7))
M_ALV =material("Alvenaria Rebocada",(0.9,0.88,0.82))
M_TELHA=material("Telha Ceramica Vila Gale",(0.7,0.35,0.2))
report={}

# ===== A) ESTACIONAMENTOS (2175 m2, 168 ligeiros + 2 onibus) =====
lots=[("Estacionamento-Norte",60,45,30,24,56),("Estacionamento-Central",140,45,30,24,56),
      ("Estacionamento-Sul",225,45,30,24.5,56)]
park_area=0
for i,(nm,cx,cy,w,d,vagas) in enumerate(lots,1):
    z=tz(cx,cy)
    make_slab(nm,"Pavimento Univerde 15cm","BASESLAB",cx,cy,z,w,d,0.15,M_PAV,site)
    sp=make_space(nm,"Estacionamento de Veiculos Ligeiros",cx,cy,z,w,d,0.2,site,
                  {"NumeroVagas":vagas,"Tipo":"Veiculos Ligeiros","Pavimento":"Univerde permeavel"})
    park_area+=w*d
    # marcacoes de vagas (linhas) - 2 fileiras de stalls 2.5x5
    for row,yy in enumerate([cy-d/4,cy+d/4]):
        n=int(w//2.5)
        for k in range(n+1):
            xx=cx-w/2+k*2.5
            make_slab(f"Vaga-Linha-{nm}-{row}-{k}","Sinalizacao Vaga","NOTDEFINED",xx,yy,z+0.02,0.10,5.0,0.02,
                      material("Termoplastico Branco",(0.95,0.95,0.95)),site,below=False)
# vagas onibus
zb=tz(255,45); make_slab("Estacionamento-Onibus","Pavimento Asfalto","BASESLAB",255,45,zb,16,7,0.15,M_ASF,site)
make_space("Estacionamento-Onibus","Vagas de Onibus (2)",255,45,zb,16,7,0.2,site,{"NumeroVagas":2,"Tipo":"Onibus"})
park_area+=16*7
report["Estacionamentos"]=(f"{len(lots)} lotes + onibus", round(park_area,1), 168+2)

# ===== B) AREA DESPORTIVA (1168 m2) =====
courts=[("Quadra-Polidesportiva","Quadra Polidesportiva",315,35,32,19,M_POLI),
        ("Quadra-Padel","Quadra de Padel",345,72,20,10,M_PADEL),
        ("Quadra-Beach-Tennis-1","Beach Tennis 1",372,35,16,8,M_BEACH),
        ("Quadra-Beach-Tennis-2","Beach Tennis 2",372,48,16,8,M_BEACH)]
sport_area=0
for nm,ln,cx,cy,w,d,mat in courts:
    z=tz(cx,cy)
    make_slab(nm,ln,"BASESLAB",cx,cy,z,w,d,0.12,mat,site)
    make_space(nm,ln,cx,cy,z,w,d,0.2,site,{"Tipo":"Desportivo"})
    sport_area+=w*d
report["Area Desportiva"]=("4 quadras",round(sport_area,1),None)

# ===== C) PISTA DE CARROS INFANTIL (678 m2) =====
z=tz(390,230); make_slab("Pista-de-Carros-Infantil","Pista de Carros para Criancas","BASESLAB",390,230,z,38,18,0.10,M_ASF,site)
make_space("Pista-de-Carros-Infantil","Pista de Carros para Criancas",390,230,z,38,18,0.2,site,{"Tipo":"Recreativo"})
report["Pista de Carros"]=("1 pista",38*18,None)

# ===== D) SUBESTACAO (144.47 m2) =====
z=tz(385,150); b,st=make_building("Subestacao","Subestacao de Energia - 144.47 m2",385,150,z,"SUB-Terreo")
make_slab("SUB-Laje-Piso","Laje Piso","FLOOR",385,150,z,12,12,0.15,M_CONC,st,below=True)
for (dx,dy,ww,dd) in [(-6,0,0.2,12),(6,0,0.2,12),(0,-6,12,0.2),(0,6,12,0.2)]:
    make_wall("SUB-Parede",385+dx,150+dy,z,ww,dd,3.2,M_ALV,st)
make_slab("SUB-Cobertura","Cobertura","ROOF",385,150,z+3.3,12.4,12.4,0.15,M_CONC,st,below=False)
make_space("SUB-Sala","Sala de Equipamentos / Trafo",385,150,z,11.6,11.6,3.1,st,{"Tipo":"Tecnico"})
report["Subestacao"]=("edificio",144.0,None)

# ===== E) CENTRAL DE GAS (~30 m2) =====
z=tz(385,123); b,st=make_building("Central de Gas","Central de Gas (GLP)",385,123,z,"GAS-Terreo")
make_slab("GAS-Laje","Laje Piso","FLOOR",385,123,z,6,5,0.15,M_CONC,st,below=True)
for (dx,dy,ww,dd) in [(-3,0,0.2,5),(3,0,0.2,5),(0,-2.5,6,0.2),(0,2.5,6,0.2)]:
    make_wall("GAS-Parede",385+dx,123+dy,z,ww,dd,2.6,M_ALV,st)
make_space("GAS-Abrigo","Abrigo de Botijoes/Tanque GLP",385,123,z,5.6,4.6,2.5,st,{"Tipo":"Tecnico"})
report["Central de Gas"]=("edificio",30.0,None)

# ===== F) APOIO QUADRAS (94.80 m2) =====
z=tz(300,75); b,st=make_building("Apoio Quadras","Apoio as Quadras - vestiarios/bar - 94.80 m2",300,75,z,"APQ-Terreo")
make_slab("APQ-Laje","Laje Piso","FLOOR",300,75,z,12,8,0.15,M_CONC,st,below=True)
for (dx,dy,ww,dd) in [(-6,0,0.2,8),(6,0,0.2,8),(0,-4,12,0.2),(0,4,12,0.2)]:
    make_wall("APQ-Parede",300+dx,75+dy,z,ww,dd,3.0,M_ALV,st)
make_slab("APQ-Cobertura","Cobertura","ROOF",300,75,z+3.1,12.6,8.6,0.12,M_TELHA,st,below=False)
make_space("APQ-Vestiario","Vestiarios e Apoio das Quadras",300,75,z,11.6,7.6,2.9,st,{"Tipo":"Apoio"})
report["Apoio Quadras"]=("edificio",94.8,None)

# ===== G) SPA - AMPLIACAO (+~304 m2 -> ~598) =====
spa=[bb for bb in m.by_type("IfcBuilding") if bb.Name=="SPA"][0]
import ifcopenshell.util.element as E
spa_st=[stt for stt in m.by_type("IfcBuildingStorey") if E.get_aggregate(stt)==spa][0]
zc=12.8
# anexo a +X do SPA existente (envelope ate X92.5) -> 95..119
make_slab("SPA-Anexo-Laje","Laje Piso Anexo SPA","FLOOR",107,270,zc,24,14,0.15,M_CONC,spa_st,below=True)
for (dx,dy,ww,dd) in [(-12,0,0.2,14),(12,0,0.2,14),(0,-7,24,0.2),(0,7,24,0.2)]:
    make_wall("SPA-Anexo-Parede",107+dx,270+dy,zc,ww,dd,3.2,M_ALV,spa_st)
make_slab("SPA-Anexo-Cobertura","Cobertura Anexo","ROOF",107,270,zc+3.3,24.4,14.4,0.15,M_TELHA,spa_st,below=False)
ann=[("SAUNAS-SPA","Saunas e Termas",100,266,8,7),("TRAT-SPA","Salas de Tratamento",100,274,8,7),
     ("DECK-SPA","Deck Piscina Interior",112,267,11,9),("CIRC-SPA","Circulacao e Apoio SPA",112,275,11,5)]
spa_add=0
for nm,ln,cx,cy,w,d in ann:
    make_space(nm,ln,cx,cy,zc,w,d,3.0,spa_st,{"Tipo":"SPA"}); spa_add+=w*d
report["SPA (ampliacao)"]=("anexo",round(spa_add,1),None)

m.write("HVG_MASTER_v89_programa_completo.ifc")
print("=== ELEMENTOS CRIADOS ===")
for k,(t,a,n) in report.items():
    print(f"  {k:22} {t:14} area~{a} m2"+(f" | {n} vagas" if n else ""))
print("\nGravado: HVG_MASTER_v89_programa_completo.ifc")
