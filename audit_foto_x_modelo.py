#!/usr/bin/env python3
"""
Auditoria de aderência do modelo IFC ao construído (foto real x modelo BIM).

Confronta as áreas documentadas no deck fotográfico
`referencias/Inhotim_Projeto_3D.pdf` com a geometria do modelo, reportando
coberturas e estrutura por edifício e sinalizando as divergências conhecidas
(cobertura do SPA, treliça da recepção, nomenclatura da cobertura do Bloco
Principal). Reprodutível sobre qualquer versão HVG_MASTER.

Uso:
    python3 audit_foto_x_modelo.py HVG_MASTER_v105_REALISTA.ifc
"""
import sys
from collections import Counter

import ifcopenshell
import ifcopenshell.util.element as ue


def building_of(elem):
    """Edifício que contém o elemento, subindo a estrutura espacial."""
    try:
        s = ue.get_container(elem)
        while s and not s.is_a("IfcBuilding"):
            s = s.Decomposes[0].RelatingObject if s.Decomposes else None
        return s.Name if s else "?"
    except Exception:
        return "?"


def main(path):
    f = ifcopenshell.open(path)
    print(f"== {path} | schema {f.schema} | {len(list(f))} entidades ==\n")

    # Integridade básica
    roots = f.by_type("IfcRoot")
    guids = [r.GlobalId for r in roots]
    print(f"IfcRoot: {len(roots)} | GUIDs únicos: {len(set(guids))} "
          f"| duplicados: {len(guids) - len(set(guids))}")
    print(f"Sistemas MEP: {len(f.by_type('IfcDistributionSystem'))} | "
          f"Materiais: {len(f.by_type('IfcMaterial'))}\n")

    # Coberturas e estrutura por edifício de interesse
    alvos = ["Bloco Principal", "Centro de Convenções", "Restaurante da Piscina",
             "SPA", "Boite Soul & Blues", "Clube NEP", "Guarita"]
    print("=== Coberturas e estrutura por edifício ===")
    for tgt in alvos:
        cols = sum(1 for x in f.by_type("IfcColumn") if building_of(x) == tgt)
        bms = sum(1 for x in f.by_type("IfcBeam") if building_of(x) == tgt)
        mem = sum(1 for x in f.by_type("IfcMember") if building_of(x) == tgt)
        roofs = [(r.PredefinedType, r.Name) for r in f.by_type("IfcRoof")
                 if building_of(r) == tgt]
        print(f"  [{tgt}] cols={cols} beams={bms} members={mem}")
        for pt, n in roofs:
            print(f"        cobertura: {pt} | {n}")

    # Busca por estruturas de cobertura aparentes (treliças/tesouras de madeira)
    import re
    hits = Counter()
    for e in f.by_type("IfcProduct"):
        n = (getattr(e, "Name", "") or "")
        if re.search(r"trelic|tesoura|madeira|espacial|truss", n, re.I):
            hits[e.is_a()] += 1
    print(f"\nElementos nomeados treliça/tesoura/madeira/space-frame: "
          f"{sum(hits.values())} {dict(hits)}")

    # Sinais das divergências conhecidas
    print("\n=== Checagem das divergências foto x modelo ===")
    spa_roofs = [r for r in f.by_type("IfcRoof") if building_of(r) == "SPA"]
    spa_flat = any(r.PredefinedType == "FLAT_ROOF" for r in spa_roofs)
    bp_mem = sum(1 for x in f.by_type("IfcMember") if building_of(x) == "Bloco Principal")
    bp_pir = any("Piramidal" in (r.Name or "")
                 for r in f.by_type("IfcRoof") if building_of(r) == "Bloco Principal")
    print(f"  [4.1] SPA com cobertura plana (real=tesouras de madeira): "
          f"{'DIVERGE' if spa_flat else 'ok'}")
    print(f"  [4.2] Recepção sem treliça (members no Bloco Principal={bp_mem}): "
          f"{'DIVERGE' if bp_mem == 0 else 'ok'}")
    print(f"  [4.3] Cobertura do Bloco Principal nomeada 'Piramidal' "
          f"(real=hip baixa+beirais): {'REVER' if bp_pir else 'ok'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "HVG_MASTER_v105_REALISTA.ifc")
