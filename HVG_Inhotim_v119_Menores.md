# HVG Inhotim — Revisão v119

## Divisórias dos edifícios menores (Boite, Clube NEP, Guarita, Apoio Quadras, Subestação)

**Modelo base:** `HVG_MASTER_v118_SPA.ifc` → **Entregue:** `HVG_MASTER_v119_MENORES.ifc`
**Fontes (DWG):** 041 Boite · 09 Clube NEP · 02 Guarita · 10 Apoio Quadras · 12 Subestação
**Data:** 30/06/2026

Pipeline `detail_lib` + filtro do cluster mais denso (estes DWG têm vários
planos/detalhes): extrai paredes, de-rotaciona e mapeia ao footprint de cada
edifício no modelo.

| Edifício | Footprint (modelo) | Divisórias |
|----------|--------------------|:----------:|
| Boite Soul & Blues | BOITE-Terreo | **44** |
| Clube NEP | NEP-Terreo | **248** |
| Guarita | H1-Terreo | **6** |
| Apoio Quadras | APQ-Terreo | **82** |
| Subestação | SUB-Terreo | **82** |
| **Total** | | **462** |

Validação: IFC4 válido, GUIDs únicos, geometria válida, demais edifícios preservados.
Preview: `referencias/v119_menores/v119_menores_divisorias.png`.

**Pendentes:** Copa de Apoio e Piscinas exteriores (sem edifício‑alvo claro no
modelo — a Copa é apoio dos blocos; piscinas são elementos de implantação).

## Arquivos
`HVG_MASTER_v119_MENORES.ifc` · `build_v119.py` · `HVG_Inhotim_v119_Menores.md` · preview
