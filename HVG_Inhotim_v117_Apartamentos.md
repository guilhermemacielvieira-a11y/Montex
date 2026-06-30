# HVG Inhotim — Revisão v117

## Divisórias dos blocos de apartamentos A e B (DWG oficiais 07/08)

**Modelo base:** `HVG_MASTER_v116_OUTROS_EDIF.ifc` → **Entregue:** `HVG_MASTER_v117_APARTAMENTOS.ifc`
**Fontes:** `07 - Bloco 18 Aptos A.dwg` · `08 - Bloco 24 Aptos B.dwg` (via LibreDWG)
**Autoria:** Guilherme Maciel — Grupo Montex Ltda · **Data:** 30/06/2026

---

## 1. Método

1. Em cada DWG, **localiza o plano do Térreo** pelo rótulo "PLANTA TÉRREO" e
   isola as linhas da camada de parede **`Par1`** desse plano.
2. **Mapeia a planta-tipo** ao footprint de cada bloco do modelo
   (de-rotação + ajuste de eixos + escala), via `detail_lib`.
3. **Replica** o layout: tipo A → 12 blocos A; tipo B → 4 blocos B.

Os apartamentos são **compactos** (estúdios ~19–33 m²: quarto/estar + I.S. +
varanda — Quadro Sinóptico), logo **poucas paredes internas por unidade**
(predominam as paredes que separam unidades e fecham varandas/I.S.).

---

## 2. O que foi modelado (v117)

| Tipo | Blocos | Planta-tipo (segmentos Par1) | Divisórias/bloco | Total |
|------|:------:|:----------------------------:|:----------------:|:-----:|
| **A** (18 aptos) | 12 (A‑01…A‑12) | 248 | ~174 | — |
| **B** (24 aptos) | 4 (B‑13…B‑16) | 137 | ~63 | — |
| **Total** | **16** | | | **2.340 `IfcWall`** |

Replicação **consistente** (A‑01 ≡ A‑05; B‑13 ≡ B‑15) — preview
`referencias/v117_apartamentos/v117_apartamentos_blocos.png`: blocos A com
unidades em duas fileiras ao longo de corredores; blocos B com unidades em
torno do núcleo central de circulação.

---

## 3. Validação (v117)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 568.830 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Divisórias de apartamentos | **2.340**, geometria 2.340/2.340 válida |
| `IfcWall` (total no modelo) | 5.106 |
| Bloco Principal / Convenções / Restaurante | preservados |

---

## 4. Estado geral do detalhamento por edifício

| Edifício | Detalhamento |
|----------|--------------|
| **Bloco Principal** | ✅ Completo (calibração+grid, ambientes, divisórias, portas, fachadas, clerestório, guarda-corpos, mobiliário, louças) — v110–v115 |
| **Centro de Convenções** | ✅ Divisórias (v116) |
| **Restaurante da Piscina** | ✅ Divisórias (v116) |
| **Blocos de Apartamentos A/B** | ✅ Divisórias do Térreo (v117) |
| **SPA** | ⏳ pendente de DWG |

**Refinamentos pendentes (todos os edifícios):** programa de ambientes
(`IfcSpace`), portas/esquadrias, fachadas e mobiliário — extraíveis das mesmas
plantas; e demais pavimentos dos apartamentos (subsolos/cobertura).

---

## 5. Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v117_APARTAMENTOS.ifc` | Modelo BIM v117 |
| `build_v117.py` · `detail_lib.py` | Construtor + biblioteca |
| `HVG_Inhotim_v117_Apartamentos.md` | Este relatório |
| `referencias/v117_apartamentos/v117_apartamentos_blocos.png` | Preview (4 blocos) |
