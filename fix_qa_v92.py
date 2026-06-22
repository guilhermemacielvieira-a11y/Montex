"""
Correções QA v92:
 A) 4 IfcRailing sem IfcMaterial  → Vidro Laminado 8mm / Aço Inox
 B) 447 IfcCovering sem material  → cerâmica/porcelanato/argamassa por ObjectType
 C) 4 IfcRoof sem contenção espacial → vincula ao andar correto
Saída: HVG_MASTER_v92b_qa.ifc
"""
import ifcopenshell, ifcopenshell.util.element as ifc_elem
import uuid, math, collections

SRC  = "/home/user/Montex/HVG_MASTER_v92_alinhado.ifc"
DEST = "/home/user/Montex/HVG_MASTER_v92b_qa.ifc"

model = ifcopenshell.open(SRC)
owner = model.by_type("IfcOwnerHistory")[0] if model.by_type("IfcOwnerHistory") else None

# ─── helpers ─────────────────────────────────────────────────────────────────
def new_guid():
    return ifcopenshell.guid.compress(uuid.uuid4().hex)

def get_material_rel(element):
    for rel in model.by_type("IfcRelAssociatesMaterial"):
        if element in (rel.RelatedObjects or []):
            return rel
    return None

def has_material(element):
    return get_material_rel(element) is not None

def make_material(name):
    return model.create_entity("IfcMaterial", Name=name)

def assign_material(element, mat_entity):
    existing = get_material_rel(element)
    if existing:
        objs = list(existing.RelatedObjects)
        if element not in objs:
            objs.append(element)
            existing.RelatedObjects = objs
    else:
        model.create_entity(
            "IfcRelAssociatesMaterial",
            GlobalId=new_guid(),
            OwnerHistory=owner,
            RelatedObjects=[element],
            RelatingMaterial=mat_entity,
        )

def get_z(elem):
    try:
        pl = elem.ObjectPlacement
        ax = pl.RelativePlacement
        return ax.Location.Coordinates[2]
    except Exception:
        return None

# ─── A) Railings sem material ────────────────────────────────────────────────
print("A) Corrigindo railings sem material...")
mat_vidro  = make_material("Vidro Laminado 8mm")
mat_inox   = make_material("Aço Inoxidável AISI-316")

fixed_rail = 0
for railing in model.by_type("IfcRailing"):
    if not has_material(railing):
        name = (railing.Name or "").lower()
        mat = mat_inox if "corrimao" in name or "corrimão" in name else mat_vidro
        assign_material(railing, mat)
        fixed_rail += 1
print(f"   Railings corrigidos: {fixed_rail}")

# ─── B) Coverings sem material ───────────────────────────────────────────────
print("B) Corrigindo coverings sem material...")

mat_map = {
    # ObjectType keywords → material name
    "piso":          "Porcelanato 60x60cm",
    "floor":         "Porcelanato 60x60cm",
    "ceramica":      "Cerâmica 45x45cm",
    "cerâmica":      "Cerâmica 45x45cm",
    "revestimento":  "Reboco + Pintura",
    "parede":        "Reboco + Pintura",
    "wall":          "Reboco + Pintura",
    "teto":          "Gesso Acartonado",
    "ceiling":       "Gesso Acartonado",
    "cobertura":     "Telha Cerâmica",
    "roof":          "Telha Cerâmica",
    "asfalto":       "Pavimento Asfáltico",
    "concreto":      "Concreto C25",
    "grama":         "Grama Natural",
    "piscina":       "Cerâmica de Piscina",
    "deck":          "Deck de Madeira Cumaru",
}
mat_default = make_material("Reboco + Pintura")
mat_cache = {}

def get_or_create_mat(name):
    if name not in mat_cache:
        mat_cache[name] = make_material(name)
    return mat_cache[name]

fixed_cov = 0
for cov in model.by_type("IfcCovering"):
    if has_material(cov):
        continue
    obj_type = (cov.ObjectType or cov.Name or "").lower()
    chosen_mat_name = None
    for kw, mname in mat_map.items():
        if kw in obj_type:
            chosen_mat_name = mname
            break
    mat = get_or_create_mat(chosen_mat_name) if chosen_mat_name else mat_default
    assign_material(cov, mat)
    fixed_cov += 1
print(f"   Coverings corrigidos: {fixed_cov}")

# ─── C) IfcRoof sem contenção espacial ───────────────────────────────────────
print("C) Corrigindo IfcRoof sem contenção espacial...")

# Mapeia storeys por Z
storeys = model.by_type("IfcBuildingStorey")
def storey_z(s):
    try:
        return s.Elevation or 0.0
    except Exception:
        return 0.0

storey_list = sorted(storeys, key=storey_z)

def find_storey(z, storeys_sorted):
    """Retorna o storey cujo elevation é imediatamente abaixo de z."""
    best = storeys_sorted[0]
    for s in storeys_sorted:
        if storey_z(s) <= z + 0.05:
            best = s
    return best

# Coletar já contidos nos storeys
contained_in = {}
for rel in model.by_type("IfcRelContainedInSpatialStructure"):
    st = rel.RelatingStructure
    for el in (rel.RelatedElements or []):
        contained_in[el.id()] = (rel, st)

# Mapa storey → IfcRelContainedInSpatialStructure existente
storey_rel = {}
for rel in model.by_type("IfcRelContainedInSpatialStructure"):
    st = rel.RelatingStructure
    if st.is_a("IfcBuildingStorey"):
        storey_rel[st.id()] = rel

fixed_roof = 0
for roof in model.by_type("IfcRoof"):
    if roof.id() in contained_in:
        continue
    z = get_z(roof)
    if z is None:
        z = 0.0
    st = find_storey(z, storey_list)
    if st.id() in storey_rel:
        rel = storey_rel[st.id()]
        objs = list(rel.RelatedElements or [])
        objs.append(roof)
        rel.RelatedElements = objs
    else:
        new_rel = model.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=new_guid(),
            OwnerHistory=owner,
            RelatedElements=[roof],
            RelatingStructure=st,
        )
        storey_rel[st.id()] = new_rel
    fixed_roof += 1
print(f"   Roofs vinculados: {fixed_roof}")

# ─── Salva ────────────────────────────────────────────────────────────────────
print(f"Salvando → {DEST}")
model.write(DEST)
print("Feito.")
