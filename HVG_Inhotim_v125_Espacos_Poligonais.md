# HVG Inhotim — Revisão v125

## Recorte poligonal dos ambientes (`IfcSpace` com contorno real)

**Modelo base:** `HVG_MASTER_v124_BAR_PISCINA.ifc` → **Entregue:** `HVG_MASTER_v125_ESPACOS_POLIGONAIS.ifc`
**Autoria:** Guilherme Maciel — Grupo Montex Ltda · **Data:** 30/06/2026 · **Schema:** IFC4

---

## 1. Objetivo

Substituir os `IfcSpace` **quadrados** (dimensionados pela área de planilha,
geometria nominal) do **Bloco Principal** (Subsolo + Térreo) e do **SPA**
(Térreo) por **espaços com contorno poligonal real**, que **tesselam**
(preenchem sem sobreposição e sem vazios) a placa de cada pavimento.

---

## 2. Por que não recortar pelos *loops* das paredes

A hipótese inicial — reconstruir o polígono de cada sala a partir das paredes
isoladas por camada (`polygonize`) — foi **testada e descartada por evidência**:

| Teste | Resultado |
|-------|-----------|
| SPA — paredes mapeadas ao modelo (`polygonize`) | 0 salas; placa permanece **1 polígono** |
| SPA — paredes em coordenadas nativas do DWG | idem (footprint de ~557 m² não se subdivide) |
| Bloco Principal — paredes nativas (Subsolo/Térreo) | 1 região conectada de ~4.033 m²; `polygonize`→ 0 |
| Fechamento de vãos por *buffer* (0,05–0,30 m) | insuficiente: vãos de porta (~0,8–0,9 m) uniriam salas |

**Causa:** as paredes dos DWG são linhas de **face** com **vãos sistemáticos**
(portas, encontros) — **nunca formam células fechadas**. Forçar `polygonize`
produziria um único bloco, **pior** que os espaços por área atuais.

---

## 3. Método adotado — partição de Voronoi (Thiessen) por ambiente

Em vez de *loops* de parede frágeis, particiona-se a **placa calibrada** de
cada pavimento por **diagrama de Voronoi**, semeado no **centroide real de cada
ambiente** (posição lida da planta oficial):

1. **Sementes** = centroides dos ambientes (Bloco Principal: 55 rótulos com área
   e posição da planta; SPA: 15 rótulos `A=…m²`), mapeados ao footprint do modelo.
2. **Voronoi** (`shapely.voronoi_polygons`) → cada ponto recebe a região da placa
   **mais próxima** dele; a fronteira entre dois ambientes vizinhos **aproxima a
   divisória** entre eles.
3. **Recorte** de cada célula à placa do pavimento → polígono real.
4. **Autoria** como `IfcSpace` com `IfcArbitraryClosedProfileDef` extrudado
   (pé-direito do pavimento).

Cada espaço guarda a **área geométrica real** (`GrossFloorArea`,
`GrossPerimeter` em `Qto_SpaceBaseQuantities`) **e** a **área de planilha** do
projeto (`Pset_SpaceCommon.GrossPlannedArea`) — rastreabilidade preservada.

> Nota: o Voronoi reparte **toda** a placa entre os ambientes nomeados (incluindo
> a quota de circulação/paredes adjacente a cada sala); por isso a área
> geométrica supera a área de planilha — esta fica registrada na propriedade.

---

## 4. O que foi entregue (v125)

| Pavimento | Ambientes poligonais | Cobertura da placa |
|-----------|:--------------------:|:------------------:|
| **BP — Subsolo** | 32 | 3.346 / 3.346 m² (100 %) |
| **BP — Térreo** | 23 | 3.346 / 3.346 m² (100 %) |
| **SPA — Térreo** | 15 | 317 / 317 m² (100 %) |
| **Total** | **70** | tesselagem sem vazios/sobreposição |

Preview: `referencias/v125_espacos/v125_espacos_poligonais.png` — layout legível
de ambientes nomeados (RESTAURANTE, REFEITÓRIO, LOBBY, BAR, PISCINA, MASSAGENS…)
particionando cada placa.

---

## 5. Validação

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 654.806 |
| GlobalIds únicos | **Sim** |
| Geometria dos espaços poligonais | **71/71** válida (IfcOpenShell) |
| Alinhamento com paredes (X/Y) | BP ±29 m e SPA ±12/±6,6 m — coincidem |
| `IfcSpace` (total no modelo) | 1.352 (70 recortados; demais preservados) |

---

## 6. Alcance e limitação

- **Aplicável** onde há rótulos de ambiente com **posição** na planta: Bloco
  Principal e SPA (feito). Generalizável a outros edifícios **assim que** houver
  rótulos de ambiente posicionados (Convenções/Restaurante/Apartamentos não
  trazem rótulos de área `A=` nos DWG — limitação de anotação, já registrada).
- O contorno é a **melhor aproximação principiada** das divisórias a partir dos
  dados disponíveis; não substitui um *space boundary* extraído de paredes
  fechadas (inexistentes nos DWG).

---

## 7. Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v125_ESPACOS_POLIGONAIS.ifc` | Modelo BIM v125 |
| `build_v125.py` · `detail_lib.py` | Construtor + biblioteca |
| `HVG_Inhotim_v125_Espacos_Poligonais.md` | Este relatório |
| `referencias/v125_espacos/v125_espacos_poligonais.png` | Preview da partição |
