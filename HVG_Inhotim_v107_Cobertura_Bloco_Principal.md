# HVG Inhotim — Revisão v107

## Cobertura do Bloco Principal: 4 águas (hip) de baixa inclinação com beiral profundo

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v106_ESTRUTURA_COBERTURAS.ifc`
**Entregue:** `HVG_MASTER_v107_COBERTURA_BP.ifc`
**Data:** 29/06/2026

---

## 1. Objetivo

Resolver a divergência **4.3** (severidade 🟠 média) da auditoria foto × modelo:
a cobertura do Bloco Principal estava nomeada "**Piramidal**" e, mais relevante,
**não tinha beiral** — a geometria ficava **5,85 m para dentro das fachadas**,
ou seja, as paredes envidraçadas avançavam para além do telhado, o oposto do
que mostram as fotografias (p.5–7), onde o telhado é um **chapéu largo de baixa
inclinação com abas (beirais) profundas em balanço** sobre as fachadas.

---

## 2. Diagnóstico (v106)

| Métrica | v106 (antes) |
|---------|--------------|
| `IfcRoof` | `HIP_ROOF` "Cobertura‑Piramidal‑Telha Cerâmica Vila Galé" (Brep) |
| Pegada do telhado | X 131,0–199,0 / Y 211,0–279,0 |
| Fachadas (paredes) | X 125,1–204,8 / Y 205,2–284,9 |
| **Balanço (beiral)** | **−5,85 m** em todos os lados (telhado *aquém* das fachadas) ❌ |
| Cumeeira | Z 10,35 (rise 6,5 m, ~10,8°) |

O tipo `HIP_ROOF` e a baixa inclinação já estavam tecnicamente corretos; o
problema central era a **ausência de beiral** e a nomenclatura.

---

## 3. O que foi modelado (v107)

Substituição da cobertura por um **sólido hip fechado (`IfcFacetedBrep`)** com:

| Métrica | v107 (depois) |
|---------|---------------|
| Nome | "Cobertura‑4Águas (Hip Baixa)‑Beiral Profundo‑Telha Cerâmica Vila Galé" |
| Tipo | `HIP_ROOF` |
| Pegada do beiral | X 122,6–207,3 / Y 202,7–287,4 |
| **Balanço (beiral)** | **+2,50 m** em todos os lados (cobre e avança sobre as fachadas) ✔ |
| Cota do beiral / cumeeira | Z 3,70 / Z 8,20 |
| Inclinação | ~6,1° (baixa, chapéu largo) |
| Cumeeira (espigão) | horizontal, 28 m ao longo de X |
| Geometria | 4 águas — 2 trapézios (frente/fundo) + 2 tacaniças triangulares |
| Material | *Telha Cerâmica Vila Galé* (preservado) |

> Preview: `referencias/v106_previews/v107_BP_cobertura_hip_beiral.png`
> (telhado em vermelho cerâmico avançando sobre o envelope de paredes em azul).

---

## 4. Validação do entregável (v107)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 510.190 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| `IfcRoof` (mantido) | 31 (cobertura antiga removida, nova adicionada) |
| Beiral cobrindo as fachadas | **+2,50 m** em todos os lados ✔ |
| Geometria (iterator) | sólido fechado, 6 vértices / 5 faces, render OK |
| Sistemas MEP / membros v106 | preservados (treliças do SPA e da recepção intactas) |

Reexecução de `audit_foto_x_modelo.py` sobre a v107 — **as três divergências
resolvidas**:
- `[4.1] SPA → ok` · `[4.2] Recepção → ok` · `[4.3] Cobertura BP → ok`

---

## 5. Observação

A pegada do Bloco Principal no modelo é praticamente **quadrada (~80 × 80 m)** —
daí o aspecto "piramidal" de qualquer cobertura de 4 águas com pendente uniforme.
A v107 introduz uma **cumeeira horizontal** (espigão de 28 m) e **rebaixa** o
telhado para mitigar esse efeito e privilegiar a leitura de "chapéu largo".
Uma futura reestruturação da **planta do bloco para a proporção retangular real**
(fora do escopo desta revisão) permitiria um espigão mais longo e fiel.

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v107_COBERTURA_BP.ifc` | Modelo BIM v107 (IFC4) |
| `build_v107.py` | Construtor reprodutível (v106 → v107) |
| `HVG_Inhotim_v107_Cobertura_Bloco_Principal.md` | Este relatório |
| `referencias/v106_previews/v107_BP_cobertura_hip_beiral.png` | Preview 3D da nova cobertura |
