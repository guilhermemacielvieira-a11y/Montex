#!/usr/bin/env python3
"""HVG v89 -> v90: detalhamento LOD300 dos novos itens.
Subestacao (trafo, QGBT, eletrocalhas), Central de Gas (tanque GLP, rede, regulador, sistema GAS),
Quadras (postes de rede, alambrado, iluminacao esportiva)."""
import ifcopenshell, ifcopenshell.geom as geom, numpy as np
import ifcopenshell.util.element as E, ifcopenshell.util.placement as Pl
m=ifcopenshell.open("HVG_MASTER_v89_programa_completo.ifc")
oh=m.by_type("IfcOwnerHistory")[0]
site=m.by_type("IfcSite")[0]; site_pl=site.ObjectPlacement
ctx=[c for c in m.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier=="Body"][0]
def g(): return ifcopenshell.guid.new()
def dirn(t): return m.create_entity("IfcDirection",[float(a) for a in t])
def ptn(t): return m.create_entity("IfcCartesianPoint",[float(a) for a in t])
def plc(x,y,z,rel=None): return m.create_entity("IfcLocalPlacement",rel or site_pl,
    m.create_entity("IfcAxis2Placement3D",ptn((x,y,z)),dirn((0,0,1)),dirn((1,0,0))))
def style(rgb):
    col=m.create_entity("IfcColourRgb",None,*[float(c) for c in rgb])
    r=m.create_entity("IfcSurfaceStyleRendering",col,0.0,None,None,None,None,None,None,"NOTDEFINED")
    return m.create_entity("IfcPresentationStyleAssignment",[m.create_entity("IfcSurfaceStyle",None,"BOTH",[r])])
def box(w,d,h,zoff=0.0):
    pr=m.create_entity("IfcRectangleProfileDef","AREA",None,m.create_entity("IfcAxis2Placement2D",ptn((0.,0.)),dirn((1.,0.))),float(w),float(d))
    return m.create_entity("IfcExtrudedAreaSolid",pr,m.create_entity("IfcAxis2Placement3D",ptn((0.,0.,zoff)),dirn((0,0,1)),dirn((1,0,0)),),dirn((0,0,1)),float(h))
def cyl(r,h,axis=(0,0,1),zoff=0.0):
    pr=m.create_entity("IfcCircleProfileDef","AREA",None,m.create_entity("IfcAxis2Placement2D",ptn((0.,0.)),dirn((1.,0.))),float(r))
    ax=dirn(axis); ref=(1,0,0) if abs(axis[0])<0.9 else (0,1,0)
    return m.create_entity("IfcExtrudedAreaSolid",pr,m.create_entity("IfcAxis2Placement3D",ptn((0.,0.,zoff)),ax,dirn(ref)),dirn((0,0,1)),float(h))
def shp(sol,rgb):
    m.create_entity("IfcStyledItem",sol,[style(rgb)],None)
    return m.create_entity("IfcProductDefinitionShape",None,None,[m.create_entity("IfcShapeRepresentation",ctx,"Body","SweptSolid",[sol])])
_mats={}
def mat(name):
    if name not in _mats: _mats[name]=m.create_entity("IfcMaterial",name)
    return _mats[name]
def assoc(el,name): m.create_entity("IfcRelAssociatesMaterial",g(),oh,None,None,[el],mat(name))
def contain(el,struct):
    rel=next((r for r in struct.ContainsElements),None)
    if rel: rel.RelatedElements=list(rel.RelatedElements)+[el]
    else: m.create_entity("IfcRelContainedInSpatialStructure",g(),oh,None,None,[el],struct)
def to_system(els,sysname):
    sys=next((x for x in m.by_type("IfcDistributionSystem") if x.Name==sysname),None)
    rel=next((r for r in sys.IsGroupedBy),None)
    if rel: rel.RelatedObjects=list(rel.RelatedObjects)+els
    else: m.create_entity("IfcRelAssignsToGroup",g(),oh,None,None,els,None,sys)
def storey_of(bname):
    b=[x for x in m.by_type("IfcBuilding") if x.Name==bname][0]
    return [st for st in m.by_type("IfcBuildingStorey") if E.get_aggregate(st)==b][0], b

s=geom.settings(); s.set("use-world-coords",True)
V=np.array(geom.create_shape(s,site).geometry.verts).reshape(-1,3)
def tz(x,y): d=(V[:,0]-x)**2+(V[:,1]-y)**2; return float(V[np.argsort(d)[:8],2].mean())
created={}

# ===== SUBESTACAO LOD300 =====
sub_st,_=storey_of("Subestacao"); z=tz(385,150)
def mk(cls,name,x,y,zz,sol,rgb,matname,predef=None,extra_args=None):
    args=[g(),oh,name,None,None,plc(x,y,zz),shp(sol,rgb),None]
    if predef is not None: args.append(predef)
    el=m.create_entity(cls,*args)
    assoc(el,matname); return el
els=[]
# transformador a oleo 2.4x1.6x2.2
els.append(mk("IfcTransformer","SUB-Transformador-1000kVA",381,147,z,box(2.4,1.6,2.2),(0.45,0.45,0.5),"Aco/Oleo Transformador","VOLTAGE"))
els.append(mk("IfcTransformer","SUB-Transformador-1000kVA-2",381,153,z,box(2.4,1.6,2.2),(0.45,0.45,0.5),"Aco/Oleo Transformador","VOLTAGE"))
# cubiculos MT / QGBT
for i,(yy,nm) in enumerate([(146,"Cubiculo-MT"),(149,"QGBT"),(152,"Cubiculo-Medicao")]):
    els.append(mk("IfcElectricDistributionBoard",f"SUB-{nm}",389,yy,z,box(0.9,0.6,2.0),(0.3,0.35,0.4),"Chapa Aco Pintada"))
# eletrocalha perimetral
for (x0,y0,w,d) in [(385,145.2,11,0.3),(385,154.8,11,0.3)]:
    els.append(mk("IfcCableCarrierSegment","SUB-Eletrocalha",x0,y0,z+2.6,box(w,d,0.1),(0.6,0.6,0.65),"Bandeja Eletrica Galvanizada"))
for e in els: contain(e,sub_st)
to_system(els,"ELE-EletricaIluminacao")
created["Subestacao (trafo/QGBT/MT/calha)"]=len(els)

# ===== CENTRAL DE GAS LOD300 + sistema GAS =====
gas_st,gas_b=storey_of("Central de Gas"); z=tz(385,123)
gels=[]
# tanque GLP horizontal cilindrico (deitado, eixo X) ~2.5m, R0.6
tank=m.create_entity("IfcTank",g(),oh,"GAS-Tanque-GLP-2000L",None,None,plc(385,123,z+0.7,),shp(cyl(0.6,2.5,axis=(1,0,0)),(0.9,0.9,0.85)),None,"STORAGE")
assoc(tank,"Aco Carbono Tanque GLP"); gels.append(tank)
# regulador / valvula
val=m.create_entity("IfcValve",g(),oh,"GAS-Regulador-1ofEstagioM",None,None,plc(383.2,123,z+0.6,),shp(box(0.2,0.2,0.3),(0.8,0.3,0.2)),None,"PRESSUREREDUCING")
assoc(val,"Bronze/Latao"); gels.append(val)
# rede de gas (tubo aco) do tanque ate a parede + ate o bloco principal (trecho)
for i,(x0,y0,L,ax) in enumerate([(383,123,3.0,(-1,0,0)),(380,123,2.0,(0,1,0))]):
    p=m.create_entity("IfcPipeSegment",g(),oh,f"GAS-Tubo-Aco-{i+1}",None,None,plc(x0,y0,z+0.5,),shp(cyl(0.03,L,axis=ax),(0.85,0.75,0.1)),None,"RIGIDSEGMENT")
    assoc(p,"Tubo Aco SCH40 Gas"); gels.append(p)
for e in gels: contain(e,gas_st)
# novo sistema GAS
gsys=m.create_entity("IfcDistributionSystem",g(),oh,"GAS-CombustivelGLP","Sistema de Gas Combustivel (GLP)",None,"GAS")
m.create_entity("IfcRelAssignsToGroup",g(),oh,None,None,gels,None,gsys)
m.create_entity("IfcRelServicesBuildings",g(),oh,None,None,gsys,[gas_b])
created["Central de Gas (tanque/regulador/rede + sistema GAS)"]=len(gels)

# ===== QUADRAS LOD300 (postes de rede, alambrado, iluminacao) =====
qels=[]; lels=[]
courts={"Quadra-Polidesportiva":(315,35,32,19),"Quadra-Padel":(345,72,20,10),
        "Quadra-Beach-Tennis-1":(372,35,16,8),"Quadra-Beach-Tennis-2":(372,48,16,8)}
for nm,(cx,cy,w,d) in courts.items():
    z=tz(cx,cy)
    # 2 postes de rede no meio (eixo menor)
    for sx in (-1,1):
        post=m.create_entity("IfcMember",g(),oh,f"{nm}-Poste-Rede",None,None,plc(cx,cy+sx*d/2,z,),shp(box(0.08,0.08,2.0),(0.7,0.7,0.7)),None,"POST")
        assoc(post,"Aco Galvanizado"); qels.append(post)
    # rede (tela fina) entre postes
    net=m.create_entity("IfcRailing",g(),oh,f"{nm}-Rede",None,None,plc(cx,cy,z+0.8,),shp(box(0.02,d,0.9),(0.1,0.1,0.1)),None,"USERDEFINED")
    assoc(net,"Rede Polietileno"); qels.append(net)
    # 4 postes de iluminacao com luminaria
    for sx in (-1,1):
        for sy in (-1,1):
            px,py=cx+sx*(w/2+0.5),cy+sy*(d/2+0.5)
            pole=m.create_entity("IfcMember",g(),oh,f"{nm}-Poste-Iluminacao",None,None,plc(px,py,z,),shp(cyl(0.06,6.0),(0.55,0.55,0.55)),None,"POST")
            assoc(pole,"Aco Galvanizado"); qels.append(pole)
            lum=m.create_entity("IfcLightFixture",g(),oh,f"{nm}-Refletor-LED",None,None,plc(px,py,z+6.0,),shp(box(0.4,0.25,0.15),(0.95,0.95,0.8)),None,"DIRECTIONSOURCE")
            assoc(lum,"Refletor LED 400W"); lels.append(lum)
# alambrado da polidesportiva (perimetro, 4 lados)
cx,cy,w,d=courts["Quadra-Polidesportiva"]; z=tz(cx,cy)
for (dx,dy,ww,dd) in [(-w/2,0,0.05,d),(w/2,0,0.05,d),(0,-d/2,w,0.05),(0,d/2,w,0.05)]:
    f=m.create_entity("IfcRailing",g(),oh,"Alambrado-Polidesportivo",None,None,plc(cx+dx,cy+dy,z,),shp(box(ww,dd,4.0),(0.5,0.55,0.5)),None,"USERDEFINED")
    assoc(f,"Alambrado Aco Galvanizado"); qels.append(f)
allq=qels+lels
for e in allq:
    # contidos no site (elementos externos)
    contain(e,site)
to_system(lels,"ELE-EletricaIluminacao")
created["Quadras (postes/rede/alambrado/iluminacao)"]=len(allq)

m.write("HVG_MASTER_v90_LOD300.ifc")
print("=== DETALHAMENTO LOD300 ===")
for k,v in created.items(): print(f"  {k}: {v} elementos")
print("Sistemas agora:",[x.Name for x in m.by_type("IfcDistributionSystem")])
print("Gravado: HVG_MASTER_v90_LOD300.ifc")
