# HVG Inhotim — Revisão v121

## Portas dos demais edifícios por detecção de vãos

**Base:** `HVG_MASTER_v120_SPA_AMBIENTES.ifc` → **Entregue:** `HVG_MASTER_v121_PORTAS_GERAIS.ifc`
**Data:** 30/06/2026

Método universal (independe de anotação): agrupa as paredes‑divisória por reta,
ordena ao longo dela e detecta **lacunas de 0,65–1,15 m** (vãos de porta),
inserindo `IfcDoor` (folha simples, 2,10 m) em cada vão — em Convenções,
Restaurante, SPA, Clube NEP, Boite, Guarita, Apoio Quadras e apartamentos.

- **62 portas novas** inseridas, geometria 100 % válida (somam‑se às já
  existentes no modelo).

Validação: IFC4, GUIDs únicos, demais elementos preservados.

## Arquivos
`HVG_MASTER_v121_PORTAS_GERAIS.ifc` · `build_v121.py` · este relatório
