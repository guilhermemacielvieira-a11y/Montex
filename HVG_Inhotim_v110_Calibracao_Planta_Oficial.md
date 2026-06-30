# HVG Inhotim — Revisão v110

## Calibração do Bloco Principal pela PLANTA OFICIAL + formalização do IfcGrid

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc`
**Entregue:** `HVG_MASTER_v110_BP_CALIBRADO.ifc`
**Fontes oficiais:** `01 - Planta Situacao v9.dwg` · **`031 - Bloco Principal - Plantas.dwg`** ·
`032 - Bloco Principal - Cortes e Fachadas.dwg` (extraídas via LibreDWG 0.13.3)
**Data:** 30/06/2026

---

## 1. Achado da planta oficial (correção de rumo)

A leitura das **cotas reais** da planta de arquitetura do Bloco Principal
(`031 - Bloco Principal - Plantas.dwg`) revelou que **tanto o modelo quanto a
v109 estavam errados** quanto ao tamanho/proporção:

| Fonte | Footprint Bloco Principal | Malha | Pilares |
|-------|---------------------------|-------|---------|
| **Planta oficial (031)** | **≈ 58,7 m × 57,0 m** (quase quadrado) | **≈ 4,9 m** (~12 vãos) | ~13×13 |
| Modelo v90…v108 | 80 × 80 m (superdimensionado) | 5,0 m (16 vãos) | 17×17 = 289 |
| v109 (foto) | 101 × 63 m (1,6:1 — direção errada) | 6,3 × 3,9 m (não‑uniforme) | 289 |

Cotas medidas no DWG (DIMENSION_LINEAR, valores `act_measurement`):
- **Horizontais (X):** 58,73 · 58,71 · 58,67 m (três pranchas) → comprimento ≈ **58,7 m**
- **Verticais (Y):** 57,46 · 56,65 m → largura ≈ **57,0 m**
- **Módulo recorrente:** 4,96 / 4,86 m (confirma a malha documentada ~4,97 m)

> Ou seja: o edifício real é **quase quadrado (~58,7×57), não 80×80 e não
> retangular alongado**. A aparência alongada das fotos era distorção de
> perspectiva/grande‑angular. A planta oficial é a referência autoritativa.

---

## 2. O que foi feito (v110)

Rebaseado no **v108** (planta quadrada original + SPA/cenografia preservados),
descartando a reestruturação equivocada da v109:

1. **Escala** de paredes, lajes, terminais MEP, escadas, janelas e espaços do
   Bloco Principal para o footprint real **58,7 × 57,0 m** (em torno do centro
   C=(165,245); fatores KX=0,737, KY=0,716).
2. **Reconstrução da malha de pilares**: removidos os 289 pilares (17×17 a 5 m)
   e criados **169 pilares em malha 13×13** a **4,89 × 4,75 m** (≈ módulo
   documentado), seção 0,30×0,30, Concreto C25, nomeados `Pilar-BP-A1`…`M13`.
3. **IfcGrid formal** `BP-Malha-Estrutural`: **13 eixos U (1…13) × 13 eixos V
   (A…M)**, com geometria de eixos para coordenação/locação.
4. **Cobertura regenerada** (hip de 4 águas com beiral +2,5 m; como a planta é
   quase quadrada, a cumeeira é curta — aspecto quase piramidal **correto**).
5. **Treliça espacial da recepção reconstruída** (240 barras) sobre o átrio
   recalibrado.

---

## 3. Validação do entregável (v110)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 502.785 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Pilares do BP | **169/169** com geometria válida |
| Footprint medido (pilares) | X = 59,0 m · Y = 57,3 m (alvo 58,7 × 57,0) ✔ |
| `IfcGrid` | **13 U × 13 V**, eixos 1…13 / A…M ✔ |
| Malha (módulo) | 4,89 × 4,75 m (≈ 4,97 documentado) ✔ |
| Demais edifícios (Bloco‑A‑01 etc.) | **inalterados** ✔ |
| SPA (tesouras) + cenografia (v106–v108) | preservados |

> Previews: `referencias/v106_previews/v110_planta_grid_calibrado.png` (planta +
> IfcGrid cotada) e `v110_bloco_principal_3d.png` (volumetria).

---

## 4. Estado das divergências foto × modelo

| # | Item | Status |
|---|------|--------|
| 4.1 | Cobertura do SPA (tesouras de madeira) | ✅ v106 |
| 4.2 | Treliça espacial da recepção | ✅ v106 / recalibrada v110 |
| 4.3 | Cobertura do Bloco Principal (hip + beiral) | ✅ v107 / recalibrada v110 |
| 4.5 | Parque aquático infantil | ✅ v108 |
| 4.6 | Pista de carros | ✅ v108 |
| 8 | Proporção/tamanho do Bloco Principal | ✅ **v110 (calibrado pela planta oficial)** |
| — | **Malha estrutural formal (IfcGrid)** | ✅ **v110** |

> **Observação:** a v109 (101×63) fica **substituída** pela v110, que reflete as
> dimensões reais da planta oficial. O footprint corrigido (3.346 m²/pav) é
> coerente com a área do Quadro Sinóptico (5.197,57 m² para subsolo+térreo).

---

## 5. Nota técnica — extração dos DWG

Os DWG (AutoCAD 2018, objetos AEC) foram convertidos com **LibreDWG 0.13.3**
(`dwgread -O JSON`) compilado no próprio ambiente, e as dimensões lidas dos
entes `DIMENSION_LINEAR` (`act_measurement`). Os DWF (Subsolo/Térreo/Cobertura/
Corte/Fachadas) são as mesmas pranchas plotadas (1:1000 / 1:100) — a fonte
métrica usada foi o DWG de model space (coordenadas reais).

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v110_BP_CALIBRADO.ifc` | Modelo BIM v110 (IFC4) calibrado + IfcGrid |
| `build_v110.py` | Construtor reprodutível (v108 → v110) |
| `HVG_Inhotim_v110_Calibracao_Planta_Oficial.md` | Este relatório |
| `referencias/v106_previews/v110_planta_grid_calibrado.png` | Planta + IfcGrid cotada |
| `referencias/v106_previews/v110_bloco_principal_3d.png` | Volumetria 3D calibrada |
