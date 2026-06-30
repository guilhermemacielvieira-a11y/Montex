# HVG Inhotim — Revisão v112

## Paredes de compartimentação (divisórias) internas do Bloco Principal

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v110_BP_CALIBRADO.ifc`
**Entregue:** `HVG_MASTER_v112_DIVISORIAS.ifc`
**Fonte oficial:** `031 - Bloco Principal - Plantas.dwg` (camadas *Alvenaria / PAR / PAR1*)
**Data:** 30/06/2026

---

## 1. Objetivo

Subir o LOD dos pavimentos (após o programa de ambientes da v111), modelando as
**paredes de compartimentação internas reais** de cada pavimento, traçadas da
planta oficial.

---

## 2. Método

1. **Decodificação das camadas** do DWG (handle → nome): identificadas as camadas
   de parede **`Alvenaria`** (932 linhas) + **`PAR1`** (260) + **`PAR`** (60).
2. **Extração** das linhas dessas camadas, por pavimento (Subsolo / Térreo).
3. **De‑rotação** do edifício (ângulo dominante **48°**) e **mapeamento 1:1**
   (rotação + translação, escala 1,0 — pois o footprint já está calibrado em
   58,7 × 57 m) para o centro do Bloco Principal no modelo (165, 245).
4. **Criação** de cada segmento como `IfcWall` (PredefinedType=`PARTITIONING`,
   espessura 0,15 m, altura = pé‑direito ~2,8 m do corte 032).
5. **Reposicionamento** dos 55 ambientes (`IfcSpace`) pelo **mesmo transform**,
   alinhando‑os às divisórias.

---

## 3. O que foi modelado (v112)

| Pavimento | Paredes‑divisória (`IfcWall PARTITIONING`) | Ambientes (`IfcSpace`) |
|-----------|:------------------------------------------:|:----------------------:|
| Subsolo | **520** | 32 (2.083 m²) |
| Térreo | **348** | 23 (1.103 m²) |
| **Total** | **868** | **55** |

- Material das divisórias: *Alvenaria Bloco Cerâmico Rebocado*.
- Layout fiel à planta: Subsolo com o núcleo denso de serviço (cozinhas, câmaras,
  rouparias, vestiários) + hall de restaurante aberto; Térreo com o cluster de
  gabinetes/lojas, o conjunto de WCs/bar e o Lobby aberto.

> Previews: `referencias/v112_divisorias/v112_divisorias_por_pavimento.png`
> (paredes no modelo, render do IFC) e `v112_paredes_planta_oficial.png`
> (paredes extraídas/mapeadas da planta oficial).

---

## 4. Validação do entregável (v112)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 516.008 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| `IfcWall` (total no modelo) | 2.228 (+868 divisórias do BP) |
| Geometria das divisórias (render) | **868/868 válidas (0 erros)** |
| Ambientes do BP | 55 (alinhados às divisórias) |
| Calibração v110 (footprint, IfcGrid, pilares) | preservada |
| SPA / cenografia / demais edifícios | inalterados |

---

## 5. Notas de LOD e próximos passos

- As divisórias estão como **paredes de partição** ao nível do pé‑direito; portas
  e vãos por ambiente (`IfcDoor` + `IfcOpeningElement`/`IfcRelVoidsElement`)
  são o próximo refinamento — extraíveis da camada `ESQUADRIA` da mesma planta.
- Os ambientes (`IfcSpace`) continuam como volumes esquemáticos dimensionados por
  área; um refinamento adicional é recortar o footprint de cada ambiente pelo
  polígono real das divisórias que o cercam.
- A camada `MOB`/`Equipamento`/`Loiças` traz mobiliário e louças sanitárias —
  passível de inclusão como `IfcFurniture`/`IfcSanitaryTerminal` se desejado.

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v112_DIVISORIAS.ifc` | Modelo BIM v112 com as divisórias internas |
| `build_v112.py` | Construtor reprodutível (v110 → v112) |
| `HVG_Inhotim_v112_Divisorias.md` | Este relatório |
| `referencias/v112_divisorias/v112_divisorias_por_pavimento.png` | Divisórias no modelo (render IFC) |
| `referencias/v112_divisorias/v112_paredes_planta_oficial.png` | Paredes mapeadas da planta oficial |
