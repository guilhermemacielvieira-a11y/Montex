# HVG Inhotim — Revisão v109

## Reestruturação da planta do Bloco Principal: pegada quadrada → proporção retangular real

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc`
**Entregue:** `HVG_MASTER_v109_PLANTA_RETANGULAR.ifc`
**Data:** 30/06/2026

---

## 1. Objetivo

Resolver a observação estrutural registrada na v107: a planta do Bloco Principal
era **quase quadrada (~80 × 80 m)**, o que forçava qualquer cobertura de 4 águas
a um aspecto piramidal e divergia da volumetria **retangular alongada** do edifício
real (fotografias p.5–7). Esta revisão **reestrutura a planta** para a proporção
retangular, permitindo enfim uma cobertura com **cumeeira longa**.

---

## 2. Método — escala anisotrópica preservando a área

Aplicada uma transformação de escala não‑uniforme a **todos** os elementos do
Bloco Principal, em torno do centro C = (165, 245), preservando a área construída:

| Fator | Valor | Efeito |
|-------|-------|--------|
| `KX` | √1,6 ≈ **1,265** | alonga o eixo X |
| `KY` | 1/√1,6 ≈ **0,791** | comprime o eixo Y |
| Razão final | **1,60 : 1** | de 80×80 m para **≈ 101 × 63 m** (área ~constante) |

O Bloco Principal é um **pavilhão de pilares** (289 pilares, apenas 8 paredes
perimetrais, 2 lajes, 4 janelas), o que tornou a operação controlada:

| Ação | Qtd | Como |
|------|----:|------|
| Elementos reposicionados | **416** | escala da origem do placement em torno de C (pilares, terminais, escadas, janelas, vigas, bombas, eletrocalhas…) |
| Paredes perimetrais esticadas | **8** | `XDim` do perfil escalado pelo fator do eixo (X→KX, Y→KY) |
| Lajes esticadas | **2** | `XDim`·KX, `YDim`·KY |
| Espaços (zonas) reajustados | **16** | perfil + reposição |
| Cobertura | regenerada | hip com **cumeeira longa (37,8 m)**, beiral +2,5 m, ~7,5° |
| Treliça espacial da recepção | reconstruída | **320 barras** sobre o novo átrio (8×5 módulos) |

Elementos‑filho (`IfcStairFlight`, `IfcOpeningElement`) foram preservados — seguem
seus hospedeiros automaticamente, evitando duplo deslocamento.

---

## 3. Validação do entregável (v109)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 512.382 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Pilares do BP | **289/289** com geometria válida |
| Nova pegada (pilares) | X = **101 m**, Y = **63 m**, **razão 1,60** ✔ |
| Paredes perimetrais | acompanham a malha (planta comparada) ✔ |
| Cobertura | cumeeira horizontal de 37,8 m (não mais piramidal) ✔ |
| Demais edifícios (ex.: Bloco‑A‑01) | **inalterados** ✔ |
| Revisões anteriores (SPA, cenografia) | preservadas |

> Previews: `referencias/v106_previews/v109_planta_comparacao.png` (planta v108 × v109)
> e `referencias/v106_previews/v109_bloco_principal_3d.png` (volumetria 3D).

---

## 4. Estado final das divergências foto × modelo

| # | Item | Status |
|---|------|--------|
| 4.1 | Cobertura do SPA (tesouras de madeira) | ✅ v106 |
| 4.2 | Treliça espacial da recepção | ✅ v106 |
| 4.3 | Cobertura do Bloco Principal (hip + beiral) | ✅ v107 |
| 4.5 | Parque aquático infantil | ✅ v108 |
| 4.6 | Pista de carros (sinalização + pintura) | ✅ v108 |
| — | **Proporção retangular do Bloco Principal** | ✅ **v109** |

**Todas as divergências da auditoria foram resolvidas.**

---

## 5. Observações e próximos passos sugeridos

- A escala anisotrópica reposiciona a malha de pilares de forma **uniforme**
  (espaçamento X ≈ 6,3 m, Y ≈ 3,9 m); um eventual ajuste para um **módulo
  estrutural específico** (com `IfcGrid` formal) é uma evolução natural.
- Recomenda‑se confrontar a nova pegada com a **planta de implantação oficial**
  para calibrar exatamente as dimensões (esta revisão adotou razão 1,6:1 com
  área preservada como aproximação fiel à leitura fotográfica).
- Migrar os `.ifc` (≈ 53–56 MB) para **Git LFS** caso o histórico cresça.

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v109_PLANTA_RETANGULAR.ifc` | Modelo BIM v109 (IFC4) |
| `build_v109.py` | Construtor reprodutível (v108 → v109) |
| `HVG_Inhotim_v109_Planta_Retangular.md` | Este relatório |
| `referencias/v106_previews/v109_planta_comparacao.png` | Planta v108 × v109 |
| `referencias/v106_previews/v109_bloco_principal_3d.png` | Volumetria 3D do bloco |
