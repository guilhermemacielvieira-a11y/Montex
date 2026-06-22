"""
QA Final Consolidado — HVG_MASTER_v92_alinhado.ifc
Cobre: integridade, contenção espacial, materiais, clashes,
       geometria/cotas, varandas/guarda-corpos, coberturas, janelas.
"""
import ifcopenshell
import ifcopenshell.util.element as ifc_elem
import math, collections, datetime

IFC_PATH = "/home/user/Montex/HVG_MASTER_v92_alinhado.ifc"

print("=" * 70)
print("QA FINAL CONSOLIDADO — v92")
print(f"Arquivo : {IFC_PATH}")
print(f"Data    : {datetime.date.today()}")
print("=" * 70)

model = ifcopenshell.open(IFC_PATH)
issues = []

# ─────────────────────────────────────────────────────────────────────────────
# 1. INTEGRIDADE DE SCHEMA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 1 ] INTEGRIDADE DE SCHEMA")

schema = model.schema
total_entities = len(list(model))
print(f"  Schema      : {schema}")
print(f"  Total entid.: {total_entities:,}")

# GUIDs duplicados
all_elements = list(model.by_type("IfcRoot"))
guids = [e.GlobalId for e in all_elements]
guid_counts = collections.Counter(guids)
dupes = {g: c for g, c in guid_counts.items() if c > 1}
if dupes:
    issues.append(f"GUIDs duplicados: {len(dupes)}")
    print(f"  GUIDs duplicados : {len(dupes)}  ⚠️")
else:
    print(f"  GUIDs únicos     : {len(all_elements)} ✅")

# Pontos cartesianos inválidos
pts = model.by_type("IfcCartesianPoint")
bad_pts = [p for p in pts if any(
    (v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))))
    for v in (p.Coordinates or [])
)]
dirs_ = model.by_type("IfcDirection")
bad_dirs = [d for d in dirs_ if any(
    (v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))))
    for v in (d.DirectionRatios or [])
)]
print(f"  Pontos inválidos : {len(bad_pts)}")
print(f"  Direções inválidas: {len(bad_dirs)}")
if bad_pts: issues.append(f"Pontos cartesianos inválidos: {len(bad_pts)}")
if bad_dirs: issues.append(f"Direções inválidas: {len(bad_dirs)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CONTENÇÃO ESPACIAL
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 2 ] CONTENÇÃO ESPACIAL")

contained = set()
for rel in model.by_type("IfcRelContainedInSpatialStructure"):
    for el in (rel.RelatedElements or []):
        contained.add(el.id())

# Elementos físicos que deveriam estar contidos
physical_types = (
    "IfcWall","IfcSlab","IfcColumn","IfcBeam","IfcDoor","IfcWindow",
    "IfcRailing","IfcRoof","IfcStair","IfcFurnishingElement",
    "IfcFlowSegment","IfcFlowFitting","IfcEnergyConversionDevice",
    "IfcDistributionControlElement","IfcMember","IfcPlate",
    "IfcCovering","IfcBuildingElementProxy"
)
not_contained = []
for t in physical_types:
    for el in model.by_type(t):
        if el.id() not in contained:
            not_contained.append(el)

pct_ok = (1 - len(not_contained) / max(len(contained) + len(not_contained), 1)) * 100
print(f"  Contidos   : {len(contained):,}")
print(f"  Sem cont.  : {len(not_contained):,}  ({pct_ok:.1f}% OK)")
if len(not_contained) > 50:
    issues.append(f"Elementos sem contenção espacial: {len(not_contained)}")

by_type_nc = collections.Counter(el.is_a() for el in not_contained)
if by_type_nc:
    for t, c in by_type_nc.most_common(5):
        print(f"    {t}: {c}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. MATERIAIS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 3 ] MATERIAIS")

def get_material(element):
    for rel in model.by_type("IfcRelAssociatesMaterial"):
        if element in (rel.RelatedObjects or []):
            mat = rel.RelatingMaterial
            if mat:
                if mat.is_a("IfcMaterial"):
                    return mat.Name
                if mat.is_a("IfcMaterialLayerSetUsage"):
                    ls = mat.ForLayerSet
                    if ls and ls.MaterialLayers:
                        return ls.MaterialLayers[0].Material.Name if ls.MaterialLayers[0].Material else None
                if mat.is_a("IfcMaterialLayerSet"):
                    if mat.MaterialLayers:
                        return mat.MaterialLayers[0].Material.Name if mat.MaterialLayers[0].Material else None
                if mat.is_a("IfcMaterialList"):
                    if mat.Materials:
                        return mat.Materials[0].Name if mat.Materials[0] else None
                if mat.is_a("IfcMaterialConstituentSet"):
                    if mat.MaterialConstituents:
                        return mat.MaterialConstituents[0].Material.Name if mat.MaterialConstituents[0].Material else None
    return None

check_types = ["IfcSlab","IfcWall","IfcColumn","IfcBeam","IfcRoof","IfcCovering","IfcRailing"]
mat_summary = {}
for t in check_types:
    elements = model.by_type(t)
    no_mat = [e for e in elements if get_material(e) is None]
    mat_summary[t] = (len(elements), len(no_mat))
    status = "✅" if len(no_mat) == 0 else "⚠️"
    print(f"  {t:<30} total={len(elements):4d}  sem mat={len(no_mat):4d}  {status}")
    if len(no_mat) > 0 and t in ("IfcSlab","IfcWall","IfcColumn"):
        issues.append(f"{t} sem material: {len(no_mat)}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. VARANDAS — guarda-corpos
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 4 ] VARANDAS — GUARDA-CORPOS")

# Lajes classificadas como varanda
varanda_slabs = [s for s in model.by_type("IfcSlab")
                 if s.Name and "varanda" in s.Name.lower()]
if not varanda_slabs:
    # Tenta por ObjectType
    varanda_slabs = [s for s in model.by_type("IfcSlab")
                     if s.ObjectType and "varanda" in s.ObjectType.lower()]
print(f"  Lajes de varanda encontradas: {len(varanda_slabs)}")

# Guarda-corpos (railings)
all_railings = model.by_type("IfcRailing")
print(f"  Guarda-corpos totais       : {len(all_railings)}")

# Verifica material nos railings
railings_no_mat = [r for r in all_railings if get_material(r) is None]
print(f"  Railings sem material      : {len(railings_no_mat)}")
if railings_no_mat:
    issues.append(f"Railings sem material: {len(railings_no_mat)}")

# Verifica conteúdo espacial dos railings
railings_not_cont = [r for r in all_railings if r.id() not in contained]
print(f"  Railings sem contenção     : {len(railings_not_cont)}")
if railings_not_cont:
    issues.append(f"Railings sem contenção espacial: {len(railings_not_cont)}")

if len(varanda_slabs) > 0 and len(all_railings) >= len(varanda_slabs):
    print(f"  Ratio railings/varandas    : {len(all_railings)}/{len(varanda_slabs)} ✅")
elif len(varanda_slabs) > 0:
    print(f"  Ratio railings/varandas    : {len(all_railings)}/{len(varanda_slabs)} ⚠️")
    issues.append(f"Poucos guarda-corpos: {len(all_railings)} para {len(varanda_slabs)} lajes de varanda")

# ─────────────────────────────────────────────────────────────────────────────
# 5. JANELAS / ESQUADRIAS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 5 ] JANELAS / ESQUADRIAS")

windows = model.by_type("IfcWindow")
doors   = model.by_type("IfcDoor")
print(f"  Janelas (IfcWindow) : {len(windows)}")
print(f"  Portas  (IfcDoor)   : {len(doors)}")

# Janelas sem material
win_no_mat = [w for w in windows if get_material(w) is None]
print(f"  Janelas sem material: {len(win_no_mat)}")

# Verificar alinhamento vertical das janelas (dZ consistente entre pisos)
def get_z(elem):
    try:
        pl = elem.ObjectPlacement
        if pl and pl.is_a("IfcLocalPlacement"):
            ax = pl.RelativePlacement
            if ax and ax.is_a("IfcAxis2Placement3D"):
                loc = ax.Location
                if loc:
                    return loc.Coordinates[2]
    except Exception:
        pass
    return None

win_zs = [get_z(w) for w in windows]
win_zs = [z for z in win_zs if z is not None]
if win_zs:
    z_rounded = collections.Counter(round(z, 1) for z in win_zs)
    print(f"  Z-coords distintas (arred.0.1m): {len(z_rounded)}")
    for z, cnt in sorted(z_rounded.most_common(8)):
        print(f"    Z={z:7.2f}m → {cnt} janelas")

# ─────────────────────────────────────────────────────────────────────────────
# 6. COBERTURAS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 6 ] COBERTURAS")

roofs = model.by_type("IfcRoof")
coverings = model.by_type("IfcCovering")
slabs_roof = [s for s in model.by_type("IfcSlab")
              if s.PredefinedType and "ROOF" in str(s.PredefinedType).upper()]
print(f"  IfcRoof            : {len(roofs)}")
print(f"  IfcCovering        : {len(coverings)}")
print(f"  IfcSlab ROOF type  : {len(slabs_roof)}")

roofs_no_mat = [r for r in roofs if get_material(r) is None]
cov_no_mat   = [c for c in coverings if get_material(c) is None]
print(f"  Roofs sem material    : {len(roofs_no_mat)}")
print(f"  Coverings sem material: {len(cov_no_mat)}")
if roofs_no_mat: issues.append(f"IfcRoof sem material: {len(roofs_no_mat)}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. ESTRUTURA — COTAS BÁSICAS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 7 ] ESTRUTURA — COTAS BÁSICAS")

columns = model.by_type("IfcColumn")
beams   = model.by_type("IfcBeam")
slabs   = model.by_type("IfcSlab")
walls   = model.by_type("IfcWall")
print(f"  Pilares  : {len(columns)}")
print(f"  Vigas    : {len(beams)}")
print(f"  Lajes    : {len(slabs)}")
print(f"  Paredes  : {len(walls)}")

# Piso a piso via Z das lajes (base)
slab_zs = [get_z(s) for s in slabs]
slab_zs = sorted(set(round(z, 2) for z in slab_zs if z is not None))
print(f"  Níveis de laje (Z distintos, arred. 2cm) : {len(slab_zs)}")
if slab_zs:
    for z in slab_zs[:10]:
        print(f"    Z = {z:.2f} m")
    if len(slab_zs) > 10:
        print(f"    ... e mais {len(slab_zs)-10} níveis")

# Diffs entre pisos consecutivos (pé-direito estimado)
if len(slab_zs) >= 2:
    diffs = [round(slab_zs[i+1] - slab_zs[i], 2) for i in range(min(6, len(slab_zs)-1))]
    pd_cnt = collections.Counter(diffs)
    print(f"  Pé-direito (diffs entre níveis) : {dict(pd_cnt)}")
    most_common_pd = pd_cnt.most_common(1)[0][0]
    if not (2.4 <= most_common_pd <= 4.5):
        issues.append(f"Pé-direito atípico: {most_common_pd} m")

# ─────────────────────────────────────────────────────────────────────────────
# 8. CLASH DETECTION (broad-phase AABB)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 8 ] CLASH DETECTION (broad-phase AABB)")

def get_bbox(elem):
    """Retorna (xmin,ymin,zmin,xmax,ymax,zmax) via placement + sizes se disponível."""
    z = get_z(elem)
    if z is None:
        return None
    try:
        pl = elem.ObjectPlacement
        ax = pl.RelativePlacement
        loc = ax.Location.Coordinates
        x, y = loc[0], loc[1]
        # Tenta OverallWidth/OverallHeight para janelas e portas
        w = getattr(elem, "OverallWidth", None) or 1.0
        h = getattr(elem, "OverallHeight", None) or 2.5
        return (x - w/2, y - 0.1, z, x + w/2, y + 0.1, z + h)
    except Exception:
        return None

# Clash simples: MEP × estrutura (apenas contagem por tipo)
mep_elements = (list(model.by_type("IfcFlowSegment")) +
                list(model.by_type("IfcFlowFitting")) +
                list(model.by_type("IfcDistributionFlowElement")))
struct_elements = columns + list(beams) + list(slabs)

print(f"  Elementos MEP    : {len(mep_elements)}")
print(f"  Elementos estrut.: {len(struct_elements)}")

# Broad-phase clash por bounding box XY apenas (rápido, sem geometria)
def xy_bbox(elem):
    try:
        pl = elem.ObjectPlacement
        ax = pl.RelativePlacement
        loc = ax.Location.Coordinates
        return (loc[0], loc[1])
    except Exception:
        return None

clash_count = 0
tol = 0.3  # 30 cm tolerância broad-phase
mep_xys = [(xy_bbox(e), e) for e in mep_elements]
mep_xys = [(xy, e) for xy, e in mep_xys if xy]
struct_xys = [(xy_bbox(e), e) for e in struct_elements]
struct_xys = [(xy, e) for xy, e in struct_xys if xy]

for (mx, my), me in mep_xys:
    for (sx, sy), se in struct_xys:
        if abs(mx - sx) < tol and abs(my - sy) < tol:
            clash_count += 1
            break

print(f"  Potenciais clashes MEP×Estrut. (broad XY, tol={tol}m): {clash_count}")
if clash_count > 20:
    issues.append(f"Clashes potenciais MEP×Estrutura: {clash_count}")
else:
    print("  Resultado aceitável ✅")

# ─────────────────────────────────────────────────────────────────────────────
# 9. 4D — CRONOGRAMA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 9 ] 4D — CRONOGRAMA")

work_plans  = model.by_type("IfcWorkPlan")
work_scheds = model.by_type("IfcWorkSchedule")
tasks       = model.by_type("IfcTask")
rel_proc    = model.by_type("IfcRelAssignsToProcess")
print(f"  IfcWorkPlan      : {len(work_plans)}")
print(f"  IfcWorkSchedule  : {len(work_scheds)}")
print(f"  IfcTask          : {len(tasks)}")
print(f"  RelAssignsToProc.: {len(rel_proc)}")
if not tasks:
    issues.append("Nenhum IfcTask encontrado (4D ausente)")

# ─────────────────────────────────────────────────────────────────────────────
# 10. GRIDS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 10 ] GRIDS")

grids = model.by_type("IfcGrid")
print(f"  IfcGrid : {len(grids)}")
for g in grids:
    nu = len(g.UAxes or [])
    nv = len(g.VAxes or [])
    print(f"    {g.Name or '?'}  U={nu}  V={nv}")
if not grids:
    issues.append("Nenhum IfcGrid no modelo")

# ─────────────────────────────────────────────────────────────────────────────
# 11. SISTEMAS DE DISTRIBUIÇÃO (MEP)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[ 11 ] SISTEMAS DE DISTRIBUIÇÃO")

systems = model.by_type("IfcDistributionSystem")
print(f"  Sistemas MEP : {len(systems)}")
for s in systems:
    print(f"    {s.Name or '?'}  type={s.PredefinedType}")

# ─────────────────────────────────────────────────────────────────────────────
# RESUMO FINAL
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("RESUMO DE QA")
print("=" * 70)
if issues:
    print(f"  Problemas encontrados: {len(issues)}")
    for i, iss in enumerate(issues, 1):
        print(f"  {i}. {iss}")
else:
    print("  Sem problemas críticos detectados ✅")

print(f"\n  Schema    : {schema}")
print(f"  Entidades : {total_entities:,}")
print(f"  Pilares   : {len(columns)}")
print(f"  Vigas     : {len(beams)}")
print(f"  Lajes     : {len(slabs)}")
print(f"  Paredes   : {len(walls)}")
print(f"  Janelas   : {len(windows)}")
print(f"  Portas    : {len(doors)}")
print(f"  Railings  : {len(all_railings)}")
print(f"  IfcTask   : {len(tasks)}")
print(f"  IfcGrid   : {len(grids)}")
print("=" * 70)
print("QA concluído.")
