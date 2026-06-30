# HVG Inhotim — Comparação Referência Fotográfica × Modelo BIM

## Auditoria de aderência do modelo IFC ao construído (foto real × `HVG_MASTER_v105_REALISTA.ifc`)

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Cliente / Requerente:** Vila Galé
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo auditado:** `HVG_MASTER_v105_REALISTA.ifc` (IFC4, ~55 MB, 505.115 entidades, 51.843 objetos `IfcRoot`)
**Referência:** `referencias/Inhotim_Projeto_3D.pdf` — *Hotel Vila Galé Inhotim, Projeto 3D* (15 páginas, fotografias do empreendimento construído)
**Data:** 29/06/2026

---

## 1. Objetivo

Confrontar **fotografias do hotel construído** (deck oficial "Inhotim – Projeto 3D")
com o **modelo BIM atual (v105 "REALISTA")**, registrando:

1. o que o modelo **já representa fielmente** (validação positiva);
2. as **divergências arquitetônicas** ainda presentes (geometria/material/LOD);
3. uma lista priorizada de **ações para a próxima revisão (v106)**.

A referência fotográfica documenta as seguintes áreas: Bloco Principal (exterior),
Recepção, Restaurante, Convenções, Piscina das Crianças / Parque aquático,
Clube da Criança / Pista de carros e SPA (piscina interior aquecida).

---

## 2. Estado do modelo v105 (síntese quantitativa)

A v105 "REALISTA" é um salto de detalhamento de interiores/acabamentos sobre a v90:

| Entidade | v90 (LOD300) | v105 (REALISTA) | Δ |
|----------|-------------:|----------------:|----|
| Entidades totais | 320.791 | **505.115** | +57 % |
| `IfcWall` | 592 | **1.360** | +768 |
| `IfcWindow` | 542 | **942** | +400 |
| `IfcDoor` | 223 | **607** | +384 |
| `IfcStair` | 0 | **21** | +21 |
| `IfcRailing` | — | **79** | +79 |
| `IfcFlowTerminal` | — | **357** | +357 |
| `IfcFurniture` | 1.760 | 1.760 | — |
| `IfcRoof` | 31 | 31 | — |
| `IfcColumn` / `IfcBeam` / `IfcMember` | 893 / 492 / 24 | 893 / 492 / **24** | — |

**Leitura:** a evolução v90→v105 concentrou‑se em **vedação interna, esquadrias,
circulação vertical (escadas/guarda‑corpos) e louças/terminais** — o "realismo" de
interiores. A **macroestrutura e as coberturas permaneceram inalteradas**, e é
justamente aí que estão as divergências em relação às fotos (§4).

Validação de integridade (v105):
- Schema **IFC4** válido (leitura IfcOpenShell 0.8.5 OK).
- **51.843 GlobalIds — 0 duplicados.**
- 6 sistemas de distribuição MEP (`IfcDistributionSystem`).
- 69 materiais (`IfcMaterial`).
- Pendências menores de contenção espacial: 4 `IfcRoof` + 1 `IfcCovering` +
  22 `IfcElementAssembly` sem `IfcRelContainedInSpatialStructure`
  (os 1.549 `IfcOpeningElement` "sem contenção" são vãos, ligados por
  `IfcRelVoidsElement` — comportamento correto, não são órfãos).

---

## 3. O que o modelo já representa fielmente ✔

| Área (foto) | Confirmação no modelo v105 |
|-------------|----------------------------|
| **Bloco Principal — volume de 2 pavimentos, fachada totalmente envidraçada** (p.5–7) | Edifício "Bloco Principal" com 289 pilares, fechamentos `IfcWindow` em fita e `IfcWall`; malha regular de pilares coerente com a foto interna do restaurante (p.10). |
| **Restaurante — pé‑direito duplo, pilares brancos esbeltos, laje/forro metálico** (p.10) | "Bloco Principal" modela a malha de pilares e a estrutura metálica à vista descrita no Quadro Sinóptico; esquadrias de piso a teto presentes. |
| **Centro de Convenções — pavilhão térreo alongado** (p.11) | Edifício "Centro de Convenções", 50 pilares, cobertura em 2 águas. |
| **Restaurante da Piscina / volumes de apoio** (p.5, fundo) | Edifício "Restaurante da Piscina", 32 pilares, 2 pavimentos. |
| **SPA — grande salão único da piscina interior** (p.14) | Edifício "SPA", pavimento único "SPA‑Terreo", 24 pilares — **planta correta** (a divergência é só a cobertura, §4.1). |
| **Implantação — lagos ornamentais, vegetação densa, quadras** (p.13, fundo) | 287 `IfcGeographicElement` (Ipê‑Amarelo, Araucária, Quaresmeira, Palmeira‑Imperial, nenúfares em 2 lagos) + postes de quadras (`IfcMember`). |
| **Apartamentos escalonados na encosta com cobertura plana** | 16 blocos A/B com `FLAT_ROOF` em laje impermeabilizada — coerente com os cortes. |

---

## 4. Divergências em relação ao construído ✕ (prioridade para v106)

### 4.1 SPA — cobertura **plana no modelo × telhado de tesouras de madeira na realidade** 🔴 *(alta)*
- **Foto (p.14):** a piscina interior aquecida é coberta por um **telhado inclinado
  com tesouras/estrutura de madeira aparente** (escura) e telhamento cerâmico/sanduíche
  — é o elemento arquitetônico mais marcante do ambiente.
- **Modelo v105:** o SPA tem `IfcRoof` = **`FLAT_ROOF` "Cobertura‑Plana‑Laje
  Impermeabilizada"**, `IfcMember` = **0** (nenhuma tesoura).
- **Ação v106:** substituir a laje plana por **cobertura inclinada** e modelar as
  **tesouras de madeira** como `IfcMember`/`IfcElementAssembly` (PredefinedType
  estrutura de madeira), com material *Madeira Lamelada/Maciça* e telha cerâmica.

### 4.2 Recepção — **treliça espacial metálica aparente não modelada** 🔴 *(alta)*
- **Foto (p.8):** o lobby da recepção é coberto por uma **grande treliça espacial
  (space‑frame) metálica aparente**, ícone do átrio de entrada.
- **Modelo v105:** o "Bloco Principal" tem **0 `IfcMember`** e apenas 8 `IfcBeam`;
  não existe qualquer elemento nomeado "treliça/tesoura/space‑frame" no modelo inteiro
  (busca textual: 0 ocorrências).
- **Ação v106:** modelar a treliça do átrio como `IfcElementAssembly` de `IfcMember`
  (banzos/diagonais SHS), aço aparente, sob a cobertura central do Bloco Principal.

### 4.3 Bloco Principal — cobertura nomeada "Piramidal" × **hipped de baixa inclinação com grandes beirais** 🟠 *(média)*
- **Foto (p.5, p.6, p.7):** a cobertura é um **telhado de 4 águas de baixa inclinação,
  com beirais (abas) muito profundos em balanço** sobre as fachadas envidraçadas —
  não um volume piramidal acentuado.
- **Modelo v105:** `IfcRoof` `HIP_ROOF` "**Cobertura‑Piramidal**‑Telha Cerâmica Vila Galé".
  O **tipo `HIP_ROOF` está correto**, mas o **nome ("Piramidal") e provavelmente a
  geometria/inclinação** sugerem volume mais alto que o real.
- **Ação v106:** ajustar a inclinação para baixa declividade e **modelar os beirais em
  balanço**; renomear para "Cobertura‑4Águas‑Beiral‑Profundo".

### 4.4 SPA / Restaurante da Piscina — coberturas inclinadas reais lidas como planas 🟠 *(média)*
- Tanto o SPA (§4.1) quanto outros pavilhões de lazer aparecem nas fotos com
  **telhados inclinados de telha** sobre estrutura aparente, enquanto o modelo usa
  `FLAT_ROOF`. Revisar caso a caso contra o projeto de coberturas.

### 4.5 Áreas de lazer — **mobiliário/equipamento lúdico ausente** 🟢 *(baixa — LOD de cenografia)*
- **Parque aquático / Piscina das Crianças (p.12):** brinquedos aquáticos
  (cogumelos, baldes, escorregas, esculturas), guarda‑sóis e espreguiçadeiras
  coloridas — **não modelados** (modelo tem lâmina d'água/piscina, sem os brinquedos).
- **Clube da Criança / Pista de carros (p.13):** a **pista de kart infantil** com
  pintura viária e placas de sinalização **não está modelada** como elemento
  dedicado (existe a quadra/área desportiva, não a pista).
- **Ação v106 (opcional):** incluir como `IfcFurniture`/`IfcGeographicElement` se o
  uso pretendido (apresentação/marketing) exigir esse nível de cenografia.

---

## 5. Matriz‑resumo

| # | Item | Foto (referência) | Modelo v105 | Severidade | Ação v106 |
|---|------|-------------------|-------------|:----------:|-----------|
| 1 | Cobertura do SPA | Tesouras de madeira inclinadas (p.14) | `FLAT_ROOF` laje | 🔴 Alta | ✅ **Resolvido na v106** — telhado 2 águas + 7 tesouras de madeira |
| 2 | Treliça da Recepção | Space‑frame metálico aparente (p.8) | 0 `IfcMember` no BP | 🔴 Alta | ✅ **Resolvido na v106** — treliça espacial (288 barras) |
| 3 | Cobertura Bloco Principal | Hip baixa + beirais profundos (p.5–7) | `HIP_ROOF` "Piramidal" | 🟠 Média | ✅ **Resolvido na v107** — hip baixa renomeada + beiral +2,5 m |
| 4 | Coberturas de pavilhões | Inclinadas de telha | Algumas `FLAT_ROOF` | 🟠 Média | Revisar projeto de coberturas |
| 5 | Brinquedos do parque aquático | Equipamento lúdico (p.12) | Ausente | 🟢 Baixa | `IfcFurniture` (opcional) |
| 6 | Pista de carros infantil | Pista pintada + placas (p.13) | Ausente | 🟢 Baixa | Elemento dedicado (opcional) |
| 7 | Contenção espacial residual | — | 4 roofs + 1 covering + 22 assemblies sem contenção | 🟢 Baixa | Atribuir a pavimento/site |
| 8 | Proporção da planta do Bloco Principal | Retangular alongada (p.5–7) | Pegada ~quadrada 80×80 | 🟠 Média | ✅ **Recalibrado na v110** pela planta oficial — ~58,7×57 + IfcGrid (v109 substituída) |

---

## 6. Conclusão

O **`HVG_MASTER_v105_REALISTA.ifc` é um modelo arquitetônico maduro e quantitativamente
consistente** (IFC4 válido, GUIDs únicos, 6 sistemas MEP, interiores fortemente
detalhados). A confrontação com as fotografias do construído mostra **alta aderência
de implantação, volumetria, fachadas e programa**.

As divergências remanescentes são **focadas e localizadas**, concentrando‑se em
**coberturas e estruturas de cobertura aparentes** — em especial **(1) o telhado de
tesouras de madeira do SPA** e **(2) a treliça espacial metálica da recepção**, os dois
elementos estruturais mais característicos das fotos e que ainda são lidos como
laje plana / ausentes no modelo. Resolvê‑los é a prioridade da v106 para que o
modelo "REALISTA" também o seja na quinta fachada (cobertura) e nas estruturas à vista.

---

## 7. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v105_REALISTA.ifc` | Modelo BIM atual auditado (IFC4, REALISTA) |
| `HVG_Inhotim_Comparacao_Foto_x_Modelo_v105.md` | Este relatório de comparação foto × modelo |
| `referencias/Inhotim_Projeto_3D.pdf` | Deck fotográfico de referência (15 páginas) |
| `referencias/Inhotim_Projeto_3D_paginas/page_01..15.png` | Páginas do deck renderizadas (para citação direta) |
| `audit_foto_x_modelo.py` | Script reprodutível da auditoria (coberturas/estrutura por edifício) |
