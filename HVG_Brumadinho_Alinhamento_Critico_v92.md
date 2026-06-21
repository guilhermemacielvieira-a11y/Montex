# HVG Brumadinho — Alinhamento IFC × Desenhos (Cortes/Fachadas) e Correção Crítica

**Modelo de entrada:** `HVG_MASTER_v91_consolidado.ifc`
**Modelo corrigido:** `HVG_MASTER_v92_alinhado.ifc` (IFC4)
**Referências:** Bloco Aptos A — Cortes e Fachadas; Bloco Aptos B — Plantas; Bloco Principal — Fachadas
**Data:** 21/06/2026 · Grupo Montex

---

## 1. Método
Verificação feita por **matemática de placement** (`IfcLocalPlacement`, confiável),
não pela malha — pois o motor de geometria deste ambiente apresenta um *bug de
memória* no `create_shape` repetido (gera vértices-lixo intermitentes). A leitura
por **iterador** (usada na renderização) confirma **0 elementos corrompidos** no modelo.
**Os dados do IFC estão íntegros** (0 `IfcCartesianPoint`/`IfcDirection` com coordenada inválida).

## 2. Conferência de alinhamento (IFC × desenhos) — CONFORME
| Item verificado | Desenho | IFC | Status |
|-----------------|---------|-----|--------|
| Pé-direito (piso a piso) | 2,60 + 0,20 laje = **2,80 m** | 2,80 m (15,70→18,50→21,30) | ✅ |
| Pé-direito Bloco Principal | — | 3,00 m | ✅ |
| Janelas — alinhamento vertical (X) | alinhadas nos 3 pisos | dZ/dX = 0,000; mesmo X nos 3 pisos | ✅ |
| Esquadrias frente/fundo | porta-janela (peitoril 0,20) + janela alta (1,40) | idem | ✅ |
| Varandas — empilhamento | alinhadas | mesma XY, Z empilhado | ✅ |
| Bloco B — meio-nível (split level) | subsolo a montante, pav1 a jusante (cortes A-B/C-D) | janelas X-alinhadas, fachadas opostas por piso | ✅ |
| Paredes/lajes — nível | horizontais | inclinação 0,000 (níveis constantes) | ✅ |

> O “tilt” que aparecia na fachada HD anterior era **artefato de projeção**
> (sobreposição de fachada frente+fundo no render), **não** um erro do modelo —
> placements são identidade e as lajes/guarda-corpos estão em Z constante.

## 3. ERROS ENCONTRADOS E CORRIGIDOS

### 3.1 Guarda-corpos de varanda ausentes (segurança / NBR 14718) — **CRÍTICO**
- **Antes:** das **48** lajes de varanda (16 blocos × 3 pisos), apenas **16** tinham
  guarda-corpo; **32 pisos sem proteção** (≈192 varandas).
- Os guarda-corpos existentes estavam **contidos no Site** (não no pavimento) e **sem material**.
- A geometria deles usava **extrudados de círculo com eixo rotacionado** (corrimão
  tubular) — representação frágil que provoca **renderização errada** em vários motores.
- **Correção:** removidos os 20 guarda-corpos frágeis e **reconstruídos 48 guarda-corpos
  de vidro robustos** (caixas axis-aligned, painel h=1,05 + corrimão), um por laje de
  varanda, **contidos no pavimento correto** e com **material Vidro Laminado 8mm**.
- **Resultado:** **0 pisos de varanda sem guarda-corpo**; 0 geometria frágil; iterador confirma 48/48 íntegros.

### 3.2 Saneamento associado
- Containment espacial das varandas corrigido (Site → pavimento).
- Material aplicado a todos os guarda-corpos.

## 4. Visual comparativo
`HVG_Comparativo_BlocoA_Fachada.pdf/png`: fachada Sul do Bloco A (IFC v92) com os
níveis de piso e as cotas de pé-direito do projeto (2,60 + 0,20 = 2,80 m) sobrepostos,
evidenciando as 3 fileiras de esquadrias **alinhadas** e os **guarda-corpos restituídos
em todos os pisos**.

## 5. Validação final (v92)
| Verificação | Resultado |
|-------------|-----------|
| Schema / recarga | IFC4 ✔ |
| GUIDs únicos | Sim |
| Pontos/direções inválidos nos dados | **0** |
| Elementos corrompidos (via iterador) | **0** |
| Lajes de varanda sem guarda-corpo | **0** (antes 32) |
| Geometria frágil (círculo eixo-rotacionado) em railings | **0** |

## 6. Arquivos entregues
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v92_alinhado.ifc` | Modelo corrigido (guarda-corpos restituídos/robustos) |
| `HVG_Comparativo_BlocoA_Fachada.pdf/png` | Visual comparativo IFC × desenho |
| `HVG_Brumadinho_Alinhamento_Critico_v92.md` | Este relatório |
| `audit_align.py`, `fix_varandas_final.py`, `comparativo.py` | Scripts reproduzíveis |
