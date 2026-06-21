# HVG Brumadinho — Quantitativos e Orçamento Indicativo (5D) · modelo v90

**Modelo:** `HVG_MASTER_v90_LOD300.ifc` (IFC4)
**Data:** 21/06/2026 · Grupo Montex
**Método:** extração de `BaseQuantities` do IFC (volumes/áreas/contagens) +
cálculo geométrico para comprimentos MEP e área de telhado.

---

## 1. Takeoff mestre (quantitativos por disciplina)

| Disciplina | Serviço | Qtd | Un | Nº elem. |
|------------|---------|-----|----|----------|
| Estrutura | Pilares (concreto/aço) | **207,3** | m³ | 893 |
| Estrutura | Vigas (concreto/aço) | **818,9** | m³ | 492 |
| Estrutura | Lajes — volume | 18.132 | m³ | 375 |
| Estrutura | Lajes de piso — área | **26.437** | m² | 63 |
| Arquitetura | Paredes — área | **25.974** | m² | 592 |
| Arquitetura | Paredes — volume | 2.179 | m³ | 592 |
| Arquitetura | Esquadrias / Janelas | **3.028** | m² | 542 |
| Arquitetura | Portas | **223** | un | 223 |
| Cobertura | Telhado — superfície | **15.694** | m² | 31 |
| Acabamento | Revestimentos / Coberturas | 21.704 | m² | 447 |
| Urbanismo | Pavimentação externa / site | 30.610 | m² | 312 |
| MEP | Tubulação (hidráulica/incêndio) | **4.200** | m | 326 |
| MEP | Dutos AVAC | 1.120 | m | 48 |
| MEP | Eletrocalhas/bandejas | 1.142 | m | 50 |

Detalhamento por **material** em `HVG_v90_Quantitativos_por_Material.csv`;
takeoff mestre em `HVG_v90_Takeoff_Mestre.csv`.

## 2. Área construída (útil) por grupo

| Grupo | Área útil (m²) |
|-------|----------------|
| Edifícios comuns (BP, CC, Boîte, Rest. Piscina, SPA, NEP, Guarita) | 12.026 |
| Blocos de Apartamentos A (12) | 9.954 |
| Blocos de Apartamentos B (4) | 5.321 |
| Novos utilitários (Subestação, Gás, Apoio Quadras) | 249 |
| Espaços externos (estac./quadras/pista) | 4.035 |
| **TOTAL útil** | **31.584 m²** |

## 3. Orçamento indicativo (5D) — **preços de REFERÊNCIA**

> ⚠️ **Importante:** os valores unitários abaixo são **referências de ordem de
> grandeza** (R$, base 2026) e devem ser **substituídos pelas composições próprias
> (SINAPI/SICRO/cotação)**. O total cobre apenas o **escopo modelado**
> (estrutura, vedações, cobertura, esquadrias, revestimentos, pavimentação e MEP
> básico) — **não inclui** fundações, instalações completas e equipamentos MEP,
> acabamentos finos, paisagismo detalhado, piscinas/lagos (estrutura hidráulica),
> mobiliário, BDI e impostos.

| Serviço | Qtd | Un | R$/un (ref.) | Subtotal (R$) |
|---------|-----|----|-----|--------------|
| Pilares (concreto/aço) | 207 | m³ | 2.600 | 538.963 |
| Vigas (concreto/aço) | 819 | m³ | 2.600 | 2.129.071 |
| Lajes (Steel Deck/concreto) | 26.437 | m² | 310 | 8.195.354 |
| Paredes (alvenaria/drywall) | 25.974 | m² | 190 | 4.935.111 |
| Esquadrias/Janelas | 3.028 | m² | 950 | 2.876.220 |
| Portas | 223 | un | 1.300 | 289.900 |
| Telhado (telha+estrutura) | 15.694 | m² | 240 | 3.766.560 |
| Revestimentos/Coberturas | 21.704 | m² | 160 | 3.472.566 |
| Pavimentação externa | 30.610 | m² | 120 | 3.673.247 |
| Tubulação | 4.200 | m | 85 | 357.009 |
| Dutos AVAC | 1.120 | m | 230 | 257.669 |
| Eletrocalhas | 1.142 | m | 130 | 148.499 |
| **TOTAL INDICATIVO (escopo modelado)** | | | | **≈ R$ 30,6 milhões** |

Custo indicativo do escopo modelado: **≈ R$ 970/m²** construído. Por ser apenas o
escopo modelado (sem fundações, instalações completas, acabamentos finos e BDI),
este valor é, como esperado, inferior ao custo turnkey de um resort
(tipicamente R$ 4.000–7.000/m²). Planilha: `HVG_v90_Orcamento_Indicativo.csv`.

## 4. Observações de qualidade de dados (para refinar o 5D)
- **187 lajes de pavimentação de site sem material** no modelo (≈ 30 mil m²) —
  recomenda‑se completar o `IfcMaterial` para custear corretamente a pavimentação.
- As **lajes de piso (Steel Deck)** dominam o item de maior custo — vale validar
  espessuras/composição para o orçamento executivo.

## 5. Arquivos entregues
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_v90_Takeoff_Mestre.csv` | Quantitativos por disciplina |
| `HVG_v90_Quantitativos_por_Material.csv` | Quantitativos por categoria × material |
| `HVG_v90_Orcamento_Indicativo.csv` | Orçamento indicativo (preços de referência) |
| `HVG_Brumadinho_Quantitativos_5D_v90.md` | Este relatório |
| `takeoff_5d.py`, `takeoff_geom.py`, `takeoff_final.py` | Scripts reproduzíveis |
