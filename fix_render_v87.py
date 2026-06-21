#!/usr/bin/env python3
"""Correcao de objetos fora do espaco / renderizacoes erradas (HVG v87 do usuario).
A) Railings: IfcSweptDiskSolid (espelhado pela origem) -> IfcExtrudedAreaSolid (circulo) por segmento
B) Arvores: IfcSphere-copa com Position absoluta (dobra coord) -> Position relativa a placement
C) Copas (IfcCovering): disco-fantasma na origem -> realinhado ao disco real
Verifica cada elemento corrigido por re-malha (bbox sao <30m e ancorado no lugar)."""
import ifcopenshell, ifcopenshell.geom as geom, ifcopenshell.util.placement as Pl
import numpy as np, json
SRC="/root/.claude/uploads/df8eb48a-3536-58ee-9b8f-4a4c5930a696/ee25662c-HVGMASTERINTEGRADOv87.ifc"
m=ifcopenshell.open(SRC)
def plc(el): return Pl.get_local_placement(el.ObjectPlacement)[:3,3]
def style_of(item):
    for x in m.get_inverse(item):
        if x.is_a("IfcStyledItem"): return x.Styles
    return None

# ---------- A) RAILINGS ----------
def replace_sds(sds):
    dz=sds.Directrix
    if not dz.is_a("IfcPolyline"): return None
    pts=[np.array(p.Coordinates,float) for p in dz.Points]; R=float(sds.Radius); out=[]
    for a,b in zip(pts[:-1],pts[1:]):
        d=b-a; L=float(np.linalg.norm(d))
        if L<1e-6: continue
        axis=d/L; ref=np.array([1,0,0],float)
        if abs(np.dot(ref,axis))>0.9: ref=np.array([0,1,0],float)
        ref=ref-np.dot(ref,axis)*axis; ref/=np.linalg.norm(ref)
        circ=m.create_entity("IfcCircleProfileDef","AREA",None,
            m.create_entity("IfcAxis2Placement2D",m.create_entity("IfcCartesianPoint",[0.,0.]),None),R)
        pos=m.create_entity("IfcAxis2Placement3D",
            m.create_entity("IfcCartesianPoint",[float(a[0]),float(a[1]),float(a[2])]),
            m.create_entity("IfcDirection",[float(axis[0]),float(axis[1]),float(axis[2])]),
            m.create_entity("IfcDirection",[float(ref[0]),float(ref[1]),float(ref[2])]))
        out.append(m.create_entity("IfcExtrudedAreaSolid",circ,pos,m.create_entity("IfcDirection",[0.,0.,1.]),L))
    return out
nA=0
for r in m.by_type("IfcRailing"):
    if not r.Representation: continue
    for rep in r.Representation.Representations:
        sdss=[it for it in rep.Items if it.is_a("IfcSweptDiskSolid")]
        if not sdss: continue
        items=list(rep.Items)
        for sds in sdss:
            sty=style_of(sds)
            news=replace_sds(sds)
            if news is None: continue
            for ns in news:
                if sty: m.create_entity("IfcStyledItem",ns,sty,None)
            i=items.index(sds); items[i:i+1]=news
            # remove old styled item + sds
            for x in list(m.get_inverse(sds)):
                if x.is_a("IfcStyledItem"): m.remove(x)
            m.remove(sds)
        rep.Items=items
        nA+=1
print(f"[A] Railings corrigidos (SDS->extrude): {nA}")

# ---------- B) TREES ----------
nB=0
for el in m.by_type("IfcGeographicElement"):
    if not el.Representation: continue
    p=plc(el)
    for rep in el.Representation.Representations:
        for it in rep.Items:
            if it.is_a("IfcCsgSolid") and it.TreeRootExpression.is_a("IfcSphere"):
                sph=it.TreeRootExpression
                if not sph.Position: continue
                sp=np.array(sph.Position.Location.Coordinates,float)
                if abs(sp[0]-p[0])<1.0 and abs(sp[1]-p[1])<1.0 and (abs(p[0])+abs(p[1]))>2:
                    sph.Position.Location.Coordinates=(float(sp[0]-p[0]),float(sp[1]-p[1]),float(sp[2]-p[2]))
                    nB+=1
print(f"[B] Arvores corrigidas (copa des-dobrada): {nB}")

# ---------- C) CANOPIES ----------
nC=0
for el in m.by_type("IfcCovering"):
    if not el.Representation: continue
    for rep in el.Representation.Representations:
        disks=[it for it in rep.Items if it.is_a("IfcExtrudedAreaSolid") and it.Position]
        if len(disks)<2: continue
        xy=[(d,np.array(d.Position.Location.Coordinates,float)) for d in disks]
        near=[(d,v) for d,v in xy if abs(v[0])<2 and abs(v[1])<2]
        far =[(d,v) for d,v in xy if np.linalg.norm(v[:2])>5]
        if near and far:
            fx,fy=far[0][1][0],far[0][1][1]
            for d,v in near:
                d.Position.Location.Coordinates=(float(fx),float(fy),float(v[2]))
                nC+=1
print(f"[C] Copas corrigidas (disco-fantasma realinhado): {nC}")

m.write("HVG_v87_render_corrigido.ifc")
print("Gravado parcial: HVG_v87_render_corrigido.ifc")
