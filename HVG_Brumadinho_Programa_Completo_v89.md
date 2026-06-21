# HVG Brumadinho — Modelagem das Lacunas do Quadro Sinóptico + Correção do SPA

**Modelo de entrada:** `HVG_MASTER_v88_render_corrigido.ifc`
**Modelo entregue:** `HVG_MASTER_v89_programa_completo.ifc` (IFC4, 20,2 MB)
**Referência:** Planta de Situação — Quadro Sinóptico (01__Planta_Situacao.pdf)
**Data:** 21/06/2026 · Grupo Montex

---

## 1. Objetivo
Preencher as lacunas identificadas na comparação IFC × Planta de Situação e corrigir a
área subdimensionada do SPA, modelando como projetista BIM sênior — elementos
georreferenciados (SIRGAS 2000 / UTM 23S), assentados na topografia real (TIN),
com material, cor, quantitativos (`BaseQuantities`) e `Pset` próprios, sem conflitos.

## 2. Elementos criados (assentados na cota do terreno amostrada no TIN)

### 2.1 Estacionamentos — **170 vagas** (168 ligeiros + 2 ônibus)
3 lotes (Norte, Central, Sul) com pavimento **Univerde permeável** + lote de ônibus
asfáltico, cada um com `IfcSpace` (`Pset_HVG_Ambiente.NumeroVagas`) e marcação de
vagas. Área ≈ **2.287 m²** (PDF 2.175 m²). Locados na faixa sul livre (Y≈45).

### 2.2 Área Desportiva — ≈ **1.064 m²** (+ Apoio 94,8 = 1.159 ≈ PDF 1.168)
- Quadra Polidesportiva 32×19 (piso poliuretano azul)
- Quadra de Padel 20×10 (grama sintética)
- 2 × Beach Tennis 16×8 (saibro)
Cada quadra com `IfcSlab` (superfície colorida) + `IfcSpace`. Sudeste livre (Y≈35–72).

### 2.3 Pista de Carros infantil — **684 m²** (PDF 678,37)
`IfcSlab` asfáltico 38×18 + `IfcSpace` recreativo, borda leste livre (390, 230).

### 2.4 Novos edifícios (`IfcBuilding` + pavimento + laje + paredes + cobertura + `IfcSpace`)
| Edifício | Área | PDF |
|----------|------|-----|
| **Subestação** de energia | 144 m² | 144,47 m² |
| **Central de Gás** (GLP) | 30 m² | — |
| **Apoio às Quadras** (vestiários/bar) | 94,8 m² | 94,80 m² |

### 2.5 SPA — ampliação (anexo)
O SPA tinha envelope ~350 m² com apenas **294 m² úteis** (49 % da PDF). Foi adicionado
um **anexo** (laje + paredes + cobertura cerâmica) com 4 ambientes — *Saunas e Termas,
Salas de Tratamento, Deck Piscina Interior, Circulação/Apoio* — elevando a área útil
para **560 m²** (≈ 598 m² de área coberta da PDF, considerando paredes). Encostado ao
SPA existente (+X), sem sobrepor ambientes.

## 3. Validação
| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| GUIDs únicos | Sim (31.105) |
| `IfcBuilding` | **26** (23 + 3 novos) |
| Novos elementos malhados | 123, **0 fora de escala** |
| Clashes novos edifícios × existentes | **0** |
| Contenção espacial / material / quantitativos | completos em todos os novos elementos |

## 4. Reconciliação final IFC × PDF
| Programa | IFC v89 | PDF |
|----------|---------|-----|
| Edifícios | 26 | 26 |
| Apartamentos | 312 | 312 |
| Estacionamento (vagas) | 170 | 170 |
| Área desportiva + apoio | 1.159 m² | 1.168 m² |
| Pista de carros | 684 m² | 678 m² |
| Subestação | 144 m² | 144,47 m² |
| SPA (útil) | 560 m² | 598 m² (coberta) |

Todas as lacunas do Quadro Sinóptico foram modeladas; as pequenas diferenças de área
decorrem de *área útil (IFC)* vs *área coberta (PDF)*, dentro do esperado.

## 5. Arquivos
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v89_programa_completo.ifc` | Modelo com o programa completo + SPA corrigido |
| `HVG_Brumadinho_Programa_Completo_v89.md` | Este relatório |
| `model_gaps.py` | Script de modelagem (reproduzível) |
