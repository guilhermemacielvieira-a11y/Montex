# HVG Inhotim — Revisão v108

## Cenografia de lazer: parque aquático infantil + pista de carros

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Local:** Brumadinho — Minas Gerais — Brasil
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v107_COBERTURA_BP.ifc`
**Entregue:** `HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc`
**Data:** 30/06/2026

---

## 1. Objetivo

Resolver as divergências **4.5** e **4.6** (severidade 🟢 baixa) da auditoria
foto × modelo, adicionando a cenografia das áreas infantis que aparece nas
fotografias mas estava ausente no modelo.

---

## 2. O que foi modelado

### 2.1 Piscina das Crianças / Parque aquático (foto p.12) — **31 elementos**
Sobre a `Piscina-Infantil` já existente (X 77,5–92,5 / Y 255–265, lâmina Z ≈ 2,30):

| Elemento | Qtd | Descrição |
|----------|----:|-----------|
| Cogumelos‑chafariz | 3 | Haste + chapéu‑disco (Ø 1,8 m) |
| Balde basculante | 1 | Haste 3,2 m + balde 1,0 m |
| Escorregas | 2 | Rampas inclinadas até a água |
| Palmeira lúdica | 1 | Tronco + 6 folhas radiais (verde) |
| Esculturas (pato/sapo) | 2 | Massas lúdicas |
| Guarda‑sóis | 6 | Mastro 2,4 m + lona Ø 3,2 m (laranja) |

Materiais novos: *Plástico Lúdico Colorido*, *Plástico Lúdico Verde*,
*Lona Guarda‑Sol Laranja*, *Aço Galvanizado Estrutura Lúdica*.

> Preview: `referencias/v106_previews/v108_parque_aquatico.png`

### 2.2 Clube da Criança / Pista de carros (foto p.13) — **65 elementos**
Sobre a `Pista-de-Carros-Infantil` já existente (X 371–409 / Y 221–239,
superfície Z ≈ −0,08), que tinha só a laje — sem sinalização nem pintura:

| Elemento | Qtd | Descrição |
|----------|----:|-----------|
| Faixa de contorno do circuito | 4 | Perímetro pintado |
| Eixo central tracejado | 7 | Divisória da via |
| Faixas de pedestres (zebrado) | 10 | 2 travessias |
| Rotatória central (anel) | 16 | Marcação circular |
| **Pintura viária (total)** | **37** | Material *Tinta Viária Branca* |
| Placas de sinalização | 14 | Poste 1,1 m + placa 0,4 m (28 peças) |

Materiais novos: *Tinta Viária Branca*, *Aço Galvanizado Poste*,
*Alumínio Placa Sinalização*.

> Preview: `referencias/v106_previews/v108_pista_carros.png`

---

## 3. Validação do entregável (v108)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 511.470 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| Elementos novos | **96** (31 parque aquático + 65 pista) |
| Geometria (iterator) | 100 % renderizável |
| Posição parque aquático | X 73–97 / Y 251–269 (sobre a piscina infantil) ✔ |
| Posição pintura da pista | X 371,9–408,1 / Y 221,9–238,1 (sobre a pista) ✔ |
| Revisões anteriores | preservadas (treliças v106 + cobertura v107) |

---

## 4. Estado das divergências foto × modelo

| # | Item | Status |
|---|------|--------|
| 4.1 | Cobertura do SPA (tesouras de madeira) | ✅ v106 |
| 4.2 | Treliça espacial da recepção | ✅ v106 |
| 4.3 | Cobertura do Bloco Principal (hip + beiral) | ✅ v107 |
| 4.5 | Parque aquático infantil (brinquedos) | ✅ **v108** |
| 4.6 | Pista de carros (sinalização + pintura) | ✅ **v108** |
| — | Reestruturação da planta do Bloco Principal (proporção retangular) | ⏭️ próxima |

---

## 5. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v108_CENOGRAFIA_LAZER.ifc` | Modelo BIM v108 (IFC4) |
| `build_v108.py` | Construtor reprodutível (v107 → v108) |
| `HVG_Inhotim_v108_Cenografia_Lazer.md` | Este relatório |
| `referencias/v106_previews/v108_parque_aquatico.png` | Preview 3D do parque aquático |
| `referencias/v106_previews/v108_pista_carros.png` | Preview 3D da pista de carros |
