# HVG Inhotim — Revisão v111

## Detalhamento dos pavimentos do Bloco Principal (Subsolo + Térreo) pela planta oficial

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v110_BP_CALIBRADO.ifc`
**Entregue:** `HVG_MASTER_v111_PAVIMENTOS.ifc`
**Fontes oficiais:** `031 - Bloco Principal - Plantas.dwg` (programa) ·
`032 - Bloco Principal - Cortes e Fachadas.dwg` (níveis/alturas) — via LibreDWG
**Data:** 30/06/2026

---

## 1. Objetivo

Após a calibração estrutural (v110), **detalhar os pavimentos** do Bloco
Principal com o **programa real de ambientes** lido da planta oficial, e
**conferir os níveis/alturas com o corte e as fachadas** (032).

---

## 2. Programa de ambientes (planta 031)

As três plantas (Subsolo, Térreo, Cobertura) foram isoladas no model space e
os rótulos `AMBIENTE A=___m²` extraídos com posição. A Cobertura é o plano de
telhado (sem ambientes). Render das plantas reais em
`referencias/v111_pavimentos/031_planta_subsolo.png` e `031_planta_terreo.png`.

### 2.1 Subsolo — **32 ambientes · 2.083 m²** (núcleo de serviço)
Restaurante Versátil (682,89 m²) · Área de Buffet's e Show‑cooking's (267,63) ·
Restaurante (176,78 / 86,44) · Lavandaria (155,06) · Circulação (134,80) ·
Refeitório (77,74) · Convívio/Formação (51,88) · Descargas (48,64) ·
Oficina/Manutenção (45,64) · Bebidas e Mercearia (41,09) · Rouparias 1 e 2
(36,48 / 37,24) · Câmaras frias/congelação (carnes, peixes, frutas, lacticínios) ·
Economato · Cozinha/Cocção · Vestiários · Governanta · RH · Chefe de Compras · etc.

### 2.2 Térreo — **23 ambientes · 1.103 m²** (público + administração)
**Lobby (508,60 m²)** · Restaurantes (93,52 ×2) · Bar (29,17) · Copa do Bar
(17,04) · Copas (23,26 ×2) · WC Masculino/Feminino/Hall/Def. (24,50 / 26,00 /
11,08 / 4,77) · Diretor (24,01) · Sub‑Diretor (16,45) · Reuniões (21,48) ·
Sala de Cinema (22,62) · Sala de TV (21,93) · Animação (32,00) · Lojas /
Loja Garrafeira (13,05 / 21,93 / 16,63) · Maleiro Bell (23,39) · Equipamentos (17,48).

---

## 3. Conferência com o corte e fachadas (032)

Níveis (cotas) lidos no corte/fachadas, datum **±0,00**:

| Cota | Leitura |
|------|---------|
| 0,00 | referência |
| 5,00 / 6,50 | piso Térreo (escalonado) |
| 8,40 / 8,95 | segundo nível do Térreo |
| 9,90 | topo das fachadas / forro |
| 11,70 | cumeeira da cobertura |

- **Pé‑direito** medido (cotas verticais do corte): **2,72–2,84 m** (forro) —
  adotado **2,80–2,84 m** para a altura dos ambientes do modelo.
- **Térreo escalonado** confirmado (níveis 5,00 e 8,40 nas plantas) — coerente
  com a leitura "Nível 5.00 / Nível 8.40" anotada na planta do Térreo.

---

## 4. O que foi modelado (v111)

- **Removidos** os 16 `IfcSpace` genéricos do Bloco Principal.
- **Criados 55 `IfcSpace` reais** — 32 no Subsolo, 23 no Térreo — cada um com:
  - `Name` / `LongName` do ambiente (ex.: `TER-LOBBY` / "LOBBY");
  - **área real** em `Qto_SpaceBaseQuantities.GrossFloorArea` (ex.: LOBBY = 508,6 m²);
  - posição obtida por **mapeamento PCA** da planta para o footprint calibrado
    (58,7 × 57 m), agregados ao respectivo `IfcBuildingStorey` (BP‑Subsolo / BP‑Terreo);
  - altura conforme o pé‑direito do corte (~2,8 m).

> Render dos espaços: `referencias/v111_pavimentos/v111_espacos_por_pavimento.png`.
> **Nota de LOD:** os ambientes estão como **programa de espaços** (nome+área+
> posição relativa). As **paredes de compartimentação internas** (alvenarias de
> divisória) e portas por ambiente são o próximo passo de detalhamento.

---

## 5. Validação do entregável (v111)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 502.983 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| `IfcSpace` no Bloco Principal | **55** (32 Subsolo + 23 Térreo) |
| Áreas (Qto) | conferem com a planta (ex.: LOBBY 508,6 m²) ✔ |
| Calibração v110 (footprint 58,7×57, IfcGrid, pilares) | preservada |
| Demais edifícios / SPA / cenografia | inalterados |

---

## 6. Nota técnica — leitura dos DWG/DWF

DWG (AutoCAD 2018, objetos AEC) convertidos com **LibreDWG 0.13.3** compilado no
ambiente (`dwgread -O JSON`). Os DWF (Subsolo/Térreo/Cobertura/Corte/Fachadas)
são as mesmas pranchas plotadas; a fonte métrica foi o DWG de model space.

---

## 7. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v111_PAVIMENTOS.ifc` | Modelo BIM v111 com os ambientes por pavimento |
| `build_v111.py` | Construtor reprodutível (v110 → v111) |
| `HVG_Inhotim_v111_Pavimentos.md` | Este relatório |
| `referencias/v111_pavimentos/031_planta_subsolo.png` | Planta do Subsolo (031, renderizada) |
| `referencias/v111_pavimentos/031_planta_terreo.png` | Planta do Térreo (031, renderizada) |
| `referencias/v111_pavimentos/v111_espacos_por_pavimento.png` | Espaços do modelo por pavimento |
