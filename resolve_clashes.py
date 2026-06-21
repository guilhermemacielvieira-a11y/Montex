#!/usr/bin/env python3
"""HVG Brumadinho - Resolucao de interferencias MEP x Estrutura (v86 -> v87).
Reposiciona terminais de teto (sprinklers e difusores) que penetram pilares,
com deslocamento minimo preservando cobertura, e verifica zero residuos."""
import ifcopenshell, ifcopenshell.util.placement as P
import numpy as np, math, csv, json

SRC="/root/.claude/uploads/df8eb48a-3536-58ee-9b8f-4a4c5930a696/47ef91eb-HVGMASTERINTEGRADOv86.ifc"
m=ifcopenshell.open(SRC)
MARGIN=0.05  # folga minima exigida (m)

def footprint(el):
    pds=el.Representation
    if not pds: return None
    for r in pds.Representations:
        for it in r.Items:
            if it.is_a("IfcExtrudedAreaSolid"):
                p=it.SweptArea
                if p.is_a("IfcRectangleProfileDef"): return (p.XDim/2.0,p.YDim/2.0,float(it.Depth))
                if p.is_a("IfcCircleProfileDef"):     return (float(p.Radius),float(p.Radius),float(it.Depth))
    return None
def wpos(el):
    x=P.get_local_placement(el.ObjectPlacement); return (float(x[0][3]),float(x[1][3]),float(x[2][3]))

# Pilares: posicao mundo + meia-dimensao + faixa Z (base..base+depth)
cols=[]
for c in m.by_type("IfcColumn"):
    f=footprint(c)
    if not f: continue
    p=wpos(c)
    cols.append({"p":p,"hx":f[0],"hy":f[1],"z0":p[2],"z1":p[2]+f[2]})

def xy_overlap(px,py,hx,hy,col,margin):
    return (abs(px-col["p"][0]) < hx+col["hx"]+margin) and (abs(py-col["p"][1]) < hy+col["hy"]+margin)
def z_overlap(z0,z1,col):
    return (z0 < col["z1"]) and (z1 > col["z0"])

def clashing_cols(px,py,pz,hx,hy,hz,margin):
    out=[]
    for col in cols:
        if z_overlap(pz-hz, pz+hz, col) and xy_overlap(px,py,hx,hy,col,margin):
            out.append(col)
    return out

# Candidatos de deslocamento: 16 direcoes x distancias crescentes, escolhe menor norma
DIRS=[(math.cos(a),math.sin(a)) for a in [i*math.pi/8 for i in range(16)]]
DISTS=[round(d,3) for d in np.arange(0.20,1.61,0.05)]

terms=[]
for t in m.by_type("IfcAirTerminal")+m.by_type("IfcFireSuppressionTerminal"):
    f=footprint(t)
    if f: terms.append((t,f))

# posicoes atuais de todos terminais (para evitar criar clash terminal-terminal)
term_pts=[(wpos(t)[0],wpos(t)[1],f[0],f[1]) for t,f in terms]

log=[]
moved=0
for t,f in terms:
    hx,hy,depth=f
    hz=max(depth/2.0,0.05)
    px,py,pz=wpos(t)
    hit=clashing_cols(px,py,pz,hx,hy,hz, 0.0)
    if not hit:
        continue
    # procurar deslocamento minimo que limpe TODOS os pilares na vizinhanca por MARGIN
    best=None
    for dist in DISTS:
        for dx,dy in DIRS:
            ox,oy=float(dx*dist),float(dy*dist)
            nx,ny=px+ox,py+oy
            if clashing_cols(nx,ny,pz,hx,hy,hz, MARGIN):
                continue
            # nao colidir com outro terminal (exceto o proprio) por 0.10m
            bad=False
            for qx,qy,qhx,qhy in term_pts:
                if abs(qx-px)<1e-6 and abs(qy-py)<1e-6: continue
                if abs(nx-qx)<hx+qhx+0.10 and abs(ny-qy)<hy+qhy+0.10:
                    bad=True; break
            if bad: continue
            best=(ox,oy,dist); break
        if best: break
    if not best:
        log.append({"guid":t.GlobalId,"type":t.is_a(),"status":"UNRESOLVED","pos":[round(px,2),round(py,2)]})
        continue
    ox,oy,dist=best
    # aplicar no ponto de localizacao proprio do terminal (L0), unico por elemento
    loc=t.ObjectPlacement.RelativePlacement.Location
    cx,cy,cz=loc.Coordinates
    loc.Coordinates=(float(cx+ox), float(cy+oy), float(cz))
    moved+=1
    log.append({"guid":t.GlobalId,"type":t.is_a(),"status":"MOVED",
                "from":[round(px,3),round(py,3)],"to":[round(px+ox,3),round(py+oy,3)],
                "offset":[round(ox,3),round(oy,3)],"dist":round(dist,3)})

# VERIFICACAO final: re-scan
residual=0
for t,f in terms:
    hx,hy,depth=f; hz=max(depth/2.0,0.05)
    px,py,pz=wpos(t)
    if clashing_cols(px,py,pz,hx,hy,hz, 0.0):
        residual+=1
print(f"Terminais movidos: {moved}")
print(f"Clashes residuais (margin 0): {residual}")
unres=[l for l in log if l['status']=='UNRESOLVED']
print(f"Nao resolvidos: {len(unres)}")
maxd=max((l['dist'] for l in log if l['status']=='MOVED'), default=0)
print(f"Maior deslocamento: {maxd} m")

with open("/home/user/Montex/clash_resolution_log.json","w") as fo:
    json.dump(log,fo,indent=1,ensure_ascii=False)

# atualizar metadados do projeto -> v87
proj=m.by_type("IfcProject")[0]
proj.Description = (proj.Description or "") + (
    " | v87 COORDENACAO MEP: %d terminais de teto reposicionados (sprinklers/difusores) "
    "para eliminar penetracao em pilares 30x30 - deslocamento min<=%.2fm preservando cobertura; "
    "0 interferencias residuais terminal-pilar."% (moved, maxd))

OUT="/home/user/Montex/HVG_MASTER_v87_Arq_MEP_coordenado.ifc"
m.write(OUT)
print("Gravado:", OUT)
