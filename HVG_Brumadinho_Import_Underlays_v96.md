# HVG Brumadinho — Importação dos Underlays DXF no IFC (v95 → v96)

**Modelo de entrada:** `HVG_MASTER_v95_corrigido.ifc`
**Modelo entregue:** `HVG_MASTER_v96_underlays.ifc` (IFC4, 51 MB)
**Insumos:** `HVG_underlays_DXF.zip` + protocolos **MTX-BIM-HVG-PROT-001** (LOD 300) e **MTX-BIM-HVG-PROT-002** (Plano de Importação) + `HVG_pacote_importacao_Archicad.zip`
**Data:** 22/06/2026 · Grupo Montex

---

## 1. O que foi feito

Os **8 underlays DXF** (planta/cortes limpos) foram **importados e georreferenciados diretamente
no IFC v95**, conforme as **coordenadas do relatório** e o **manifesto** `import_manifest.csv`
(PROT-002). Cada underlay foi embutido como **`IfcAnnotation` 2D**, contido no **pavimento correto**,
sobre uma **camada `MTX-Underlay-*` travada**, posicionado na **origem compartilhada
EPSG:31983 (E 578.800 / N 7.773.500 / H 935)** que o IFC já carrega no `IfcMapConversion`.

> O PROT-002 deixa claro que o Archicad **não pode ser operado remotamente**. Esta entrega faz
> exatamente o que o pacote manual não consegue automatizar: **traz os underlays para dentro do
> modelo federado**, georreferenciados, prontos para o traçado LOD 300.

---

## 2. Mapeamento aplicado (fonte: `import_manifest.csv`)

Para os dois edifícios multi-planta (Bloco Principal e Bloco B) foram usadas as **regiões já
separadas** do pacote, como manda o manifesto — não as folhas DXF cruas.

| Underlay (DXF) | Edifício | Pavimento (v95) | Linhas (orig→úteis) | Polilinhas | Esc. |
|----------------|----------|------------------|---------------------|-----------|------|
| 02.dxf | Guarita | H1-Terreo | 62.628 → 62.451 | 11.784 | 1:50 |
| 05.dxf | Centro de Convenções | CC-Terreo | 5.633 → 5.593 | 532 | 1:100 |
| 06.dxf | Restaurante da Piscina | RP-Terreo | 26.444 → 26.435 | 2.289 | 1:100 |
| 09.dxf | Clube NEP | NEP-Terreo | 5.031 → 5.031 | 499 | 1:100 |
| 13.dxf | SPA | SPA-Terreo | 39.954 → 39.750 | 2.803 | 1:100 |
| 04.dxf | Boite | BOITE-Terreo | 32.256 → 32.256 | 2.372 | 1:100 |
| BlocoPrincipal_R1_…Cobertura.dxf | Bloco Principal | BP-Terreo | 205.390 → 204.492 | 11.766 | 1:100 |
| BlocoB_R1_Planta_1.dxf | Bloco B | B13-Terreo | 111.451 → 111.449 | 21.328 | 1:100 |
| BlocoB_R2_…1_PAVIMENTO.dxf | Bloco B | B13-Pav1 | 26.529 → 26.526 | 2.510 | 1:100 |

---

## 3. Método (georreferência e processamento)

1. **Leitura** das entidades `LINE` de cada DXF (unidade = metros, `INSUNITS=6`).
2. **Filtro de outliers** (percentil 0,5–99,5 + margem) — remove geometria-lixo dispersa
   (ex.: o DXF do Bloco Principal tinha pontos perdidos inflando as extensões a ~9.000 km).
3. **Translado** do canto inferior-esquerdo (robusto) para a **origem local do pavimento**,
   coincidente com a origem compartilhada do IFC v95 → o underlay federa **sem deslocamento**.
4. **Encadeamento** de segmentos contíguos (dedup de pontos a 1 mm) em **polilinhas** —
   reduziu ~514 mil linhas para **~55 mil polilinhas**, mantendo o arquivo enxuto.
5. **Geometria compacta** no IFC: um `IfcCartesianPointList3D` compartilhado por edifício +
   `IfcIndexedPolyCurve` por polilinha, num `IfcShapeRepresentation` (subcontexto `Annotation`,
   `PLAN_VIEW`).
6. **Anotação**: `IfcAnnotation` (`ObjectType = MTX-UNDERLAY-DXF`), `IfcLocalPlacement` relativo
   ao pavimento, contida via `IfcRelContainedInSpatialStructure`.
7. **Camada travada**: `IfcPresentationLayerWithStyle` `MTX-Underlay-<edifício>`
   (`LayerOn=True`, `LayerFrozen=True`, `LayerBlocked=True`).
8. **Rastreabilidade**: PSet `MTX_Underlay` em cada anotação (SourceDXF, Manifest, Escala, CRS, Observação).

---

## 4. Validação do IFC v96

| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| Georreferência preservada | E 578.800 / N 7.773.500 / H 935 · EPSG:31983 ✅ |
| Underlays embutidos (`IfcAnnotation MTX-UNDERLAY-DXF`) | **9** ✅ |
| Camadas `MTX-Underlay-*` (todas travadas) | **9** ✅ |
| Contenção espacial (1 underlay por pavimento alvo) | 9/9 ✅ |
| GUIDs únicos | Sim ✅ |
| Coordenadas inválidas (NaN/∞) | **0** ✅ |
| Entidades totais | 451.452 (era 395.433) |
| Tamanho do arquivo | 51 MB (era 25 MB) |

Verificação visual: `HVG_v96_Underlays_Overlay.png` — underlays (azul) sobre os elementos do
v95 (vermelho), em coordenadas locais do modelo, confirmando posicionamento no pavimento certo e
escala métrica 1:1.

---

## 5. O que permanece como passo manual (conforme PROT-001/002)

- **Registro fino por planta**: o ajuste exato de posição é um passo de modelagem
  ("posicione/confirme em cada piso" — PROT-002 §3.4). Os underlays entram na origem do
  pavimento; o modelador desliza para o encaixe exato.
- **Bloco Principal**: a região contém **2 plantas giradas ~45°** (térreo + subsolo). Devem ser
  **separadas e rotacionadas** no Archicad (PROT-002, manifesto).
- **Isolamento de planta** em folhas que trazem planta + cortes (02, 13, 04): o traçado LOD 300
  usa a planta; os cortes ficam como referência lateral na mesma camada.
- **Modelagem LOD 300** (paredes/portas/janelas/zonas) e validação IDS 6/6 antes de federar —
  fluxo do PROT-001 §2.2–2.3.

---

## 6. Arquivos entregues

| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v96_underlays.ifc`** | **IFC v95 + 9 underlays DXF georreferenciados (camadas travadas)** |
| `HVG_v96_Underlays_Overlay.png` | Verificação visual underlay × v95 |
| `HVG_import_manifest.csv` | Manifesto de importação (PROT-002) |
| `embed_underlays.py` | Script de importação/embute reproduzível |
| `verify_overlay.py` | Script de verificação visual |
| `HVG_Brumadinho_Import_Underlays_v96.md` | Este relatório |
