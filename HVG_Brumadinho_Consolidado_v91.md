# HVG Brumadinho — Modelo BIM Consolidado v91 (materiais + pranchas + 4D + 5D)

**Modelo consolidado entregue:** `HVG_MASTER_v91_consolidado.ifc` (IFC4, 20 MB)
**Base:** `HVG_MASTER_v90_LOD300.ifc`
**Data:** 21/06/2026 · Grupo Montex

Esta entrega consolida em **um único arquivo IFC** as três frentes solicitadas:
(1) materiais completados + 5D recalculado, (2) pranchas cotadas a partir do
`IfcGrid` e (3) planejamento 4D (cronograma vinculado aos elementos).

---

## 1. Materiais completos + 5D recalculado

- **187 lajes de pavimentação** e **9 muros de arrimo** que estavam **sem
  `IfcMaterial`** foram associados (asfalto/concreto/termoplástico/terra),
  conforme o `ObjectType`. **Pendências de material: 0.**
- A pavimentação de site agora é **100 % atribuível por material** (concreto C25
  23.349 m², univerde 2.175 m², asfalto, grama, saibro, poliuretano…), permitindo
  custeio por composição.

### Takeoff 5D (resumo) — `HVG_v91_Takeoff_Mestre.csv`
| Disciplina | Item | Qtd | Un |
|---|---|---|---|
| Estrutura | Pilares / Vigas | 207 / 819 | m³ |
| Estrutura | Lajes (volume / área piso) | 18.132 / 26.437 | m³ / m² |
| Arquitetura | Paredes / Esquadrias / Portas | 25.974 m² / 3.028 m² / 223 un |
| Cobertura | Telhado | 15.694 | m² |
| Acabamento | Revestimentos | 21.704 | m² |
| Urbanismo | Pavimentação | 30.610 | m² |
| MEP | Tubulação / Dutos / Eletrocalhas | 4.200 / 1.120 / 1.142 | m |

**Orçamento indicativo (escopo modelado):** ≈ **R$ 30,6 milhões** (~R$ 970/m²),
com preços de **referência** a substituir por composição própria — ver
`HVG_v91_Orcamento_Indicativo.csv` e ressalvas no relatório 5D.

---

## 2. Pranchas cotadas a partir do `IfcGrid`

- Criado/consolidado o **`IfcGrid` "BP-EIXOS"** (17 eixos U: A…Q × 17 eixos V: 1…17,
  malha **4,97 m**) a partir das posições reais dos pilares do Bloco Principal.
- Gerada a **prancha cotada** `HVG_Prancha_BP_Planta_Eixos.pdf` (e `.png`):
  planta de eixos e pilares com rótulos de eixos nos 4 lados, **cotas parciais
  (4,97 m) e total (79,50 m)** em X e Y, perímetro de paredes e os 289 pilares.

---

## 3. Planejamento 4D (cronograma vinculado ao modelo)

Embutido no IFC: **`IfcWorkPlan` + `IfcWorkSchedule`** com **8 `IfcTask`** (fases),
cada uma com `IfcTaskTime` (início/fim/duração ISO‑8601) e **elementos vinculados
via `IfcRelAssignsToProcess`** (4D real, navegável em visualizadores BIM).

| Fase | Início | Fim | Elem. |
|------|--------|-----|-------|
| T01 Terraplenagem e Fundações | 09/2026 | 01/2027 | 9 |
| T02 Estrutura | 11/2026 | 08/2027 | 1.448 |
| T03 Vedações | 03/2027 | 12/2027 | 583 |
| T04 Cobertura | 06/2027 | 01/2028 | 31 |
| T05 Esquadrias | 09/2027 | 03/2028 | 765 |
| T06 Instalações MEP | 07/2027 | 05/2028 | 885 |
| T07 Acabamentos | 11/2027 | 08/2028 | 447 |
| T08 Urbanismo e Paisagismo | 03/2028 | 10/2028 | 2.399 |

Prazo total ≈ **26 meses** (set/2026 → out/2028). Gantt:
`HVG_Cronograma_4D_Gantt.pdf`; tabela: `HVG_v91_Cronograma_4D.csv`.

---

## 4. Validação do IFC consolidado (v91)
| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| GUIDs únicos | Sim |
| Lajes/paredes sem material | **0** |
| `IfcGrid` | 1 (17×17) |
| `IfcWorkSchedule` / `IfcTask` / vínculos | 1 / 8 / 8 `IfcRelAssignsToProcess` |
| Entidades | 326.272 |

---

## 5. Arquivos entregues
| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v91_consolidado.ifc`** | **Modelo BIM consolidado (materiais + IfcGrid + 4D)** |
| `HVG_Prancha_BP_Planta_Eixos.pdf` / `.png` | Prancha cotada de eixos/pilares |
| `HVG_Cronograma_4D_Gantt.pdf` / `.png` | Gantt do cronograma 4D |
| `HVG_v91_Takeoff_Mestre.csv` | Quantitativos 5D |
| `HVG_v91_Quantitativos_por_Material.csv` | Quantitativos por material |
| `HVG_v91_Orcamento_Indicativo.csv` | Orçamento indicativo |
| `HVG_v91_Cronograma_4D.csv` | Tabela do cronograma |
| `consolidate_v91.py`, `make_plans.py`, `make_gantt_5d.py` | Scripts reproduzíveis |
