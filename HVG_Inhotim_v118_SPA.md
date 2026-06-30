# HVG Inhotim — Revisão v118

## Divisórias internas do SPA (DWG oficial 13 - Bloco Spa)

**Modelo base:** `HVG_MASTER_v117_APARTAMENTOS.ifc` → **Entregue:** `HVG_MASTER_v118_SPA.ifc`
**Fonte:** `13 - Bloco Spa.dwg` (via LibreDWG) · **Data:** 30/06/2026

---

## 1. O que foi modelado

Extração das linhas de parede (camadas `ALVENARIA` / `PAR1` / `PAR` /
`SPA_ALVENARIA`) do plano do SPA, mapeadas ao footprint do edifício no modelo
(X 67,7–92,3 · Y 263,1–276,9, SPA‑Terreo): **173 `IfcWall` (PARTITIONING)**.

Layout fiel ao programa: **metade aberta** (salão da piscina interior aquecida
+ deck) e **cluster de tratamento** (salas de massagem, saunas/termas, salas de
tratamento, vestiários, recepção) — preview `referencias/v118_spa/v118_spa_divisorias.png`.

O DWG traz 18 ambientes com área (Σ 328 m²), úteis para um próximo passo de
programa de espaços (`IfcSpace`).

---

## 2. Validação

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 571.427 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Divisórias do SPA | **173**, geometria 173/173 válida |
| Demais edifícios | preservados |

---

## 3. Estado do detalhamento (divisórias) — todos os edifícios principais

| Edifício | Divisórias |
|----------|-----------|
| Bloco Principal | ✅ (v112, + portas/fachadas/acabamentos v113–v115) |
| Centro de Convenções | ✅ (v116) |
| Restaurante da Piscina | ✅ (v116) |
| Apartamentos A/B (16 blocos) | ✅ (v117) |
| **SPA** | ✅ **(v118)** |

**Edifícios menores ainda sem detalhe** (DWG já recebidos): Boite, Clube NEP,
Guarita, Apoio Quadras, Subestação, Copa de Apoio, Piscinas exteriores.

## 4. Arquivos
`HVG_MASTER_v118_SPA.ifc` · `build_v118.py` · `HVG_Inhotim_v118_SPA.md` ·
`referencias/v118_spa/v118_spa_divisorias.png`
