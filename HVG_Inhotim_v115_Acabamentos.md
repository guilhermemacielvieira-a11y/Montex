# HVG Inhotim — Revisão v115

## Clerestório, guarda-corpos envidraçados e mobiliário/louças do Bloco Principal

**Modelo base:** `HVG_MASTER_v114_FACHADAS.ifc` → **Entregue:** `HVG_MASTER_v115_ACABAMENTOS.ifc`
**Fonte:** `031 - Bloco Principal - Plantas.dwg` (camadas MOB / Loiças) · `032` (cortes/níveis)
**Autoria:** Guilherme Maciel — Grupo Montex Ltda · **Data:** 30/06/2026

---

## 1. O que foi modelado

| Item | Elemento IFC | Qtd | Observação |
|------|--------------|----:|-----------|
| **Clerestório** | `IfcPlate` (vidro) | 4 | Banda de vidro perimetral do topo do Térreo (3,55 m) até sob o beiral (3,95 m) |
| **Guarda-corpos envidraçados** | `IfcRailing` | 4 | Perímetro do Térreo, h=1,10 m, *Vidro Temperado* |
| **Mobiliário** | `IfcFurniture` | 420 | Blocos da camada `MOB` (cadeiras/bancos dos restaurantes do Subsolo) |
| **Louças sanitárias** | `IfcSanitaryTerminal` | 6 | Aparelhos da camada `Loiças` (WCs do Térreo), agrupados por proximidade |

Materiais novos: *Vidro Temperado Guarda‑Corpo*, *Mobiliario Generico*,
*Louca Ceramica Sanitaria*.

---

## 2. Notas técnicas

- **Clerestório:** a altura do modelo é comprimida (Térreo 0–3,55 m, beiral 3,7 m);
  a banda de clerestório (3,55–3,95 m) representa o vidro que, na obra, continua
  acima do forro até o beiral. Um realce maior exigiria reintroduzir o
  **pavimento superior** (níveis 5,00/8,40/9,90 do corte 032) — fora do escopo.
- **Louças:** a camada `Loiças` traz ~205 polilinhas que se concentram em **6
  pontos** (cada aparelho desenhado com vários traços); o agrupamento por
  proximidade reduziu a 6 `IfcSanitaryTerminal` reais. Há mais WCs cujas peças
  não constam dessa camada no DWG.
- **Mobiliário:** os 420 blocos `MOB` concentram‑se nos restaurantes do Subsolo
  (Restaurante Versátil / Buffet) — assentos em malha regular.

---

## 3. Validação (v115)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 525.563 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Geometria (louças/mob/clerestório/guarda-corpos) | válida (0 erros) |
| `IfcFurniture` / `IfcSanitaryTerminal` / `IfcRailing` / `IfcPlate` | 2.276 / 6 / 83 / 8 |
| Fachadas (v114) / portas / divisórias / calibração | preservadas |

> Previews: `referencias/v115_acabamentos/v115_clerestorio_guardacorpos_3d.png`
> e `v115_mobiliario_loucas.png`.

---

## 4. Evolução do Bloco Principal (LOD)

v110 calibração+IfcGrid → v111 ambientes → v112 divisórias → v113 portas →
v114 fachadas → **v115 clerestório + guarda‑corpos + mobiliário/louças**.

---

## 5. Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v115_ACABAMENTOS.ifc` | Modelo BIM v115 |
| `build_v115.py` | Construtor reprodutível (v114 → v115) |
| `HVG_Inhotim_v115_Acabamentos.md` | Este relatório |
| `referencias/v115_acabamentos/*.png` | Previews (3D + mobiliário/louças) |
