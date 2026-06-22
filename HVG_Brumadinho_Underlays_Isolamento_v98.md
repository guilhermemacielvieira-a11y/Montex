# HVG Brumadinho — Underlays: isolamento da planta + de-rotação automática (v98 consolidado)

**Base:** `HVG_MASTER_v95_corrigido.ifc` · **Entregue:** `HVG_MASTER_v98_underlays_iso.ifc` (IFC4, 49 MB)
**Data:** 22/06/2026 · Grupo Montex

Versão **consolidada e final** dos underlays, com o passo extra pedido:
isolar a planta nas folhas com cortes/detalhes e de-rotar o Bloco Principal automaticamente.

---

## 1. Isolamento da planta por janela de densidade (gabarito = footprint real)

Para cada folha que mistura **planta + cortes + detalhes**, o tamanho real do edifício (medido pela
geometria do v95, via iterador) é usado como **gabarito**: uma **janela de densidade** (soma de
comprimento de linhas, tabela de soma integral) desliza pela folha e trava na região mais densa do
tamanho da planta. Só essa região é mantida.

| Edifício | Método | Linhas antes → depois | Resultado |
|----------|--------|------------------------|-----------|
| **SPA** | isolado | 39.750 → **6.313** | planta isolada com precisão ✅ |
| **Boite** | isolado | 32.256 → 15.660 | cluster principal isolado (folha atípica de ~650 m) |
| **Guarita** | isolado | 62.451 → 58.592 | edifício mínimo (9,2 × 4,0 m); janela cobre quase tudo |
| Centro de Convenções | centro-a-centro | 5.593 | já limpo (planta única) |
| Restaurante da Piscina | centro-a-centro | 26.435 | já limpo |
| Clube NEP | centro-a-centro | 5.031 | já limpo |
| Bloco B (Térreo) | centro-a-centro | 111.449 | já limpo |
| Bloco B (1º Pav) | centro-a-centro | 26.526 | já limpo |

> O isolamento é aplicado só onde ajuda (folhas com cortes). Folhas de planta única são mantidas
> integralmente para não correr risco de cortar a planta.

## 2. De-rotação automática — Bloco Principal

O ângulo dominante de cada folha é estimado pelo histograma de orientação das linhas (ponderado por
comprimento, módulo 90°). Só o **Bloco Principal** apresentou rotação significativa:

- Ângulo detectado: **−41,8°** (as duas plantas do desenho original estão giradas ~45°).
- A folha é **de-rotada automaticamente** para alinhar aos eixos ortogonais do modelo, depois isolada
  e alinhada ao footprint. Resultado: a planta entra **ortogonal e centrada** no Bloco Principal —
  sem o giro de 45° que aparecia no v97.
- Registrado no PSet: `Metodo = isolado+de-rotado`, `RotacaoAplicada_graus = -41.8`.

## 3. Alinhamento ao footprint real

Após de-rotar/isolar, cada underlay é deslocado (translação 1:1 m) para que sua mediana coincida com
o **centro do bounding box real** do edifício, em coordenadas locais do pavimento. Verificação visual:
`HVG_v98_Underlays_Overlay.png` (underlay em azul × retângulo do footprint real em vermelho).

---

## 4. IFC consolidado (última versão)

| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| Georreferência | E 578.800 / N 7.773.500 / H 935 · EPSG:31983 ✅ |
| Underlays (`IfcAnnotation MTX-UNDERLAY-DXF`) | 9 ✅ |
| Camadas `MTX-Underlay-*` (travadas) | 9/9 ✅ |
| GUIDs únicos | Sim ✅ |
| Coordenadas inválidas | 0 ✅ |
| Entidades | 445.196 |
| Tamanho | 49 MB |

Cada underlay carrega o PSet `MTX_Underlay` com SourceDXF, Escala, CRS, Método e Rotação aplicada.

---

## 5. Arquivos entregues

| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v98_underlays_iso.ifc`** | **IFC consolidado final (underlays isolados/de-rotados)** |
| `HVG_underlays_georef_v98.zip` | 9 DXFs (planta isolada/de-rotada) em coords do modelo v95 |
| `HVG_underlays_transform_v98.csv` | Método, rotação, contagem e posição por edifício |
| `HVG_v98_Underlays_Overlay.png` | Verificação visual × footprint real |
| `align_isolate_v98.py` | Script reproduzível (isolamento + de-rotação + consolidação) |

---

## 6. Ressalva honesta

- **SPA** e **Bloco Principal** (de-rotação) tiveram o maior ganho.
- **Guarita** e **Boite** são folhas atípicas (edifício mínimo / desenho espalhado por ~650 m); o
  isolamento faz o melhor esforço, mas o registro fino permanece um ajuste de poucos cliques no
  Archicad — coerente com os protocolos PROT-001/002.
