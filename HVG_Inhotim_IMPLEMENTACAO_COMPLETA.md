# HVG Inhotim — Relatório Completo de Implementação BIM

## Modelo `HVG_MASTER_v123_APTOS_COBERTURA.ifc` — inspeção, verificação visual e reanálise

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — MG — Brasil · **Georref.:** SIRGAS 2000 / UTM 23S (EPSG:31983)
**Autoria:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Data:** 30/06/2026 · **Schema:** IFC4 · **Entidades:** 654.000 · **GlobalIds:** únicos

---

## 1. Sumário executivo

A partir do modelo "REALISTA" (v105) e dos **projetos oficiais em DWG** (planta de
situação, Bloco Principal, SPA, Convenções, Restaurante, Boite, Clube NEP, Guarita,
Apoio Quadras, Subestação e blocos de apartamentos A/B), o modelo foi:

1. **Calibrado** ao projeto executivo (Bloco Principal recalibrado pela planta
   oficial → 58,7 × 57 m, malha ~4,9 m, `IfcGrid`);
2. **Detalhado** internamente em **todos os 26 edifícios** (divisórias reais
   traçadas dos DWG, portas, ambientes, fachadas, acabamentos);
3. **Completado** verticalmente nos apartamentos (subsolos, térreo, 1º pav, e
   nível de cobertura com platibandas);
4. **Verificado** visualmente (planta geral + 3D de massas) e por inventário.

---

## 2. Verificação visual (inspeção do modelo)

- **Planta geral** (`referencias/inspecao_final/HVG_planta_geral_v123.png`):
  os 26 edifícios aparecem com **detalhamento interno** (paredes coloridas por
  edifício) nas posições corretas da implantação.
- **3D de massas** (`referencias/inspecao_final/HVG_massas_3d_v123.png`):
  volumetria coerente — Bloco Principal central, 12 blocos A e 4 blocos B (mais
  altos, com mais pavimentos), SPA, Convenções, Restaurante, Boite, Clube NEP.

**Resultado da conferência:** modelo **completo e coerente** em implantação,
volumetria e detalhamento interno.

---

## 3. Inventário por edifício (v123)

| Edifício | pil | par | por | jan | cw | laje | cob | mob | esp |
|----------|----:|----:|----:|----:|---:|----:|----:|----:|----:|
| **Bloco Principal** | 169 | 872 | 79 | 4 | 4 | 2 | 1 | 420 | 55 |
| **SPA** | 24 | 181 | 8 | 2 | — | 3 | 1 | — | 15 |
| Centro de Convenções | 50 | 251 | 20 | 2 | — | 1 | 1 | — | 5 |
| Restaurante da Piscina | 32 | 303 | 2 | 4 | — | 2 | 1 | — | 6 |
| Boite Soul & Blues | 32 | 48 | 1 | 2 | — | — | 1 | — | 5 |
| Clube NEP | 12 | 252 | 29 | 10 | — | 1 | 1 | — | 4 |
| Guarita | 6 | 10 | 1 | 6 | — | 1 | 1 | — | 2 |
| Apoio Quadras | — | 86 | 4 | — | — | 2 | — | — | 1 |
| Subestação | — | 86 | — | — | — | 2 | — | — | 1 |
| Central de Gás | — | 4 | — | — | — | 1 | — | — | 1 |
| **Bloco‑A‑01…12** (×12) | 28 | 502 | ~18 | 36 | — | 3 | 1 | ~95 | 72 |
| **Bloco‑B‑13…16** (×4) | 28 | 638 | 96 | 120 | — | 3 | 2 | ~128 | 96 |

*(pil=pilares · par=paredes · por=portas · jan=janelas · cw=curtain wall ·
laje=slabs · cob=roofs · mob=mobiliário · esp=espaços)*

**Totais:** 7.597 paredes · 747 portas · 942 janelas · 4 fachadas‑cortina ·
1.352 espaços · 773 pilares · 31 coberturas · 2.276 mobiliário · 76 pavimentos.

---

## 4. Metodologia (reprodutível)

| Etapa | Ferramenta / script |
|-------|---------------------|
| Conversão DWG (AutoCAD 2018/AEC) → JSON | **LibreDWG 0.13.3** compilado no ambiente (`dwgread -O JSON`) |
| Leitura tolerante (`-nan`, latin‑1) | `load_dwgjson.py` |
| Isolamento de paredes por camada + mapeamento ao footprint | `detail_lib.py` (de‑rotação por ângulo dominante, ajuste de eixos, escala) |
| Autoria IFC (geometria, placement, material, relações) | IfcOpenShell 0.8.5 |
| Construtores por revisão | `build_v106.py` … `build_v123.py` |
| Auditoria foto × modelo | `audit_foto_x_modelo.py` |

Cada edifício teve as linhas de parede (camadas variáveis: `PAR`/`PAR1`/
`Alvenaria`/`VERM`/`Par1`/`ALVENARIA`/`SPA_ALVENARIA`) extraídas do DWG,
de‑rotacionadas e mapeadas ao envelope do edifício no modelo.

---

## 5. Reanálise de refinamentos restantes

| # | Refinamento | Relevância | Viabilidade |
|---|-------------|:----------:|-------------|
| 1 | **Git LFS** (concluir upload) | Alta (operacional) | ✅ na máquina do usuário (`scripts/setup_git_lfs.sh`) — ambiente bloqueia `lfs.github.com` |
| 2 | **Janelas dos edifícios secundários** | Média | ⚠️ camada de esquadria esparsa/só‑legenda nos DWG — exigiria ler a *tabela de esquadrias* (V1/V2) e cruzar com paredes |
| 3 | **Recorte poligonal dos `IfcSpace`** pelas divisórias | Média | Viável — reconstruir polígono de cada ambiente a partir das paredes (atualmente espaços dimensionados por área) |
| 4 | **Piscinas exteriores / Copa de apoio** | Média‑baixa | Requer mapeamento em coordenadas de implantação (site); piscinas já representadas como `IfcCovering` |
| 5 | **Programa de ambientes** de Convenções/Restaurante/Apartamentos | Média | ⚠️ DWG sem rótulos de área (`A=`); usar nomes existentes + recorte por divisórias |
| 6 | **Calibração dimensional** dos footprints dos secundários | Baixa | Como no Bloco Principal (v110) — hoje mapeados ao envelope existente |
| 7 | **Vidros/clerestório** dos demais (SPA, Restaurante rooftop) | Baixa | Modelável onde houver pano de vidro no projeto |
| 8 | **4D/5D** (vincular `BaseQuantities` a cronograma/orçamento) | Estratégica | Próxima fase de uso do modelo |
| 9 | **IDS / model‑checking** automatizado | Estratégica | Fixar requisitos de informação e validar a cada revisão |

**Recomendação:** o modelo atingiu um **LOD 300+ coerente em todo o resort**
(estrutura, vedação interna, esquadrias principais, coberturas e acabamentos no
Bloco Principal). Os refinamentos remanescentes são **incrementais** e a maioria
**limitada pela anotação dos DWG** (esquadrias/áreas), não pela modelagem.
Itens de maior valor agregado a seguir: **(3) recorte poligonal dos espaços** e
**(8/9) preparação 4D/5D + IDS**.

---

## 6. Arquivos

Modelos `HVG_MASTER_v106…v123.ifc`; relatórios por revisão `HVG_Inhotim_v1xx_*.md`;
relatório‑mestre `HVG_Inhotim_RELATORIO_MESTRE.md`; construtores `build_v1xx.py`;
biblioteca `detail_lib.py` / `load_dwgjson.py`; referências em `referencias/`
(deck fotográfico, previews por revisão, inspeção final).
