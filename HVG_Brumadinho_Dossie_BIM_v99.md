# Dossiê de Entrega BIM — Hotel Vila Galé Collection Brumadinho

**Modelo federado de entrega:** `HVG_MASTER_v99_PROFISSIONAL.ifc` (IFC4, 50,6 MB)
**Coordenação BIM:** Grupo Montex · **Data:** 28/06/2026 · **Revisão:** v99
**CRS:** SIRGAS 2000 / UTM 23S (EPSG:31983) — E 578.800 / N 7.773.500 / H 935

---

## 1. Visão geral do empreendimento

Resort hoteleiro multidisciplinar em Brumadinho-MG, modelado em BIM federado cobrindo
**Arquitetura + Estrutura + MEP + Urbanismo**, com 26 edificações:

- **Bloco Principal** (recepção, restaurantes, administração) — estrutura metálica sobre pilotis
- **16 blocos residenciais** (Tipo A 6 vãos / Tipo B 8 vãos · apto-módulo 35,20 m² · pé-direito 2,79 m)
- **Edifícios comuns:** Centro de Convenções, Boîte, Restaurante da Piscina, SPA, Clube NEP, Guarita
- **Infraestrutura:** Subestação, Central de Gás, Apoio às Quadras, urbanismo/paisagismo

**Área útil total ≈ 31.585 m²** · **Prazo ≈ 26 meses** (set/2026 → out/2028).

---

## 2. Dimensões BIM entregues (nD)

| Dim. | Conteúdo | Evidência no IFC |
|------|----------|------------------|
| **3D** | Geometria LOD 300–500, materiais com cor (renderizável), mobiliário hoteleiro | 67 materiais com `IfcSurfaceStyle`; 1.760 móveis (`IfcFurniture`) |
| **4D** | Cronograma vinculado (8 fases, terraplenagem → urbanismo) | 8 `IfcTask` + `IfcWorkSchedule` |
| **5D** | Orçamento por composição (SINAPI) — **R$ 42,17 milhões** | `IfcCostSchedule` + 15 `IfcCostItem` (BRL) |
| **6D** | Zonas/ambientes com áreas oficiais, sistemas e classificação | 33 `IfcZone`, 6 sistemas MEP, 2 `IfcClassification` |
| **7D** | Ativos as-built FM/COBie (fabricante, garantia, vida útil, manutenção) | `COBie_Asset_AsBuilt` + `Pset_Warranty` + `Pset_ManufacturerTypeInformation` em 7.011 elementos |

Acrescenta-se a camada de **coordenação** (clash resolvido) e os **underlays DXF georreferenciados**
(9 plantas em camadas travadas) herdados das revisões anteriores.

---

## 3. 5D — Orçamento (SINAPI por composição)

| Serviço | Subtotal (R$) |
|---------|---------------|
| Estrutura concreto armado (1.026 m³) | 2.828.116 |
| Lajes de piso (Steel Deck, 26.437 m²) | 7.930.980 |
| Alvenaria + revestimento + pintura (25.974 m²) | 5.402.648 |
| Esquadrias alumínio + vidro (3.028 m²) | 2.876.220 |
| Portas internas (223 un) | 289.900 |
| Cobertura e revestimentos (21.704 m²) | 3.581.083 |
| Hidrossanitária / incêndio (4.200 m) | 399.010 |
| AVAC (1.120 m) | 268.872 |
| Elétrica (1.142 m) | 171.345 |
| Pavimentação / urbanismo (30.610 m²) | 4.132.404 |
| + Fundações (8%) / Instalações (10%) / Canteiro (3%) / BDI (25%) | 14.288.796 |
| **TOTAL GERAL ESTIMADO** | **≈ R$ 42,17 milhões** |

> Valores de **referência** (base 2026), embutidos no IFC como `IfcCostItem`/`IfcCostValue` (BRL).
> Substituir pelas composições do orçamento executivo (SINAPI/SICRO/cotação) na fase seguinte.

---

## 4. 7D — Ativos as-built (FM / COBie)

Camada de gestão de facilities aplicada por tipo, com **fabricantes de referência** e dados de garantia/vida útil:

| Tipo | Fabricante ref. | Garantia | Vida útil |
|------|-----------------|----------|-----------|
| Esquadrias (`IfcWindow`) | Alcoa Linha Suprema + vidro laminado 8 mm | 20 anos | 10 anos |
| Estrutura (`IfcColumn`/`IfcBeam`) | Gerdau perfil W ASTM A500 Gr.B | 50 anos | 50 anos |
| Lajes (`IfcSlab`) | Steel Deck MF-75 + C25 | 50 anos | 50 anos |
| Revestimentos (`IfcCovering`) | Portobello porcelanato 60×60 / forro gesso | 5 anos | 5 anos |
| Cobertura (`IfcRoof`) | Telha cerâmica Vila Galé + Onduline | 20 anos | 20 anos |
| Guarda-corpos (`IfcRailing`) | Vidro laminado / inox 304 | 20 anos | 20 anos |
| MEP (`IfcPump`/`IfcTank`) | KSB / Fortlev | 15–20 anos | 15–20 anos |
| Mobiliário (`IfcFurniture`) | Todeschini MDF sob medida | 10 anos | 10 anos |

Status: **As-Built verificado (LOD500)** · manutenção preventiva anual.
Estrutura metálica com `Pset_Aco_Reconciliacao` (norma ASTM A500/A572, ~1.350 t, conexões parafusadas A325).

---

## 5. Coordenação — Clash Detection resolvido

Varredura multidisciplinar ARQ × EST × MEP (AABB, tolerância 4 cm):

| | Antes | Depois |
|--|-------|--------|
| Total de conflitos | 349 | **3** |
| Críticos | 7 | **0** |
| Altos | 243 | **0** |
| Médios | 99 | 3 |

**346 passagens/sleeves** (`IfcOpeningElement`) inseridas nos hosts ARQ/EST nos pontos de MEP.
Registro completo: `HVG_v99_Entrega/HVG_Clash_Report_Resolvido.xlsx`.

---

## 6. Renderização arquitetônica

| Imagem | Conteúdo |
|--------|----------|
| `renders/HVG_Render_BlocoPrincipal_LOD500.png` | Bloco Principal AS-BUILT — cores por material, estrutura metálica em pilotis, esquadrias envidraçadas |
| `renders/HVG_Render_Conjunto_Blender_Cycles.png` | Implantação do conjunto (16+ blocos) — Blender Cycles, sombras e terreno |
| `renders/HVG_Render_Conjunto_Cor.png` | Vista do conjunto colorida por material |

As cores estão embutidas no IFC (`IfcSurfaceStyle` por material), permitindo render direto em
qualquer visualizador BIM (BlenderBIM, Solibri, Navisworks, usBIM).

---

## 7. Quantitativos-chave (escopo modelado)

| Disciplina | Item | Quantidade |
|------------|------|------------|
| Estrutura | Pilares / Vigas / Lajes | 893 / 492 / 375 |
| Arquitetura | Paredes / Esquadrias / Portas | 25.974 m² / 3.028 m² / 223 un |
| Cobertura | Telhado | 15.694 m² |
| MEP | Tubulação / Dutos / Eletrocalhas | 4.200 / 1.120 / 1.142 m |
| Urbanismo | Pavimentação | 30.610 m² |
| Ambientes | `IfcSpace` (com área oficial) | 1.307 |
| Mobiliário | Peças (`IfcFurniture`) | 1.760 |

---

## 8. Conteúdo do modelo `v99` (resumo técnico)

- **Schema:** IFC4 · **Entidades:** 445.466 · **GUIDs únicos:** sim · **Georreferência:** EPSG:31983 íntegra
- **3D:** 67 materiais com cor · 1.760 móveis · 9 underlays DXF (camadas travadas)
- **4D:** 8 tarefas / cronograma · **5D:** 1 orçamento / 15 itens (BRL) · **7D:** 13 tipos FM/COBie (7.011 elementos)
- **6D:** 33 zonas · 6 sistemas MEP · 2 classificações (Uniclass + MTX-CLS)
- **Documentos vinculados:** 4 (`IfcDocumentReference` → renders, clash, dossiê)

---

## 9. Arquivos entregues

| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v99_PROFISSIONAL.ifc`** | **Modelo BIM multidisciplinar nD (entrega final)** |
| `HVG_v99_Entrega/renders/*.png` | Renders arquitetônicos (Bloco Principal + conjunto) |
| `HVG_v99_Entrega/HVG_Clash_Report_Resolvido.xlsx` | Relatório de clash resolvido |
| `HVG_Brumadinho_Dossie_BIM_v99.md` | Este dossiê |
| `build_v99.py` | Script reproduzível (5D + 7D + aço + documentos) |

> **Procedência dos dados:** os parâmetros de fabricante/garantia, materiais e o orçamento foram
> consolidados a partir do pacote federado **LOD400/LOD500 AS-BUILT** (Grupo Montex) e dos relatórios
> SINAPI das revisões anteriores, mantendo o `HVG_MASTER` como modelo de coordenação multidisciplinar.
