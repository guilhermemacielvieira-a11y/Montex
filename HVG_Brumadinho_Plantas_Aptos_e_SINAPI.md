# HVG Brumadinho — Pranchas dos Blocos de Apartamentos + Orçamento por Composição (SINAPI)

**Modelo:** `HVG_MASTER_v91_consolidado.ifc` · **Data:** 21/06/2026 · Grupo Montex

---

## 1. Pranchas cotadas — Blocos de Apartamentos A e B

Geradas plantas‑tipo cotadas a partir da geometria e dos pilares (eixos derivados):

### Bloco A (tipo) — `HVG_Prancha_BlocoA_Planta_Tipo.pdf`
- 6 apartamentos/pavimento (Apto 27–41 m², Varanda 5 m², I.S. 4 m², Hall 5 m²)
- Malha de pilares **A–G × 1–4**, vãos 4,30 / 4,20 / 3,90 m, **largura total 25,00 m**
- 28 pilares, 24 ambientes, ambientes coloridos e rotulados com área

### Bloco B (tipo) — `HVG_Prancha_BlocoB_Planta_Tipo.pdf`
- Pavimento térreo com 12 apartamentos (48 ambientes)
- Mesma malha de eixos e cotas parciais/total

> Confere com o projeto básico (módulo ~25,34 m, tipologias de 19–33 m²).

---

## 2. Orçamento por composição (estilo SINAPI) — quantidades do modelo

Refinamento do 5D decompondo os serviços em **insumos com coeficientes** (códigos de
referência ilustrativos; **substituir pela composição/cotação vigente**).

| Serviço | Subtotal (R$) |
|---------|---------------|
| Estrutura de concreto armado (1.026 m³ → concreto + fôrma + armadura) | 2.828.116 |
| Lajes de piso (26.437 m²) | 7.930.980 |
| Alvenaria + revestimento (25.974 m² → bloco + reboco + pintura) | 5.402.648 |
| Esquadrias alumínio+vidro (3.028 m²) | 2.876.220 |
| Portas internas (223 un) | 289.900 |
| Cobertura e revestimentos (21.704 m²) | 3.581.083 |
| Instalação hidrossanitária/incêndio (4.200 m) | 399.010 |
| Instalação AVAC (1.120 m) | 268.872 |
| Instalação elétrica (1.142 m) | 171.345 |
| Pavimentação externa/urbanismo (30.610 m²) | 4.132.404 |
| **Custo direto (escopo modelado)** | **27.880.578** |
| + Fundações (estim. 8 %) | 2.230.446 |
| + Complementação de instalações (10 %) | 2.788.058 |
| + Canteiro/administração local (3 %) | 836.417 |
| + **BDI (25 %)** | 8.433.875 |
| **TOTAL GERAL ESTIMADO (referência)** | **≈ R$ 42,2 milhões** |

**Custo estimado: ≈ R$ 1.335/m²** (área útil 31.585 m²).

> **Ressalvas:** valores de **referência** (base 2026). O índice reflete obra de
> shell + sistemas básicos com acabamento padrão; **acabamentos premium de resort,
> equipamentos de MEP, paisagismo detalhado e estrutura das piscinas/lagos** elevam
> o custo (resorts de alto padrão: R$ 3.000–6.000/m²). Recomenda‑se substituir as
> composições pelas do orçamento executivo (SINAPI/SICRO/cotação) e detalhar os
> itens hoje cobertos por *allowance*. Planilha: `HVG_v91_Orcamento_SINAPI_Composicao.csv`.

---

## 3. Arquivos entregues
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_Prancha_BlocoA_Planta_Tipo.pdf` / `.png` | Planta‑tipo cotada Bloco A |
| `HVG_Prancha_BlocoB_Planta_Tipo.pdf` / `.png` | Planta‑tipo cotada Bloco B |
| `HVG_v91_Orcamento_SINAPI_Composicao.csv` | Orçamento por composição |
| `make_plans_aptos.py`, `sinapi_budget.py` | Scripts reproduzíveis |
