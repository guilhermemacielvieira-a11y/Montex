# HVG Brumadinho — Vila Galé Collection
## Planejamento BIM e Relatório de Coordenação / Aperfeiçoamento do Modelo IFC

**Projeto:** Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Cliente / Requerente:** Vila Galé
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Fase:** Licenciamento → Coordenação MEP / Compatibilização
**Modelo base analisado:** `HVGMASTERINTEGRADOv86.ifc` (IFC4, 20 MB, ~320,8 mil linhas)
**Entregue:** `HVG_MASTER_v87_Arq_MEP_coordenado.ifc`
**Data:** 19/06/2026

---

## 1. Sumário executivo

Atuando como projetista BIM sênior / arquiteto, foi feita uma análise minuciosa de toda a
arquitetura e da estrutura do modelo IFC entregue, confrontada com os projetos básicos de
arquitetura (Planta de Situação, Bloco Principal — Subsolo/Térreo/Cobertura/Fachadas,
Bloco de Apartamentos A — Cortes e Fachadas, Bloco de Apartamentos B — Plantas) e com os
relatórios de interferências (BCF + CSV BIMcollab).

O modelo v86 já é um modelo **maduro, LOD 300**, com hierarquia espacial completa
(Site → 23 Edifícios → 57 Pavimentos → 1.290 Ambientes), estrutura metálica/concreto,
MEP de 5 sistemas, topografia TIN real e paisagismo. O trabalho desta entrega **aproveitou
integralmente essa estrutura** e concentrou‑se em **corrigir, sanear e aperfeiçoar**:

| # | Ação | Resultado |
|---|------|-----------|
| 1 | Resolução das 25 interferências MEP × Estrutura do BCF | **25/25 resolvidas** |
| 2 | Varredura geométrica completa terminal × pilar (além do BCF) | **+36 interferências ocultas detectadas e resolvidas → 61 no total** |
| 3 | Saneamento de elementos órfãos (sem contenção espacial) | **5 → 0** |
| 4 | Completar associação de material (muros de arrimo + pavimentação/paisagismo) | **196 elementos → 0 pendências** |
| 5 | Validação final do IFC4 (schema, GUIDs, contenção, geometria) | **0 erros / 0 clashes residuais** |

Deslocamento máximo aplicado a qualquer terminal: **0,50 m** (mediana 0,20 m), preservando
o espaçamento de cobertura de sprinklers (NBR 10897) e a distribuição de difusores.

---

## 2. Análise da arquitetura (a partir dos projetos básicos)

### 2.1 Implantação (Planta de Situação, Esc. 1/1000)
- **Área do terreno:** 105.020,58 m² (10,5 ha), perímetro 1.397,15 m.
- **Topografia natural:** cotas 875 → 985 m, declive SW→NE na encosta da Serra da Moeda.
- **Taxa de ocupação:** 16,16 % · **Índice de permeabilidade:** 81,02 %.
- **Área total construída coberta:** 24.408,20 m².
- Sistema viário intertravado sinuoso, 168 vagas de veículos ligeiros + 2 de ônibus,
  lagos, piscinas (adultos c/ ondas, crianças c/ parque aquático), área desportiva
  (padel, polidesportivo, beach tennis), pista de carros infantil, tirolesa.

### 2.2 Programa edificado (Quadro Sinóptico)
| Edifício | Área (m²) | Observações arquitetônicas |
|----------|-----------|----------------------------|
| Bloco Principal (Recepção, Bar, Restaurantes) | 5.197,57 | Cobertura piramidal cerâmica Vila Galé 45 % central + abas 25 % |
| Centro de Convenções | 872,67 | Auditório, cobertura 2 águas Onduline/sanduíche 25 % |
| Boîte Soul & Blues | 486,90 | Cobertura piramidal Onduline 25 % |
| Restaurante da Piscina | 564,97 | 2 pavimentos + rooftop, estrutura SHS200×8 |
| SPA c/ piscina interior | 598,13 | — |
| Clube NEP (Kids Club) | 110,16 | — |
| Guarita | 20,40 | — |
| Blocos de Apartamentos **A** (12 blocos) | 11.485,08 | 2º Subsolo + 1º Subsolo + Térreo, 6 aptos/pav → **216 aptos** |
| Blocos de Apartamentos **B** (4 blocos) | 4.699,04 | Subsolo + Térreo (12) + 1º Pav, → **96 aptos** |
| **Total de apartamentos** | | **312 aptos** |

### 2.3 Bloco Principal — leitura dos desenhos
- **Subsolo (cota −3,00):** núcleo de serviço em "U" (cozinhas, câmaras, apoios) e
  grandes salões de restaurante; projeção de cobertura piramidal central.
- **Térreo (cota 0,00):** grande salão aberto com **malha regular de pilares** (~4,97 m)
  no setor de eventos/restaurante; estrutura metálica à vista (VT, PMT, PAL, VAL),
  fechamentos envidraçados, guarda‑corpos h=1,10 m; painéis de restaurantes
  (Versátil, NEP, Massa Fina). **É exatamente nesse salão que ocorrem as interferências MEP.**
- **Cobertura:** telhas Onduline/sanduíche em 45 % (central) e 25 % (abas) +
  trechos de **laje plana impermeabilizada**; pé‑direito até 2,98 m; fachadas com
  pirâmide central marcante.

### 2.4 Blocos de Apartamentos (A e B)
- **Tipologias (Bloco B):** apto 19,20 / 24,80 / 27,20 / 32,80 m²; varanda 8,57 m²;
  I.S. 6,20 m²; hall 6,13–8,20 m². Módulo estrutural 3,00 + 1,19 m (vão total 25,34 m).
- **Pé‑direito:** 2,60 m + 0,20 m de laje ≈ 2,80 m por pavimento.
- **Implantação escalonada na encosta** com coberturas em **laje impermeabilizada**
  (terraços verdes) — confirmado nos cortes do Bloco A.

---

## 3. Estrutura ideal de um IFC completo (planejamento de referência)

Padrão adotado/validado para o projeto (IFC4 Reference View, MVD coordenação):

```
IfcProject  (unidades SI: m, m², m³, rad · contexto Model 3D · georref. SIRGAS 2000 / UTM 23S — EPSG:31983)
└─ IfcSite  (terreno 105.020,58 m² · TIN topográfico real · cota base ~950 m)
   ├─ IfcBuilding × 23
   │  └─ IfcBuildingStorey × 57   (Subsolos, Térreos, Pavimentos, Rooftops, Coberturas)
   │     ├─ Estrutura:  IfcColumn (SHS/concreto) · IfcBeam (VT/VAL) · IfcSlab (Steel Deck MF‑75)
   │     ├─ Vedação:    IfcWall · IfcCurtainWall · IfcWindow · IfcDoor · IfcCovering · IfcRoof
   │     ├─ Espaços:    IfcSpace (1.290) com Pset_SpaceCommon + Qto_SpaceBaseQuantities
   │     └─ MEP (contido por pavimento):
   │           IfcFireSuppressionTerminal · IfcAirTerminal · IfcDuctSegment · IfcPipeSegment
   │           IfcCableCarrierSegment · IfcCableSegment · IfcElectricDistributionBoard ·
   │           IfcLightFixture · IfcCommunicationsAppliance
   └─ Mobiliário/Paisagismo: IfcFurniture · IfcGeographicElement · IfcGeographicElement (vegetação)

Agrupamentos transversais:
  IfcDistributionSystem × 5  (Incêndio · Climatização · Elétrica · Telecom · Hidráulica)
     ↳ IfcRelAssignsToGroup (elementos) + IfcRelServicesBuildings (edifícios atendidos)

Semântica obrigatória por elemento:
  • GlobalId (IfcGloballyUniqueId) único
  • IfcRelContainedInSpatialStructure  (todo elemento físico contido em um pavimento/site)
  • IfcRelAssociatesMaterial            (todo elemento com material)
  • Pset_*Common + BaseQuantities       (propriedades e quantitativos para 4D/5D)
  • IfcOwnerHistory                     (rastreabilidade)
```

Este "modelo‑alvo" foi a régua usada para auditar o v86. O modelo já aderia à maior parte;
as lacunas encontradas (contenção e material) foram fechadas — ver §5.

---

## 4. Análise das interferências (BCF / CSV BIMcollab)

### 4.1 Diagnóstico físico (causa‑raiz)
Os relatórios apontaram **25 colisões "Hard Clash"** entre terminais de teto e pilares
no **Bloco Principal — Térreo**. A investigação geométrica confirmou o mecanismo:

- **Pilares** de concreto **0,30 × 0,30 m** nascem no BP‑Subsolo (base Z = 13,05) e sobem
  6,85 m (topo Z = 19,90), atravessando o forro do Térreo.
- **Difusores de ar** (0,60 × 0,60 m, Z = 19,55) e **sprinklers** (0,10 × 0,10 m, Z = 19,05)
  foram lançados numa **malha coincidente com os centros dos pilares** → penetração de
  até 0,15 m (difusor cobre todo o pilar) e 0,06–0,12 m (sprinkler dentro do pilar).

### 4.2 Achado adicional (varredura completa)
A varredura geométrica 3D de **todos** os terminais contra **todos** os 289 pilares revelou
que o BCF capturou apenas parte do problema:

| Tipo | Reportados no BCF | Detectados na varredura | Total resolvido |
|------|-------------------|--------------------------|-----------------|
| Difusores de ar (Climatização) | 9 | +16 | **25** |
| Sprinklers (Incêndio) | 16 | +20 | **36** |
| **Total** | **25** | **+36** | **61** |

Além desses, 89 terminais estavam a menos de 5 cm de um pilar (risco de execução).

---

## 5. Correções e aperfeiçoamentos aplicados (v86 → v87)

### 5.1 Reposicionamento de terminais MEP (compatibilização)
Algoritmo de resolução com **deslocamento mínimo** (busca em 16 direções × passos de 5 cm),
garantindo folga ≥ 0,05 m de **todos** os pilares vizinhos e ≥ 0,10 m de terminais adjacentes,
sem rotação (cadeia de placement identidade verificada):

- 61 terminais reposicionados · deslocamento **mín 0,20 m / mediana 0,20 m / máx 0,50 m**.
- Edição feita no **ponto de placement próprio (folha) de cada terminal** — único por
  elemento (1 referência inversa), portanto sem efeito colateral em outros objetos.
- **Verificação pós‑edição: 0 interferências residuais terminal × pilar.**
- O espaçamento de cobertura é preservado (deslocamentos << espaçamento de 3–4,6 m).

Registro completo: `HVG_v87_Registro_Resolucao_Interferencias.csv` e `clash_resolution_log.json`.

### 5.2 Saneamento de contenção espacial (5 → 0 órfãos)
| Elemento | Antes | Depois |
|----------|-------|--------|
| 1 × IfcCovering "Grama‑Variação‑Cromática" (Z=0) | sem contenção | **IfcSite** |
| 4 × IfcRoof "Cobertura‑Plana‑Laje Impermeabilizada" (Z 7,6–9,4) | sem contenção | **B13/B14/B15/B16 — Pav1** (atribuídos por proximidade XY ao edifício) |

### 5.3 Completar associação de material (196 → 0 pendências)
| Elemento | Qtd | Material associado |
|----------|-----|--------------------|
| Muros de arrimo (IfcWall RetainingWall) | 9 | Concreto Armado C30 |
| Plataformas de corte/aterro + guias/meio‑fio (IfcSlab) | 55 | Concreto Armado C25 |
| Pavimento asfáltico + manchas/remendos | 109 | *Pavimento Asfáltico CBUQ* (novo) |
| Faixas/sinalização horizontal | 12 | *Termoplástico Sinalização Viária* (novo) |
| Canteiros + hortas orgânicas | 11 | *Terra Vegetal Adubada* (novo) |

### 5.4 Integridade preservada
Contagem de entidades, GUIDs, sistemas MEP e quantitativos mantidos; apenas
adicionadas relações de contenção/material e atualizados os placements dos terminais.

---

## 6. Validação final do entregável

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** (válido, leitura IfcOpenShell OK) |
| Entidades | 320.791 |
| GlobalIds únicos | **Sim** (31.029 objetos IfcRoot) |
| Interferências terminal × pilar | **0** |
| Slabs sem material | **0** |
| Walls sem material | **0** |
| Elementos físicos órfãos | **0** |
| Difusores / Sprinklers (preservados) | 73 / 102 |
| Sistemas de distribuição MEP | 5 (Incêndio, Climatização, Elétrica, Telecom, Hidráulica) |

---

## 7. Recomendações para evolução (próximas fases)

1. **Compatibilização MEP × MEP e MEP × Estrutura completa** — estender a varredura
   geométrica a dutos, tubulações, eletrocalhas e vigas (não apenas terminais × pilares).
2. **Consolidar materiais duplicados** — o modelo contém pares de `IfcMaterial` com nomes
   equivalentes (ex.: "Concreto Armado C25", "Vidro Laminado 8mm", "Aço ASTM A500" em duas
   grafias). Recomenda‑se unificar para uma biblioteca única de materiais.
3. **IfcGrid** — formalizar os eixos estruturais (malha ~4,97 m do Bloco Principal e módulos
   3,00+1,19 dos apartamentos) como `IfcGrid`, facilitando locação e conferência.
4. **Aberturas estruturais (IfcOpeningElement + IfcRelVoidsElement)** — onde MEP cruza
   lajes/paredes, modelar furos/passagens para coordenação executiva (furação).
5. **4D/5D** — vincular os `BaseQuantities` (já presentes) a cronograma e orçamento.
6. **IDS / Model checking** — fixar requisitos de informação (IDS) e rodar verificação
   automática (IfcOpenShell / BIMcollab / Solibri) a cada revisão.

---

## 8. Arquivos entregues

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v87_Arq_MEP_coordenado.ifc` | **Modelo BIM corrigido e aperfeiçoado** (IFC4) |
| `HVG_Brumadinho_Planejamento_BIM.md` | Este relatório de planejamento e coordenação |
| `HVG_v87_Registro_Resolucao_Interferencias.csv` | Registro das 25 issues do BCF resolvidas (status, posições, deslocamento) |
| `clash_resolution_log.json` | Log técnico dos 61 terminais reposicionados |
| `resolve_clashes.py` | Script de detecção/resolução de interferências (reprodutível) |
| `enhance_model.py` | Script de saneamento de contenção e materiais (reprodutível) |
