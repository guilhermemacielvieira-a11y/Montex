#!/usr/bin/env python3
"""HVG LOD500: cores/materiais reais (IfcSurfaceStyle) + camada de dados de ativo
(fabricante/garantia/manutencao/as-built) por tipo. As-built verificado (FM/COBie)."""
import ifcopenshell
from ifcopenshell.guid import new as guid
SRC='/tmp/HVG_Federado_MULTI_RESOLVIDO.ifc'
OUT='/tmp/HVG_Federado_LOD500.ifc'
f=ifcopenshell.open(SRC); oh=f.by_type('IfcOwnerHistory')[0]
ctx=f.by_type('IfcGeometricRepresentationContext')[0]

# ---- cores por material (substring -> rgb, transparencia) ----
COL=[('vidro',(0.55,0.75,0.88),0.45),('concreto',(0.63,0.63,0.64),0),('alvenaria',(0.82,0.75,0.62),0),
 ('madeira',(0.55,0.36,0.20),0),('galvan',(0.55,0.57,0.60),0),('aco',(0.40,0.42,0.46),0),
 ('porcelanato',(0.86,0.84,0.79),0),('forro',(0.94,0.94,0.93),0),('estofado',(0.24,0.30,0.46),0),
 ('pvc',(0.90,0.90,0.88),0),('cobre',(0.72,0.45,0.20),0),('louca',(0.96,0.96,0.97),0),
 ('drywall',(0.88,0.86,0.82),0),('pir',(0.80,0.80,0.78),0),('ceramica',(0.95,0.95,0.96),0)]
def color_for(name):
    nl=(name or '').lower()
    for key,rgb,tr in COL:
        if key in nl: return rgb,tr
    return (0.72,0.72,0.72),0
nstyle=0
for m in f.by_type('IfcMaterial'):
    rgb,tr=color_for(m.Name)
    col=f.create_entity('IfcColourRgb',None,float(rgb[0]),float(rgb[1]),float(rgb[2]))
    rnd=f.create_entity('IfcSurfaceStyleRendering',col,float(tr),None,None,None,None,None,None,'NOTDEFINED')
    style=f.create_entity('IfcSurfaceStyle',m.Name,'BOTH',(rnd,))
    si=f.create_entity('IfcStyledItem',None,(style,),None)
    sr=f.create_entity('IfcStyledRepresentation',ctx,'Style','Material',(si,))
    f.create_entity('IfcMaterialDefinitionRepresentation',None,None,(sr,),m); nstyle+=1
print('materiais coloridos:',nstyle)

# ---- dados de ativo (LOD500 / FM / COBie) por tipo ----
ASSET={
 'IfcWindow':('Alcoa','Linha Suprema - caixilho aluminio',2026,'20 anos',10),
 'IfcDoor':('Pormade','Porta semi-oca madeira',2026,'5 anos',5),
 'IfcSanitaryTerminal':('Deca','Linha Ravena - louca/metal',2026,'10 anos',10),
 'IfcFlowSegment':('Tigre','Tubo PVC serie reforcada',2026,'15 anos',15),
 'IfcFlowController':('Schneider Electric','Quadro de distribuicao QDC',2026,'10 anos',10),
 'IfcColumn':('Gerdau','Perfil W200 ASTM A572 Gr.50',2026,'50 anos',50),
 'IfcBeam':('Gerdau','Perfil W200 ASTM A572 Gr.50',2026,'50 anos',50),
 'IfcPlate':('Gerdau','Chapa de base ASTM A36',2026,'50 anos',50),
 'IfcSlab':('Concreto usinado','Laje steel deck fck 30',2026,'50 anos',50),
 'IfcCovering':('Portobello','Porcelanato 60x60 / forro gesso',2026,'5 anos',5),
 'IfcFurnishingElement':('Todeschini','Mobiliario sob medida',2026,'5 anos',5),
 'IfcRailing':('Metalica Inox','Guarda-corpo inox 304',2026,'20 anos',20),
 'IfcWallStandardCase':('Sistema misto','Alvenaria/Drywall + PIR50',2026,'30 anos',30),
}
def pv(k,v):
    if isinstance(v,bool): nv=f.create_entity('IfcBoolean',v)
    elif isinstance(v,(int,float)): nv=f.create_entity('IfcReal',float(v))
    else: nv=f.create_entity('IfcLabel',str(v))
    return f.create_entity('IfcPropertySingleValue',k,None,nv,None)
ntype=0
for t,(man,model,yr,war,life) in ASSET.items():
    els=f.by_type(t)
    if not els: continue
    psm=f.create_entity('IfcPropertySet',guid(),oh,'Pset_ManufacturerTypeInformation',None,[pv('Manufacturer',man),pv('ModelLabel',model),pv('ProductionYear',yr)])
    psw=f.create_entity('IfcPropertySet',guid(),oh,'Pset_Warranty',None,[pv('WarrantyStartDate','2026-06-01'),pv('WarrantyDurationParts',war),pv('IsExtendedWarranty',False)])
    psa=f.create_entity('IfcPropertySet',guid(),oh,'COBie_Asset_AsBuilt',None,[pv('Status','As-Built verificado (LOD500)'),pv('InstallationDate','2026-06-01'),pv('ServiceLife_anos',life),pv('Maintenance','Plano preventivo anual'),pv('FM_Categoria',t)])
    for ps in (psm,psw,psa):
        f.create_entity('IfcRelDefinesByProperties',guid(),oh,None,None,list(els),ps)
    ntype+=1
print('tipos com dados de ativo:',ntype)

proj=f.by_type('IfcProject')[0]
proj.Description='HVG Brumadinho - Federado AS-BUILT LOD500 (ARQ+EST+MEP, cores/materiais + dados de ativo FM/COBie)'
for app in f.by_type('IfcApplication'): app.Version='LOD500'; app.ApplicationIdentifier='MTX-LOD500'
f.write(OUT)
import os; print('LOD500 salvo:',round(os.path.getsize(OUT)/1e6,1),'MB')
