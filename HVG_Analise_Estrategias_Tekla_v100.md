# Análise IFC (Maple Bear / Tekla) → Estratégias aplicadas ao HVG v100

**Referência analisada:** `MAPLE BEAR - COMPLETO (2).ifc` — modelo estrutural exportado do
**Tekla Structures** (IFC2X3, CoordinationView + QuantityTakeOff), 18 MB, 237 mil entidades.
**Aplicado em:** `HVG_MASTER_v100_FABRICACAO.ifc` · Grupo Montex · 28/06/2026

---

## 1. O que o modelo Tekla ensina (estratégias de detalhamento estrutural)

O Maple Bear é um modelo de **fabricação metálica/concreto LOD 400-500**. Mesmo sendo outro
empreendimento (escola × resort), suas **estratégias de estruturação IFC** são exemplares:

| Estratégia Tekla | Como aparece no IFC | Valor |
|------------------|---------------------|-------|
| **Marca de peça / montagem** | `Tekla Common`: `Part mark`, `Assembly mark` | Rastreio de fabricação/logística por peça |
| **`IfcElementAssembly`** | 258 montagens (ex.: COLUNA = coluna + chapas de base/ligação) | Conjuntos fabricáveis/montáveis |
| **Quantity Take-Off por peça** | `BaseQuantities` (Length, Area, Volume, **Weight**) em 1.393 elementos | Quantitativo e **peso** confiáveis |
| **Fase de montagem (4D por elemento)** | `Tekla_4D` + campo `Phase` por peça | Sequenciamento de obra peça a peça |
| **Grade / Profile / Class** | `Tekla Common`: `Grade`(C30, A572), `Profile`(600X190), `Class` | Material normalizado + perfil real |
| **Conexões/parafusos** | `Tekla Fastener` (410), `IfcPlate` (768 chapas) | LOD 400 de ligações metálicas |
| **Material por norma** | `STEEL/A572-GR.50`, `CONCRETE/C30` | Nomenclatura padronizada grade/norma |

**Lições-chave:** (1) cada peça estrutural carrega **marca, perfil, grade, fase e peso**;
(2) peças são agrupadas em **montagens** (`IfcElementAssembly`); (3) o **peso** vem das
`BaseQuantities`, permitindo reconciliação de aço/concreto direta do modelo.

---

## 2. O que o HVG v99 ainda não tinha

O v99 já era forte (3D/4D/5D/7D, MEP, zonas, mobiliário), mas a **estrutura** estava em nível de
coordenação, **sem dados de fabricação**: nenhuma marca de peça, nenhum peso por elemento, nenhuma
montagem (`IfcElementAssembly` = 0), nenhuma fase por peça.

---

## 3. Estratégias aplicadas no v100

### 3.1 `Pset_Fabricacao` por elemento estrutural (padrão *Tekla Common*) — 1.760 peças
Pilares, vigas e lajes passam a carregar:
`PartMark` · `AssemblyMark` · `Phase` (vinculada ao cronograma 4D, fase T02-Estrutura) ·
`Grade` (material) · `Class` (Metálica/Concreto) · `ProfileRef` (seção calculada V/L) ·
`Finish` (pintura anticorrosiva no aço) · `Peso_kg` + `Peso_metodo`.

Exemplo: `BLOCOPRI-P0001` | AssemblyMark `EST-BLOCOPRI` | Phase `T02-Estrutura` | Grade `C25` | Peso 1.541 kg.

### 3.2 Peso por elemento (`IfcQuantityWeight` em `BaseQuantities`) — 1.505 pesos
Calculado do volume modelado × densidade nominal:

| Material | Elementos | Volume | Peso | Método |
|----------|-----------|--------|------|--------|
| **Concreto** (C25/C30) | 901 | 12.207 m³ | **30.517 t** | real (sólido × 2.500 kg/m³) |
| **Aço** (ASTM A500) | 604 pilares | 29,1 m³ | **228,7 t** | calculado de perfis modelados (~55 kg/m, × 7.850) |

> O aço resultou em ~55 kg/m médio — coerente com perfis W reais, confirmando que a geometria do v99
> usa perfis metálicos (peso confiável, não sólido cheio).

### 3.3 `IfcElementAssembly` — 22 lotes de montagem metálica
A estrutura metálica de cada edifício foi agrupada como **lote de montagem** (`EST-<edifício>`),
espelhando o conceito de conjunto fabricável do Tekla (sem inventar conexões inexistentes no v99).

### 3.4 `Pset_Aco_Reconciliacao_Calc` (consolidado, calculado)
Reconciliação com números **derivados da geometria**: 604 pilares metálicos, 29,1 m³, 228,7 t de aço;
901 elementos de concreto, 12.207 m³, 30.517 t — substitui a estimativa anterior (~1.350 t) por
valores do próprio modelo.

---

## 4. O que NÃO foi transferido (e por quê)

- **Geometria/dados do Maple Bear** — empreendimento distinto; transferir seria incorreto.
- **Conexões/parafusos (`IfcMechanicalFastener`, chapas)** — o v99 não tem detalhamento de ligações;
  criar artificialmente seria inventar. Fica como **evolução LOD 400+** caso haja modelo Tekla do HVG.
- **Perfis nomeados** (ex. W200×52) — o v100 registra `ProfileRef` por seção calculada; a nomenclatura
  comercial exata depende do detalhamento metálico executivo.

---

## 5. Validação do v100

| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| GUIDs únicos · Georreferência | Sim · E 578.800 / N 7.773.500 ✔ |
| `Pset_Fabricacao` (marcas de peça) | 1.760 ✅ |
| `IfcQuantityWeight` (pesos) | 1.505 ✅ |
| `IfcElementAssembly` (lotes) | 22 ✅ |
| Preservado do v99 | 5D (15 custos), 7D (COBie), 4D (8 tasks), 1.760 móveis, 9 underlays ✅ |
| Entidades | 469.142 |

---

## 6. Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| **`HVG_MASTER_v100_FABRICACAO.ifc`** | v99 + camada de fabricação/montagem estrutural (estratégia Tekla) |
| `HVG_Analise_Estrategias_Tekla_v100.md` | Esta análise |
| `build_v100.py` | Script reproduzível |
| `MAPLE_BEAR_COMPLETO.ifc` | Modelo de referência analisado (Tekla) |
