# HVG Inhotim — Revisão v122

## Demais pavimentos dos apartamentos (subsolos / 1º pavimento)

**Base:** `HVG_MASTER_v121_PORTAS_GERAIS.ifc` → **Entregue:** `HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc`
**Fontes:** `07 - Bloco 18 Aptos A.dwg` · `08 - Bloco 24 Aptos B.dwg` · **Data:** 30/06/2026

Completa os apartamentos (o Térreo foi feito na v117): extrai **por quadrante** as
plantas Par1 de cada pavimento e replica nos 16 blocos, **nas cotas reais** de
cada storey (via `Elevation`):

| Tipo | Pavimentos adicionados | Cotas |
|------|------------------------|-------|
| Bloco A (×12) | 1º Sub-solo, 2º Sub-solo | −2,80 m · −5,60 m |
| Bloco B (×4) | Sub-solo, 1º Pavimento | −2,80 m · +2,80 m |

**1.856 `IfcWall`** novas. Validação: IFC4, GUIDs únicos, pavimentos empilhados
nas elevações corretas (preview `referencias/v122_aptos/v122_bloco_b13_pavimentos.png`).

## Arquivos
`HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc` · `build_v122.py` · este relatório
