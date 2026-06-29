# HVG Inhotim — Revisão v106

## Estruturas de cobertura aparentes: tesouras de madeira do SPA + treliça espacial da recepção

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Cliente / Requerente:** Vila Galé
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v105_REALISTA.ifc`
**Entregue:** `HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc`
**Data:** 29/06/2026

---

## 1. Objetivo

Resolver as **duas divergências de alta severidade (🔴)** identificadas na auditoria
foto × modelo (`HVG_Inhotim_Comparacao_Foto_x_Modelo_v105.md`), modelando os dois
elementos estruturais **aparentes** mais característicos das fotografias do construído
e que ainda estavam ausentes/simplificados no modelo:

| Item | Divergência v105 | Referência |
|------|------------------|-----------|
| **4.1** | SPA com cobertura `FLAT_ROOF` (laje plana) | Foto p.14 — telhado de **tesouras de madeira** inclinado |
| **4.2** | Recepção sem estrutura de cobertura (0 `IfcMember` no Bloco Principal) | Foto p.8 — **treliça espacial metálica** aparente |

---

## 2. O que foi modelado

### 2.1 SPA — cobertura de 2 águas + tesouras de madeira lamelada colada
- **Removida** a `IfcRoof` `FLAT_ROOF` "Cobertura‑Plana‑Laje Impermeabilizada" do SPA.
- **Nova `IfcRoof` `GABLE_ROOF`** "Cobertura‑2Águas‑Telha Cerâmica‑Tesouras Madeira"
  sobre a pegada real do SPA (X 67,5–92,5 / Y 263–277), beiral 0,80 m, **cumeeira a
  Z ≈ 5,00 m** e **beiral a Z ≈ 3,00 m** (inclinação ~17°). Material: *Telha Cerâmica Vila Galé*.
- **7 tesouras** (`IfcElementAssembly` PredefinedType=`TRUSS`) vencendo o vão de ~13 m,
  cada uma com banzo inferior, dois banzos superiores (2 águas), pendural central
  (king post) e duas escoras diagonais — seção 0,12 × 0,30 m (banzos) /
  0,10 × 0,18 m (web).
- **5 terças longitudinais** de apoio do telhado (0,08 × 0,16 m).
- **47 barras** `IfcMember` no total, material *Madeira Lamelada Colada (Glulam)*.

> Preview: `referencias/v106_previews/v106_SPA_tesouras_madeira.png`

### 2.2 Recepção (Bloco Principal) — treliça espacial metálica (space frame)
- **Treliça espacial de dupla camada** (`IfcElementAssembly` PredefinedType=`TRUSS`)
  sobre o **Átrio‑Lobby Central** (X 146–184 / Y 226–264, ~38 × 38 m), grid de
  módulo ~6,3 m, banzo superior em Z ≈ 3,85 m e inferior em Z ≈ 2,65 m (altura 1,20 m).
- Geometria piramidal clássica: banzos superiores (grelha 7×7), banzos inferiores
  (grelha 6×6 deslocada meio módulo) e diagonais ligando cada nó inferior aos 4 nós
  superiores do seu módulo.
- **288 barras** `IfcMember`, seções 0,12 × 0,12 m (banzos) / 0,09 × 0,09 m (diagonais),
  material *Aço Estrutural ASTM A572 (Treliça Aparente)*.

> Preview: `referencias/v106_previews/v106_Recepcao_trelica_espacial.png`
> Observação: a altura do átrio segue o pé‑direito do térreo já existente no modelo
> (≈ 3,85 m); um eventual realce do átrio em pé‑direito duplo é tema de revisão futura.

---

## 3. Validação do entregável (v106)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido (IfcOpenShell 0.8.5) |
| Entidades | 510.197 |
| Objetos `IfcRoot` / GlobalIds únicos | 52.206 / **52.206 (0 duplicados)** |
| `IfcMember` (eram 24 — só postes de quadra) | **359** (24 + 47 SPA + 288 recepção) |
| `IfcElementAssembly` de treliça | 8 (7 tesouras SPA + 1 space frame) |
| Geometria dos novos membros (iterator) | **359/359 válidas** |
| Cobertura do SPA | `GABLE_ROOF` (laje plana removida) |
| Materiais novos | *Madeira Lamelada Colada (Glulam)*, *Aço Estrutural ASTM A572* |
| Relações órfãs/vazias | **0** (saneada 1 relação herdada vazia) |
| Sistemas MEP preservados | 6 |
| Posição (mundo) — SPA | X 66,7–93,3 / Y 262,7–277,3 / Z 2,80–5,14 ✔ |
| Posição (mundo) — Recepção | X 145,9–184,1 / Y 225,9–264,1 / Z 2,59–3,91 ✔ |

Reexecução de `audit_foto_x_modelo.py` sobre a v106:
- `[4.1] SPA com cobertura plana → **ok**`
- `[4.2] Recepção sem treliça → **ok** (members no Bloco Principal = 288)`
- `[4.3] Cobertura "Piramidal" do Bloco Principal → REVER` *(média — mantida para revisão futura)*

---

## 4. Pendências mantidas para revisão futura (não‑escopo da v106)

| # | Item | Severidade |
|---|------|:----------:|
| 4.3 | Renomear/ajustar inclinação e beirais da cobertura do Bloco Principal ("Piramidal" → hip baixa com beirais profundos) | 🟠 Média |
| 4.4 | Revisar coberturas de pavilhões lidas como planas vs. inclinadas | 🟠 Média |
| 4.5 / 4.6 | Cenografia de lazer (brinquedos do parque aquático, pista de carros infantil) | 🟢 Baixa |

---

## 5. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc` | Modelo BIM v106 (IFC4) com as estruturas de cobertura |
| `build_v106.py` | Construtor reprodutível (v105 → v106) |
| `HVG_Inhotim_v106_Estruturas_Cobertura.md` | Este relatório |
| `referencias/v106_previews/v106_SPA_tesouras_madeira.png` | Preview 3D das tesouras + cobertura do SPA |
| `referencias/v106_previews/v106_Recepcao_trelica_espacial.png` | Preview 3D da treliça espacial da recepção |
