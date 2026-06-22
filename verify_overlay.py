"""Verificacao visual: underlays DXF (azul) x elementos v95 (vermelho) em coords locais do modelo."""
import ifcopenshell, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from collections import defaultdict

m = ifcopenshell.open("HVG_MASTER_v96_underlays.ifc")

def origin_xy(el):
    """origem mundial (XY) somando apenas translacoes da cadeia de placement."""
    x = y = 0.0
    p = el.ObjectPlacement
    while p:
        rp = p.RelativePlacement
        if rp and rp.is_a("IfcAxis2Placement3D"):
            c = rp.Location.Coordinates
            x += c[0]; y += c[1]
        p = p.PlacementRelTo
    return x, y

# annotation -> storey
ann_storey = {}
st_elems = defaultdict(list)
for rel in m.by_type("IfcRelContainedInSpatialStructure"):
    st = rel.RelatingStructure
    if not st.is_a("IfcBuildingStorey"):
        continue
    for el in rel.RelatedElements:
        if el.is_a("IfcAnnotation") and el.ObjectType == "MTX-UNDERLAY-DXF":
            ann_storey[el.id()] = st.Name
        elif el.ObjectPlacement:
            st_elems[st.Name].append(origin_xy(el))

anns = [a for a in m.by_type("IfcAnnotation") if a.ObjectType == "MTX-UNDERLAY-DXF"]
fig, axs = plt.subplots(3, 3, figsize=(18, 18))
for ax, a in zip(axs.flat, anns):
    ox, oy = origin_xy(a)
    sname = ann_storey.get(a.id())
    rep = a.Representation.Representations[0]
    pts = rep.Items[0].Points.CoordList  # lista compartilhada, lida uma vez
    segs = []
    for curve in rep.Items:
        for seg in curve.Segments:
            idx = seg[0]
            for k in range(len(idx) - 1):
                pa = pts[idx[k]-1]; pb = pts[idx[k+1]-1]
                segs.append([(ox + pa[0], oy + pa[1]), (ox + pb[0], oy + pb[1])])
    lc = LineCollection(segs, colors="#1f4e79", linewidths=0.2, zorder=1)
    ax.add_collection(lc)
    fp = np.array(st_elems.get(sname, []))
    if len(fp):
        fp = fp[(np.abs(fp[:, 0]) > 0.01) | (np.abs(fp[:, 1]) > 0.01)]
        if len(fp):
            ax.scatter(fp[:, 0], fp[:, 1], s=18, c="red", alpha=0.7,
                       label="elementos v95", zorder=3)
    label = a.Name.replace("Underlay DXF - ", "")
    ax.set_title(f"{label}  [{sname}]", fontsize=11)
    ax.autoscale(); ax.set_aspect("equal"); ax.grid(True, alpha=0.2)
    ax.legend(fontsize=7, loc="upper right")
plt.suptitle("Georreferencia dos underlays: DXF (azul) sobre elementos v95 (vermelho) — coords locais do modelo", fontsize=14)
plt.tight_layout()
plt.savefig("HVG_v96_Underlays_Overlay.png", dpi=80, bbox_inches="tight")
print("salvo HVG_v96_Underlays_Overlay.png")
