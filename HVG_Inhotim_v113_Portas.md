# HVG Inhotim — Revisão v113

## Portas (esquadrias) internas do Bloco Principal

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v112_DIVISORIAS.ifc`
**Entregue:** `HVG_MASTER_v113_PORTAS.ifc`
**Fonte oficial:** `031 - Bloco Principal - Plantas.dwg` (camada *ESQUADRIA*)
**Data:** 30/06/2026

---

## 1. Objetivo

Após as divisórias (v112), modelar as **portas internas** dos pavimentos com
abertura real na parede — fechando o ciclo parede → vão → folha.

---

## 2. Método

1. **Detecção das portas** pela geometria de abertura: os **arcos da camada
   `ESQUADRIA`** (centro = dobradiça, raio = largura da folha) — 91 portas, com
   larguras de 0,70 / 0,80 / 0,90 / 1,00 m.
2. **Mapeamento 1:1** (de‑rotação 48° + translação) ao footprint calibrado.
3. Para cada porta, **localização da parede‑divisória hospedeira** (mais próxima,
   ≤ 1,5 m) das 868 paredes da v112.
4. Criação da **abertura** `IfcOpeningElement` que **vaza a parede**
   (`IfcRelVoidsElement`) e da **`IfcDoor`** que a **preenche**
   (`IfcRelFillsElement`), no frame local da parede (largura real × altura 2,10 m).

---

## 3. O que foi modelado (v113)

| Pavimento | Portas (`IfcDoor` + vão) |
|-----------|:------------------------:|
| Subsolo | **41** |
| Térreo | **37** |
| **Total** | **78** |

- Cada porta: `OverallWidth` real (0,7–1,0 m), `OverallHeight` 2,10 m,
  `OperationType` SINGLE_SWING_LEFT, com vão correspondente abrindo a alvenaria.
- As **13 portas restantes** (91 − 78) ficam em fachadas envidraçadas/perímetro
  (fora da camada de alvenaria) e não foram hospedadas nas divisórias internas —
  pertencem ao sistema de fachada (envidraçados), tema da camada de esquadria
  externa.

> Preview: `referencias/v113_portas/v113_portas_terreo.png` (paredes do Térreo +
> portas em vermelho — concentradas nos clusters de gabinetes e de WCs/bar, com
> o Lobby aberto sem portas).

---

## 4. Validação do entregável (v113)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 518.194 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| `IfcDoor` novas | **78** (com geometria válida, 0 erros) |
| Vãos novos (`IfcOpeningElement` "Vao-Porta") | 78 |
| `IfcRelVoidsElement` / `IfcRelFillsElement` novos | 78 / 78 |
| Divisórias (v112) + calibração (v110) | preservadas |
| SPA / cenografia / demais edifícios | inalterados |

---

## 5. Próximos passos de LOD (camada ESQUADRIA / fachadas)

- **Janelas e envidraçados de fachada**: as fachadas do Bloco Principal são
  totalmente envidraçadas (`IfcCurtainWall`/`IfcWindow`) — modeláveis a partir
  das linhas de esquadria externa e dos panos de vidro.
- **Folhas e marcos detalhados** (atualmente folha simples): tipologias de porta
  (`IfcDoorType`) com marco/alizar.
- **Mobiliário e louças** (camadas `MOB`/`Loiças`) → `IfcFurniture`/`IfcSanitaryTerminal`.

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v113_PORTAS.ifc` | Modelo BIM v113 com as portas internas |
| `build_v113.py` | Construtor reprodutível (v112 → v113) |
| `HVG_Inhotim_v113_Portas.md` | Este relatório |
| `referencias/v113_portas/v113_portas_terreo.png` | Portas do Térreo (preview) |
