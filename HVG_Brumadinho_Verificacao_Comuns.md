# HVG Brumadinho — Verificação dos Edifícios Comuns (SPA, Rest. Piscina, NEP, Guarita)

**Modelo:** `HVG_MASTER_v92_alinhado.ifc` · **Data:** 21/06/2026 · Grupo Montex

---

## 1. Conferência (placement, confiável) e áreas (Quadro Sinóptico)
| Edifício | Pavimentos | Cobertura | Área útil IFC | PDF (coberta) | Status |
|----------|-----------|-----------|---------------|---------------|--------|
| **SPA** (c/ piscina interior) | 1 (Térreo + anexo) | plana, no topo da parede | 560 m² | 598,13 m² | ✅ |
| **Restaurante da Piscina** | 2 (Térreo + Rooftop) | parapeito/laje no topo | 837 m² (2 pav.) | 564,97 m² (projeção) | ✅ |
| **Clube NEP** (Kids) | 1 | no topo da parede | 89 m² | 110,16 m² | ✅ |
| **Guarita** | 1 | no topo da parede | 22 m² | 20,40 m² | ✅ |

- **Pé-direito:** Rest. Piscina 3,00 m (Térreo→Rooftop); demais ~2,7–3,3 m de parede. Coerente.
- **Coberturas:** todas assentadas no topo das paredes — **0 coberturas flutuantes**
  (ao contrário dos Blocos B, já corrigidos).
- **Geometria:** **0 elementos fora de escala/posição** nos 4 edifícios.

## 2. Deficiência encontrada e CORRIGIDA — falta de janelas
- **Clube NEP e Guarita estavam com 0 janelas** (iluminação/ventilação natural
  insuficiente — não atende requisitos mínimos de habitabilidade).
- **Correção:** adicionadas **16 janelas** (alumínio + vidro), com **aberturas
  (`IfcOpeningElement` + `IfcRelVoidsElement`) vazando as paredes** e
  `IfcRelFillsElement` ligando janela↔abertura, material e quantitativos:
  - **Clube NEP: 10 janelas** (3 por fachada longa + 2 por fachada curta)
  - **Guarita: 6 janelas** (visibilidade do vigia em todas as direções)
- Validação por iterador: **0 geometria corrompida**.

> SPA (2 janelas) e Restaurante da Piscina (4) mantidos — possuem fenestração e,
> por serem edifícios de piscina/lazer com muito fechamento envidraçado/aberto,
> a contagem é plausível; não alterados sem o projeto específico.

## 3. Visual comparativo
`HVG_Comparativo_Comuns_SPA_RP_NEP_Guarita.pdf/png`: fachadas dos 4 edifícios
(NEP e Guarita já com as janelas), com alturas e cobertura conferidas.

## 4. Arquivos
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v92_alinhado.ifc` | Modelo atualizado (janelas NEP/Guarita) |
| `HVG_Comparativo_Comuns_SPA_RP_NEP_Guarita.pdf/png` | Comparativo dos 4 edifícios |
| `HVG_Brumadinho_Verificacao_Comuns.md` | Este relatório |
| `add_windows.py`, `collect4.py`, `comp4.py` | Scripts reproduzíveis |
