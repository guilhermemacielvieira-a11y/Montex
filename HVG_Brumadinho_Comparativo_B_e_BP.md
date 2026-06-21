# HVG Brumadinho — Verificação/Comparativo: Bloco B e Bloco Principal (v92)

**Modelo:** `HVG_MASTER_v92_alinhado.ifc` · **Data:** 21/06/2026 · Grupo Montex

Extensão da verificação de alinhamento (placement, confiável) e comparativo
visual aos Blocos de Apartamentos B e ao Bloco Principal.

---

## 1. Bloco B — conferência (meio-nível / split-level)
| Item | Desenho (Cortes A-B/C-D, Plantas) | IFC | Status |
|------|-----------------------------------|-----|--------|
| Pé-direito | 2,60 + 0,20 = 2,80 m | 1,80→4,60→7,40 (2,80/2,80) | ✅ |
| Janelas — alinhamento X | alinhadas | 99,7 / 103,9 / … iguais nos 3 pisos | ✅ |
| Meio-nível | SubSolo a montante, Térreo exposto, Pav.1 a jusante | SubSolo Y=141 · Térreo Y=119+141 · Pav.1 Y=119 | ✅ |
| Térreo 12 aptos / demais 6 | sim | 12 janelas no térreo, 6 nos demais | ✅ |
| Guarda-corpos varanda | presentes | restituídos (v92) | ✅ |

### Erro encontrado e CORRIGIDO
- **Coberturas planas dos Blocos B-13 a B-16 flutuando 3,00 m acima do Pav.1**
  (laje impermeabilizada em Z 13,20/13,70/14,60/15,05 em vez de capear o último
  pavimento). **Correção:** rebaixadas 3,00 m (→ 10,20/10,70/11,60/12,05),
  capeando corretamente o Pav.1. Validado.

Comparativo: `HVG_Comparativo_BlocoB_Corte.pdf/png` (perfil mostrando o meio-nível
e a cobertura já reposicionada).

---

## 2. Bloco Principal — conferência
| Item | Desenho (Fachadas) | IFC | Status |
|------|--------------------|-----|--------|
| Pé-direito subsolo→térreo | ~3,00 m | 13,05→16,05 (3,00 m) | ✅ |
| Tipologia | pavilhão aberto + cobertura piramidal cerâmica | malha de 289 pilares (4,97 m) + 1 cobertura piramidal | ✅ |
| Cobertura | piramidal central + abas | piramidal (apex Z≈26,4; H≈10,4 m) | ✅ |
| Cobertura na cota correta | no topo das paredes | base Z≈ topo paredes | ✅ |

Comparativo: `HVG_Comparativo_BP_Fachada.pdf/png` (pavilhão de pilares + cobertura
piramidal, com pé-direito 3,00 m e altura da cobertura cotados).

---

## 3. Resumo das correções desta rodada
| Correção | Qtd |
|----------|-----|
| Coberturas planas dos Blocos B reposicionadas (−3,00 m) | 4 |

Falsos-positivos descartados após verificação: coberturas do Centro de Convenções
e da Boîte (telhados inclinados que sobem acima da parede — corretos).

## 4. Arquivos
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v92_alinhado.ifc` | Modelo atualizado (coberturas B corrigidas) |
| `HVG_Comparativo_BlocoB_Corte.pdf/png` | Comparativo Bloco B (perfil/meio-nível) |
| `HVG_Comparativo_BP_Fachada.pdf/png` | Comparativo Bloco Principal (fachada) |
| `HVG_Brumadinho_Comparativo_B_e_BP.md` | Este relatório |
| `comparativo_b_bp.py` | Script reproduzível |
