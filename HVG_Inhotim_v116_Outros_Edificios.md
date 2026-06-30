# HVG Inhotim — Revisão v116

## Divisórias internas: Centro de Convenções + Restaurante da Piscina (DWG oficiais)

**Modelo base:** `HVG_MASTER_v115_ACABAMENTOS.ifc` → **Entregue:** `HVG_MASTER_v116_OUTROS_EDIF.ifc`
**Fontes:** `051 - Centro Convenções - Plantas.dwg` · `06 - Restaurante da Piscina.dwg`
**Autoria:** Guilherme Maciel — Grupo Montex Ltda · **Data:** 30/06/2026

---

## 1. Objetivo

Iniciar o detalhamento dos **demais edifícios** com o mesmo método do Bloco
Principal, a partir dos DWG oficiais enviados: **paredes de compartimentação reais**.

---

## 2. Método (pipeline genérico)

`detail_lib.py` — para cada edifício:
1. Decodifica as camadas do DWG e **isola as linhas de parede**
   (Convenções: `PAR`; Restaurante: `VERM`/`VERM1`, o "vermelho" de alvenaria);
2. **De-rotaciona** pelo ângulo dominante e **mapeia** ao footprint do edifício
   no modelo (alinhamento de eixos longos + escala de ajuste);
3. Cria cada segmento como `IfcWall` (PARTITIONING) no pavimento correspondente.

---

## 3. O que foi modelado (v116)

| Edifício | Footprint modelo | Divisórias (`IfcWall`) | DWG |
|----------|------------------|:----------------------:|-----|
| **Centro de Convenções** | X 266,6–313,4 · Y 261–279 (CC‑Terreo) | **247** | 051 |
| **Restaurante da Piscina** | X 52,6–87,3 · Y 217,7–232,3 (RP‑Terreo) | **295** | 06 |

- **Convenções:** grande salão central aberto + ala de apoio (sanitários, copa,
  salas modulares) — layout fiel à planta (preview `v116_convencoes_planta_dwg.png`).
- **Restaurante:** núcleo de cozinha/serviço compacto + área de refeição aberta
  (esplanada) — preview `v116_restaurante_divisorias.png`.

---

## 4. Validação (v116)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 533.697 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Divisórias novas | **542** (247 + 295), geometria 542/542 válida |
| Bloco Principal (v110–v115) | preservado |
| Demais edifícios | inalterados |

---

## 5. Notas e pendências

- **Fidelidade:** as divisórias são **traçadas dos DWG reais** e mapeadas ao
  footprint existente de cada edifício (ajuste de escala ao envelope do modelo).
  Uma calibração dimensional exata de cada footprint (como no Bloco Principal)
  pode ser feita num passo seguinte.
- **SPA:** ainda **sem DWG** — pendente para o mesmo tratamento.
- **Próximos:** programa de ambientes (`IfcSpace`), portas e fachadas destes
  edifícios; e os **blocos de apartamentos A/B** (DWG 07/08 já recebidos).

---

## 6. Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v116_OUTROS_EDIF.ifc` | Modelo BIM v116 |
| `detail_lib.py` · `build_v116.py` | Pipeline + construtor reprodutível |
| `HVG_Inhotim_v116_Outros_Edificios.md` | Este relatório |
| `referencias/v116_outros/*.png` | Previews (Convenções/Restaurante) |
