# HVG Inhotim — Revisão v124

## Bar da Piscina (Bar Molhado) — piscinas exteriores

**Base:** `HVG_MASTER_v123_APTOS_COBERTURA.ifc` → **Entregue:** `HVG_MASTER_v124_BAR_PISCINA.ifc`
**Fonte:** `14 - Piscinas exteriores.dwg` · **Data:** 30/06/2026

### Verificação das piscinas
O DWG das piscinas exteriores confirma que a **Piscina de Ondas** e as demais são
**retangulares** — forma já fielmente representada no modelo desde o v105, com:
lâmina d'água, borda, **raias** (3), skimmer e **deck** (`IfcCovering`/`IfcSlab`).
Também há a Piscina Infantil e 2 lagos ornamentais. **As piscinas já estavam
cobertas.**

### Adição
O elemento ausente destacado no DWG é o **"Bar Molhado / Bar da Piscina"**,
agora modelado junto à borda da Piscina de Ondas (cota do deck ≈ +3,20 m):
- **balcão em L** (`IfcFurniture`), 4 **banquetas** (`IfcFurniture`);
- **pérgola de sombra**: 4 pilares (`IfcColumn`) + cobertura plana (`IfcRoof`).

Validação: IFC4, GUIDs únicos, geometria válida, demais elementos preservados.
Preview: `referencias/v124_bar/v124_bar_piscina.png`.

## Arquivos
`HVG_MASTER_v124_BAR_PISCINA.ifc` · `build_v124.py` · este relatório · preview
