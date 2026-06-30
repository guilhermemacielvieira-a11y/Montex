# HVG Inhotim — Revisão v120

## Programa de ambientes do SPA (IfcSpace, da planta oficial)

**Base:** `HVG_MASTER_v119_MENORES.ifc` → **Entregue:** `HVG_MASTER_v120_SPA_AMBIENTES.ifc`
**Fonte:** `13 - Bloco Spa.dwg` (escala 1/100) · **Data:** 30/06/2026

Substitui os espaços genéricos do SPA por **15 `IfcSpace` reais**, com nome e
**área** (`Qto_SpaceBaseQuantities`), pareando rótulos de nome e área da planta e
posicionando com o mesmo transform das divisórias (v118):

PISCINA 75,65 · GINÁSIO 41,6 · RECEÇÃO DO SPA 27,5 · MASSAGENS (4 salas) ·
TURCO · ROUPARIA · MÉDICO · Vichy · I.S. Deficientes · SENHORAS · HOMENS ·
Área Técnica.

Validação: IFC4, GUIDs únicos, áreas em Qto. Demais edifícios preservados.

## Arquivos
`HVG_MASTER_v120_SPA_AMBIENTES.ifc` · `build_v120.py` · este relatório
