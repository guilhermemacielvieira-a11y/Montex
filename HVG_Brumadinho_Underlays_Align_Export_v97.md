# HVG Brumadinho — Underlays: alinhamento fino + DXFs georreferenciados (v96 → v97)

**Base:** `HVG_MASTER_v95_corrigido.ifc` · **Entregue:** `HVG_MASTER_v97_underlays_align.ifc` (IFC4, 52 MB)
**Data:** 22/06/2026 · Grupo Montex

Atende às duas frentes pedidas:
**(a)** alinhar cada underlay ao **centro do footprint real** do respectivo edifício;
**(b)** exportar os **DXFs já transladados para o sistema do v95**, prontos para o **Merge no Archicad**.

---

## (a) Alinhamento fino ao footprint real

O footprint de cada pavimento foi medido pela **geometria real** (bounding box via iterador de
geometria do ifcopenshell, 920 elementos, 1,3 s) — e **não** pelas origens de placement, que no v95
ficam quase todas em (0,0) e não representam a posição do elemento.

- Alvo de alinhamento = **centro do bounding box** do edifício, em coordenadas locais do pavimento.
- Fonte = **mediana robusta** das linhas do underlay (após filtro de outliers).
- Transformação = **apenas translação** (1:1 m, sem escala): a folha é deslocada para que sua mediana
  coincida com o centro do edifício.

### Footprints reais medidos (tamanho do volume LOD 200)
| Edifício | Tamanho real (m) | Centro local do pavimento |
|----------|------------------|----------------------------|
| Guarita | 9,2 × 4,0 | (0,00; 0,00) |
| Centro de Convenções | 47,1 × 18,3 | (0,00; 0,00) |
| Restaurante da Piscina | 34,8 × 14,9 | (0,00; 0,00) |
| Clube NEP | 17,8 × 8,0 | (0,00; 0,00) |
| SPA | 51,7 × 14,4 | (13,35; 0,00) |
| Boite | 35,6 × 16,0 | (0,00; 0,00) |
| Bloco Principal | 79,7 × 79,7 | (0,00; 0,00) |
| Bloco B (13) | 25,4 × 22,1 | (0,03; 0,00) |

### Qualidade do alinhamento (ver `HVG_v97_Underlays_Overlay.png`)
- **Bom encaixe automático** (planta predominante): Centro de Convenções, Restaurante da Piscina,
  Clube NEP, Bloco B (Térreo e 1º Pav).
- **Requer ajuste fino manual** (folhas com muitos cortes/tabelas, ou planta rotacionada):
  - **Guarita / SPA / Boite** — a folha mistura planta + cortes + detalhes; a mediana não isola a
    planta com precisão. O modelador desliza o underlay para o encaixe exato.
  - **Bloco Principal** — duas plantas giradas **~45°**; separar e rotacionar no Archicad
    (manifesto PROT-002). O alinhamento aqui apenas centraliza a folha sobre o edifício.

> Isto é consistente com os protocolos: o registro fino por planta é, por definição, um passo de
> modelagem ("posicione/confirme em cada piso" — PROT-002 §3.4). O ganho do v97 é levar cada folha
> ao **centro do edifício certo**, reduzindo o deslize necessário.

O IFC v97 mantém os 9 underlays como `IfcAnnotation` em **camadas `MTX-Underlay-*` travadas**, agora
com a propriedade `Alinhamento = centro-a-centro (footprint real v95)` no PSet `MTX_Underlay`.

---

## (b) DXFs georreferenciados para o Archicad

Cada underlay foi reescrito em **coordenadas do sistema do modelo v95** (engineering/local, onde os
edifícios já estão posicionados), **preservando todas as camadas originais**. Basta importar via
**Merge** com a **origem do projeto = origem do v95 (EPSG:31983, E 578.800 / N 7.773.500)** e a folha
cai sobre o edifício — sem cálculo de offset.

Pacote: **`HVG_underlays_georef_v97.zip`** (9 DXFs) · tabela: **`HVG_underlays_transform_v97.csv`**

| DXF de saída | Edifício | Posição no modelo (X,Y) | Camadas |
|--------------|----------|--------------------------|---------|
| HVG_Guarita_underlay_georef.dxf | Guarita | 320 / 215 | 5 |
| HVG_CentroConvencoes_underlay_georef.dxf | Centro de Convenções | 290 / 270 | 17 |
| HVG_RestaurantePiscina_underlay_georef.dxf | Restaurante da Piscina | 70 / 225 | 29 |
| HVG_ClubeNEP_underlay_georef.dxf | Clube NEP | 40 / 300 | 10 |
| HVG_SPA_underlay_georef.dxf | SPA | 80 / 270 | 42 |
| HVG_Boite_underlay_georef.dxf | Boite | 240 / 175 | 36 |
| HVG_BlocoPrincipal_underlay_georef.dxf | Bloco Principal | 165 / 245 | 47 |
| HVG_BlocoB_Terreo_underlay_georef.dxf | Bloco B (Térreo) | 110 / 130 | 10 |
| HVG_BlocoB_Pav1_underlay_georef.dxf | Bloco B (1º Pav) | 110 / 130 | 12 |

Sanity-check confirmou que a mediana de cada DXF coincide com a posição do edifício no modelo.

---

## Validação

| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| Georreferência preservada | E 578.800 / N 7.773.500 / H 935 · EPSG:31983 ✅ |
| Underlays / camadas travadas | 9 / 9 ✅ |
| GUIDs únicos | Sim ✅ |
| Entidades | 451.425 |
| DXFs georreferenciados (camadas preservadas) | 9 ✅ |

---

## Arquivos entregues

| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v97_underlays_align.ifc`** | IFC com underlays alinhados ao footprint real |
| **`HVG_underlays_georef_v97.zip`** | 9 DXFs em coords do modelo v95 (prontos p/ Merge) |
| `HVG_underlays_transform_v97.csv` | Posições/translações aplicadas por edifício |
| `HVG_v97_Underlays_Overlay.png` | Verificação visual do alinhamento |
| `align_and_export.py` | Script reproduzível (alinhamento + exportação) |
| `HVG_Brumadinho_Underlays_Align_Export_v97.md` | Este relatório |
