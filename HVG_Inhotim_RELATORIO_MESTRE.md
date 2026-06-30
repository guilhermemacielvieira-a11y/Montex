# HVG Inhotim — Relatório‑Mestre do Modelo BIM

## Índice consolidado das revisões e do detalhamento por edifício

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil · **Georref.:** SIRGAS 2000 / UTM 23S (EPSG:31983)
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo atual:** `HVG_MASTER_v122_APTOS_PAVIMENTOS.ifc` (IFC4) · **Data:** 30/06/2026

---

## 1. Estado quantitativo do modelo (v122)

| Entidade | Qtd | Entidade | Qtd |
|----------|----:|----------|----:|
| Entidades totais | **607.103** | `IfcWall` | 7.597 |
| `IfcBuilding` | 26 | `IfcDoor` / `IfcWindow` | 747 / 942 |
| `IfcBuildingStorey` | 60 | `IfcCurtainWall` / `IfcPlate` | 4 / 8 |
| `IfcSpace` | 1.352 | `IfcColumn` / `IfcBeam` / `IfcMember` | 773 / 492 / 663 |
| `IfcRoof` / `IfcSlab` | 31 / 375 | `IfcStair` / `IfcRailing` | 21 / 83 |
| `IfcFurniture` | 2.276 | `IfcSanitaryTerminal` / `IfcGrid` | 6 / 2 |

Schema **IFC4** válido · GlobalIds únicos · georreferenciado.

---

## 2. Linha do tempo das revisões

| Versão | Entrega |
|--------|---------|
| v105 | Modelo base "REALISTA" recebido (interiores detalhados) |
| **v106** | Estruturas de cobertura aparentes: **tesouras de madeira do SPA** + **treliça espacial da recepção** |
| v107 | Cobertura do Bloco Principal: hip de baixa inclinação + beiral profundo |
| v108 | Cenografia de lazer: parque aquático infantil + pista de carros |
| v109 | (Reestruturação retangular — substituída pela v110) |
| **v110** | **Calibração do Bloco Principal pela planta oficial (DWG) + `IfcGrid`** (58,7×57, malha ~4,9 m, 169 pilares) |
| v111 | Programa de ambientes do BP (55 `IfcSpace` com áreas) |
| v112 | Divisórias internas do BP (868 paredes, traçadas do DWG) |
| v113 | Portas internas do BP (78, com vãos) |
| v114 | Fachadas envidraçadas do BP (4 `IfcCurtainWall`) |
| v115 | Clerestório + guarda‑corpos + mobiliário (420) + louças do BP |
| v116 | Divisórias do **Centro de Convenções** (247) + **Restaurante da Piscina** (295) |
| v117 | Divisórias do **Térreo** dos 16 **blocos de apartamentos** (2.340) |
| v118 | Divisórias do **SPA** (173) |
| v119 | Divisórias dos menores: Boite, Clube NEP, Guarita, Apoio Quadras, Subestação (462) |
| v120 | Programa de ambientes do **SPA** (15 `IfcSpace`) |
| v121 | **Portas** dos demais edifícios por detecção de vãos (62) |
| v122 | Demais **pavimentos dos apartamentos** (subsolos / 1º pav — 1.856 paredes) |

---

## 3. Detalhamento por edifício

| Edifício | Calib.+Grid | Ambientes | Divisórias | Portas | Fachadas | Acabamentos |
|----------|:----------:|:---------:|:----------:|:------:|:--------:|:-----------:|
| **Bloco Principal** | ✅ | ✅ | ✅ | ✅ | ✅ envidraçada | ✅ clerestório, guarda‑corpos, mobiliário, louças |
| **SPA** | — | ✅ | ✅ | ✅ | — | tesouras de madeira (cobertura) |
| **Centro de Convenções** | — | (modelo) | ✅ | ✅ | — | — |
| **Restaurante da Piscina** | — | (modelo) | ✅ | ✅ | — | — |
| **Apartamentos A (12)** | — | — | ✅ (3 pav) | ✅ | — | — |
| **Apartamentos B (4)** | — | — | ✅ (3 pav) | ✅ | — | — |
| **Boite Soul & Blues** | — | (modelo) | ✅ | ✅ | — | — |
| **Clube NEP** | — | (modelo) | ✅ | ✅ | — | — |
| **Guarita / Apoio Quadras / Subestação** | — | (modelo) | ✅ | ✅ | — | — |

"(modelo)" = espaços genéricos já presentes no v105.

---

## 4. Método e ferramentas (reprodutível)

- **Leitura de CAD:** **LibreDWG 0.13.3** compilado no ambiente (`dwgread -O JSON`)
  para converter os DWG (AutoCAD 2018/AEC) — `load_dwgjson.py` (tolerante a `-nan`).
- **Pipeline genérico:** `detail_lib.py` — isola camadas de parede, de‑rotaciona
  (ângulo dominante) e mapeia 1:1 / por ajuste ao footprint do edifício no modelo.
- **Autoria IFC:** IfcOpenShell 0.8.5 — geometria por `IfcExtrudedAreaSolid` /
  `IfcFacetedBrep`, com placement, material e relações (contenção, vãos, fills).
- **Construtores por revisão:** `build_v106.py` … `build_v122.py` (cada um
  reprodutível a partir da versão anterior).
- **Auditoria:** `audit_foto_x_modelo.py` (confronto com o deck fotográfico).

---

## 5. Pendências e notas

| Item | Situação |
|------|----------|
| **Git LFS** | Preparado (`scripts/setup_git_lfs.sh` + `docs/Git_LFS_Migracao.md`); concluir na máquina do usuário — o ambiente bloqueia `lfs.github.com` |
| **Janelas dos secundários** | Camada de esquadria esparsa/só‑legenda nos DWG — não extraível de forma fiel |
| **Cobertura dos apartamentos** | Plano de telhado (pode ser adicionado como `IfcRoof` por bloco) |
| **Piscinas exteriores / Copa de apoio** | DWG recebidos; requerem mapeamento em coordenadas de implantação (site) |
| **Espaços poligonais** | Os `IfcSpace` estão dimensionados por área; recorte pelo polígono das divisórias é evolução possível |

---

## 6. Arquivos por revisão (no repositório)

Modelos `HVG_MASTER_v106…v122.ifc`; relatórios `HVG_Inhotim_v1xx_*.md`;
construtores `build_v1xx.py`; biblioteca `detail_lib.py`; referências em
`referencias/` (deck fotográfico, previews por revisão).
