# HVG Inhotim — Revisão v123

## Nível de cobertura dos apartamentos (terraços / platibandas)

**Base:** `HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc` → **Entregue:** `HVG_MASTER_v123_APTOS_COBERTURA.ifc`
**Fontes:** `07/08 - Blocos Aptos A/B.dwg` (PLANTA da COBERTURA) · **Data:** 30/06/2026

A laje de cobertura já existia (`IfcRoof` por bloco). Esta revisão acrescenta o
**nível de cobertura** (terraços acessíveis com platibandas/muretas), lido da
"PLANTA da COBERTURA" de cada DWG:

1. Cria um **`IfcBuildingStorey` "Cobertura"** em cada um dos 16 blocos, agregado
   ao edifício, na cota real (**Bloco A: +2,80 m** · **Bloco B: +5,60 m**).
2. Mapeia as muretas/platibandas (camada `Par1` do quadrante de cobertura) como
   **`IfcWall` PARAPET** de 1,0 m, material *Concreto Platibanda Cobertura*.

**3.120 platibandas** (≈171/bloco A · 267/bloco B). Validação: IFC4, GUIDs únicos,
16 storeys novos, cotas corretas (A +2,80 / B +5,60), empilhamento coerente
(subsolo→térreo→pav1→cobertura) — preview `referencias/v123_cobertura/v123_bloco_b13_cobertura.png`.

Com isto, os **16 blocos de apartamentos estão completos** em todos os pavimentos
(subsolos, térreo, 1º pav nos B, e cobertura) com divisórias, portas e platibandas.

## Arquivos
`HVG_MASTER_v123_APTOS_COBERTURA.ifc` · `build_v123.py` · este relatório · preview
