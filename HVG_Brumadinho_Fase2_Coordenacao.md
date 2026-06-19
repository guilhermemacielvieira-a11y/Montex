# HVG Brumadinho — Vila Galé Collection
## Fase 2 — Compatibilização Executiva e Coordenação Multidisciplinar

**Modelo de entrada:** `HVG_MASTER_v87_Arq_MEP_coordenado.ifc` (Fase 1)
**Modelo entregue:** `HVG_MASTER_v88_Arq_MEP_executivo.ifc` (IFC4)
**Data:** 19/06/2026 · **Autoria:** Grupo Montex Ltda

---

## 1. Objetivo da fase

Dar sequência ao roteiro de coordenação definido na Fase 1, elevando o modelo de
"compatibilizado" (sem interferências terminais×pilares) para **executivo**:
detecção de interferências **multidisciplinar completa**, saneamento de dados e
modelagem da **furação** (passagens de prumadas), preparando o modelo para projeto
executivo e quantitativos.

---

## 2. Detecção de interferências multidisciplinar (clash detection)

Foi implementada detecção geométrica em **fase ampla + fase estreita**:

- **Fase ampla:** caixas envolventes (AABB) no espaço‑mundo de **3.142 elementos**
  (834 MEP + 2.351 estruturais), via motor de geometria IfcOpenShell, com indexação
  espacial (hash 3 m) para broad‑phase.
- **Fase estreita:** confirmação de **interpenetração real** (ambos os sólidos com
  vértices dentro da caixa de sobreposição), eliminando os falsos‑positivos típicos
  de AABB de elementos lineares longos (tubos/dutos).
- **Escopo:** MEP × Estrutura (pilar, viga, laje, parede, cobertura, escada) e
  MEP × MEP (sistemas distintos), tolerância mínima de penetração 1 cm.

### Resultado
| Etapa | Interferências reais |
|-------|----------------------|
| Varredura inicial (sobre v87) | **3** |
| Após resolução desta fase | **1** (não‑conflito, ver §3) |

A baixíssima contagem confirma a qualidade do modelo após a Fase 1: não há colisões
MEP×MEP nem MEP×viga/parede/pilar. Relatórios: `HVG_v88_Clash_Report_Final.csv`,
`clash_full_report_v88.json`.

---

## 3. Interferências tratadas

| ID | Conflito | Penetração | Tratamento |
|----|----------|-----------|------------|
| CL2‑a | Eletrocalha `Bloco‑A‑11‑L2‑CT` × **Guia/meio‑fio** da estrada interna | 6,1 cm | Eletrocalha afastada +0,32 m em Y (folga 7,5 cm) |
| CL2‑b | Eletrocalha `Bloco‑A‑11‑L2‑CT` × **Pavimento** da estrada interna | 3,9 cm | Mesmo deslocamento (folga 22,5 cm) |
| CL2‑c | `SPDA‑CAPT‑BOITE` (captor Franklin) × **Cobertura piramidal** da Boîte | 5,0 cm | **Não‑conflito**: por NBR 5419 o captor é fixado na cumeeira e atravessa a telha por projeto. Mantido. |

> Diretriz adotada (igual à Fase 1): conflitos são resolvidos pelo **lado MEP**,
> preservando arquitetura/estrutura.

---

## 4. Saneamento de materiais (biblioteca única)

Consolidados **5 grupos** de `IfcMaterial` duplicados/quase‑duplicados, com remapeamento
de todas as referências para a instância canônica e remoção das cópias
(**39 → 34 materiais**):

| Mantido (canônico) | Removido |
|--------------------|----------|
| Concreto Armado C25 | Concreto Armado C25 (cópia) |
| Vidro Laminado 8mm | Vidro Laminado 8mm (cópia) |
| Concreto armado 30 MPa (escada) | (cópia) |
| Aço Estrutural ASTM A500 Gr.B | Aco Estrutural ASTM A500 Gr.B (sem acento) |
| Telha Cerâmica Vila Galé | Telha Ceramica Vila Gale (sem acento) |

---

## 5. Eixos estruturais (IfcGrid)

Criado **1 `IfcGrid`** ("BP‑EIXOS") a partir das posições reais dos pilares do Bloco
Principal: **17 eixos U (A…)** × **17 eixos V (1…)**, malha ~4,97 m, com geometria de
eixo (`IfcGridAxis`/`IfcPolyline`) e contido no pavimento BP‑Terreo. Facilita locação,
conferência e leitura de plantas em Archicad/Revit.

---

## 6. Furação — passagens de prumadas (IfcOpeningElement)

Análise dedicada de **penetrações verticais de MEP em lajes de piso estruturais**
(distinguindo‑as de tubulações enterradas que cruzam plataformas/estradas/gramados,
que **não** geram furo). Resultado:

- **593** penetrações brutas MEP×laje → filtradas para **329** prumadas reais
  (água fria/quente, esgoto, drenos) atravessando **lajes Steel Deck MF‑75** dos
  Blocos de Apartamentos.
- Para cada uma foi modelado um **`IfcOpeningElement` (PredefinedType OPENING)** com
  `IfcRelVoidsElement` vazando a laje hospedeira; *sleeve* dimensionado como
  Ø do tubo + 0,10 m de folga; vão estendido pela espessura da laje + 0,10 m.
- Placement relativo à laje hospedeira via transformação inversa — correto inclusive
  para as 30 lajes com rotação não‑identidade.

**Verificação geométrica:** confirmada a subtração booleana — ex.: laje
`Laje-SteelDeck-MF75` (11 furos) reduziu volume de 83,083 → 83,051 m³ e passou de
8 para 48 vértices (furos presentes). Registro: `HVG_v88_Registro_Furacao.csv`.

---

## 7. Validação final (v88)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido (recarga IfcOpenShell OK) |
| Entidades | 326.190 |
| GlobalIds únicos | **Sim** (31.688) |
| Interferências reais (MEP×Estrutura / MEP×MEP) | **0** (1 não‑conflito SPDA documentado) |
| `IfcOpeningElement` / `IfcRelVoidsElement` | 329 / 329 (booleano aplicado ✔) |
| `IfcGrid` | 1 (17 U × 17 V) |
| `IfcMaterial` | 34 (consolidados de 39) |

---

## 8. Próximas fases sugeridas (Fase 3+)

1. **Roteirização MEP LOD 350** — o MEP atual é representativo; detalhar conexões,
   conexões (fittings), inclinações de esgoto e suportes, e re‑rodar a furação.
2. **Quantitativos e 5D** — exportar `BaseQuantities` + materiais consolidados para
   planilha de orçamento; vincular ao cronograma (4D).
3. **Pranchas e documentação** — gerar plantas/cortes cotados a partir do IfcGrid.
4. **IDS + verificação automática** — formalizar requisitos de informação e validar
   a cada revisão (IfcOpenShell/BIMcollab/Solibri).

---

## 9. Arquivos entregues nesta fase

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v88_Arq_MEP_executivo.ifc` | Modelo executivo (clash‑free, com eixos, materiais saneados e furação) |
| `HVG_Brumadinho_Fase2_Coordenacao.md` | Este relatório |
| `HVG_v88_Clash_Report_Final.csv` | Registro de interferências (avaliado) |
| `HVG_v88_Registro_Furacao.csv` | Registro das 329 passagens/sleeves |
| `clash_full_report_v88.json` | Log técnico de clash detection |
| `clash_detection_full.py`, `fase2_model.py`, `fase2_furacao.py` | Scripts reproduzíveis |
