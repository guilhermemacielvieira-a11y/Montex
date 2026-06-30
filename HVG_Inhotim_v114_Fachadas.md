# HVG Inhotim — Revisão v114

## Fachadas envidraçadas do Bloco Principal (curtain wall)

**Projeto:** Hotel Vila Galé Inhotim — Country Resort Hotel das Artes, Conference & SPA
**Autoria do modelo:** Guilherme Maciel — Grupo Montex Ltda (CNPJ 10.798.894/0001‑60)
**Modelo base:** `HVG_MASTER_v113_PORTAS.ifc`
**Entregue:** `HVG_MASTER_v114_FACHADAS.ifc`
**Referência:** fotos p.5–7 (envelope totalmente envidraçado) · planta do Térreo ("Envidraçado", FACHADA 1–4)
**Data:** 30/06/2026

---

## 1. Objetivo

Modelar as **fachadas envidraçadas** do Bloco Principal — o envelope de vidro que,
sob o chapéu de cobertura, é a imagem‑marca do edifício nas fotografias.

---

## 2. O que foi modelado (v114)

- **Removidas** as 4 paredes de perímetro do Térreo (alvenaria/pedra, Z 0–3,55).
- **Criadas 4 `IfcCurtainWall`** (FACHADA 1‑Sul / 2‑Norte / 3‑Oeste / 4‑Leste) no
  perímetro calibrado (58,7 × 57 m), do piso (Z 0) ao topo do Térreo (Z 3,55),
  cada uma composta de:
  - **montantes verticais** (`IfcMember` MULLION) alinhados à **malha (~4,9 m)** +
    montantes de canto;
  - **travessas** inferior, intermédia (1,80 m) e superior (`IfcMember`);
  - **pano de vidro** (`IfcPlate`, SHEET) — material *Vidro Laminado Fachada*.

| Fachada | Montantes+travessas | Pano de vidro |
|---------|:-------------------:|:-------------:|
| 1‑Sul · 2‑Norte · 3‑Oeste · 4‑Leste | 16 cada (**64**) | 1 cada (**4**) |

Materiais: *Alumínio Anodizado Fachada* (caixilho) · *Vidro Laminado Fachada* (vidro).

> Preview: `referencias/v114_fachadas/v114_fachadas_envidracadas_3d.png` — o envelope
> de vidro com grelha de montantes sob a cobertura hip de beirais profundos.

---

## 3. Validação do entregável (v114)

| Verificação | Resultado |
|-------------|-----------|
| Schema | **IFC4** válido |
| Entidades | 519.042 |
| GlobalIds únicos | **Sim** (0 duplicados) |
| `IfcCurtainWall` | **4** (FACHADA 1–4) |
| `IfcMember` (caixilho) / `IfcPlate` (vidro) novos | 64 / 4 |
| Geometria das fachadas (render) | **68/68 partes válidas** |
| Portas/divisórias/ambientes (v111–v113) | preservados |
| Calibração v110 (footprint, IfcGrid, pilares) + cobertura | preservada |
| SPA / cenografia / demais edifícios | inalterados |

---

## 4. Evolução do Bloco Principal (LOD)

| Versão | Entrega |
|--------|---------|
| v110 | Calibração pela planta oficial + IfcGrid (58,7×57, malha ~4,9 m) |
| v111 | Programa de ambientes (55 espaços, áreas reais) |
| v112 | Divisórias internas reais (868 paredes) |
| v113 | Portas internas (78, com vãos) |
| **v114** | **Fachadas envidraçadas (4 curtain walls)** |

---

## 5. Próximos passos possíveis

- **Vidros do nível superior / clerestório** sob a cobertura (a fachada real tem
  pano de vidro também acima do forro do Térreo, até o beiral).
- **Esquadrias detalhadas** das fachadas (folhas de abrir, portas de fachada — as
  13 portas de perímetro detectadas na v113).
- **Guarda‑corpos** envidraçados das varandas/terraços (planta: "Guarda‑corpo").
- **Mobiliário e louças** internos (camadas `MOB` / `Loiças`).

---

## 6. Arquivos desta entrega

| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v114_FACHADAS.ifc` | Modelo BIM v114 com as fachadas envidraçadas |
| `build_v114.py` | Construtor reprodutível (v113 → v114) |
| `HVG_Inhotim_v114_Fachadas.md` | Este relatório |
| `referencias/v114_fachadas/v114_fachadas_envidracadas_3d.png` | Volumetria com as fachadas |
