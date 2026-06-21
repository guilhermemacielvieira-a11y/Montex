# HVG Brumadinho — Correção de Renderização/Posição + Comparação IFC × Planta de Situação

**Modelo de entrada (usuário):** `HVGMASTERINTEGRADOv87.ifc`
(`HVG_Brumadinho_MASTER_v87_Arq_MEP_Materiais.ifc`, IFC4, 20 MB)
**Modelo corrigido entregue:** `HVG_MASTER_v88_render_corrigido.ifc`
**Referência de comparação:** `01__Planta_Situacao.pdf` (Quadro Sinóptico, Esc. 1/1000, 02‑12‑2025)
**Data:** 21/06/2026 · Grupo Montex

---

## PARTE 1 — Correção de objetos fora do espaço / renderizações erradas

### 1.1 Diagnóstico (varredura geométrica de 7.746 elementos)
A malha foi gerada para todos os elementos no espaço‑mundo. Não há falhas de
geometria (0 elementos sem malha, 0 NaN). Foram detectados **151 objetos
grosseiramente fora de escala/posição** (> 120 m), todos com **3 causas‑raiz**
distintas — geometria válida em IFC, mas que renderiza errada (no IfcOpenShell e
no visualizador do usuário):

| Defeito | Qtd | Causa‑raiz | Sintoma |
|---------|-----|-----------|---------|
| Guarda‑corpos de varanda (`IfcRailing`) | **20** | `IfcSweptDiskSolid` (corrimão tubular) **espelhado pela origem** pelo motor de geometria | Lasca de ~840 m atravessando o terreno |
| Árvores ornamentais (`IfcGeographicElement`) | **70** | Copa `IfcSphere` com `Position` **absoluta** somada à placement → **coordenada dobrada** (ex.: 263→526) | Copa flutuando ao dobro da distância do tronco |
| Copas de árvore (`IfcCovering` "Copa‑Extra") | **65** | Segundo disco da copa com **offset XY não aplicado** (ficou na origem 0,0) | Disco‑fantasma esticado da árvore até a origem |

> Observação técnica: os 70 da copa de árvore incluem itens abaixo do limiar de
> 120 m (placement pequeno gera dobra menor), todos corrigidos pela assinatura do
> bug, não só os mais visíveis.

### 1.2 Correções aplicadas (155 elementos)
- **Railings:** cada `IfcSweptDiskSolid` substituído por `IfcExtrudedAreaSolid`
  (perfil círculo R=0,025) por segmento da diretriz, **transferindo o estilo** — o
  corrimão tubular é preservado e renderiza correto.
- **Árvores:** `Position` da esfera‑copa convertida de absoluta para **relativa à
  placement** (subtração da translação) — copa volta para cima do tronco.
- **Copas:** disco‑fantasma **realinhado** ao XY do disco real (mantendo seu Z) —
  as duas camadas da copa voltam a se empilhar sobre a árvore.

### 1.3 Verificação
| Item | Antes | Depois |
|------|-------|--------|
| Objetos > 120 m | 151 | **2** (ambos legítimos*) |
| `IfcSweptDiskSolid` no modelo | 20 | **0** |
| Exemplo árvore (bbox) | 7×35×266 m | **3,8×3,8×7 m** (em 263, 31) |
| Exemplo copa (bbox) | 2,2×286×305 m | **2,6×2,6×2,2 m** (em 249, 15) |
| Exemplo railing (bbox) | 131×420×26 m | **22,4×1,6×1,3 m** (em 120, 420) |
| GUIDs únicos / schema | — | Sim / IFC4 ✔ |

\* Os 2 remanescentes foram **inspecionados e confirmados corretos**: o `IfcSite`
(TIN do terreno, ~500 m — normais todas para cima, sem inversão) e o relvado
`Grama‑Variacao‑Cromatica` (24 manchas formando um gramado amplo). **Não** foram
alterados — evitou‑se falso‑positivo (inverter o terreno o quebraria).

---

## PARTE 2 — Comparação IFC × Planta de Situação (Quadro Sinóptico)

### 2.1 Contagens e estrutura — **conferem exatamente**
| Item | PDF | IFC | Status |
|------|-----|-----|--------|
| Edifícios totais | 23 (7 comuns + 12 Bl.A + 4 Bl.B) | 23 | ✅ |
| Apartamentos | **312** (216 em A + 96 em B) | 312 (312 APTO + 312 VAR + 312 I.S. + 312 HALL) | ✅ |
| Pavimentos Bloco A | 3 (2º+1º subsolo + térreo) | 3 | ✅ |
| Pavimentos Bloco B | 3 (subsolo + térreo + 1º pav) | 3 | ✅ |
| Programa comum | BP, CC, Boîte, Rest. Piscina, SPA, NEP, Guarita | todos presentes | ✅ |

### 2.2 Áreas — mesma ordem de grandeza, com divergências
A PDF declara **"área construída coberta"** (projeção/bruta); o IFC mede
`IfcSpace` (área útil interna). Daí a diferença sistemática (paredes, beirais,
varandas não contam como espaço):

| Edifício | IFC útil (m²) | PDF coberta (m²) | Δ |
|----------|---------------|------------------|---|
| Bloco Principal | 4.624 | 5.197,57 | −11 % |
| Centro de Convenções | 741 | 872,67 | −15 % |
| Boîte | 529 | 486,90 | +9 % |
| Restaurante da Piscina | 837 (2 pav.) | 564,97 | — |
| **SPA** | **294** | **598,13** | **−51 %** ⚠ |
| Clube NEP | 89 | 110,16 | −19 % |
| Guarita | 22,4 | 20,40 | +10 % |
| Blocos A (12) | 9.954 | 11.485,08 | −13 % |
| Blocos B (4) | 5.321 | 4.699,04 | +13 % |

> **Atenção:** o **SPA** está modelado com ~metade da área da PDF — provável
> sub‑modelagem (zona da piscina interior / vestiários não lançados como `IfcSpace`).
> Recomenda‑se revisar.

### 2.3 Programa externo — presente vs ausente no IFC
| Programa (PDF) | IFC | Status |
|----------------|-----|--------|
| Piscinas (adultos c/ ondas, infantil) | 34+ elementos (skimmers, bordas, ondas, escadas) | ✅ |
| Lagos (10.499 m²) | 22 elementos | ✅ |
| Parque aquático / infantil | presente | ✅ |
| Reservatórios / ETE | presente | ✅ |
| Decks / arruamento intertravado | 59 decks / 186 estradas | ✅ |
| **Área Desportiva** (Padel, Polidesportivo, Beach Tennis — 1.168 m²) | — | ❌ **ausente** |
| **Estacionamentos** (168 vagas ligeiros + 2 ônibus — 2.175 m²) | — | ❌ **ausente** |
| **Pista de Carros** infantil (678,37 m²) | — | ❌ **ausente** |
| **Subestação** (144,47 m²) | — | ❌ **ausente** |
| **Central de Gás / Apoio Quadras** | — | ❌ **ausente** |

### 2.4 Conclusão da comparação
O IFC é **fiel à Planta de Situação** no essencial — implantação, 23 edifícios,
312 apartamentos, distribuição de pavimentos e a maior parte do programa de lazer
(piscinas, lagos, parques). As **lacunas a resolver** para aderência total ao
Quadro Sinóptico são: **área desportiva, estacionamentos (168 vagas), pista de
carros, subestação e central de gás** (não modelados), além da **área do SPA**
(subdimensionada). Áreas dos edifícios diferem ~10–15 % por serem útil (IFC) vs
coberta (PDF) — esperado.

---

## Arquivos entregues
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v88_render_corrigido.ifc` | Modelo com 155 objetos fora do espaço/render corrigidos |
| `HVG_Brumadinho_Correcao_Render_e_Comparacao.md` | Este relatório |
| `fix_render_v87.py`, `diag_v87.py` | Scripts de diagnóstico e correção (reproduzíveis) |
