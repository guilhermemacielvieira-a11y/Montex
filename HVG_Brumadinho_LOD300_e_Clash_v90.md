# HVG Brumadinho — Detalhamento LOD 300 + Clash Detection (v89 → v90)

**Entrada:** `HVG_MASTER_v89_programa_completo.ifc`
**Entregue:** `HVG_MASTER_v90_LOD300.ifc` (IFC4, ~20 MB)
**Data:** 21/06/2026 · Grupo Montex

---

## 1. Detalhamento interno LOD 300 (59 elementos novos)

### 1.1 Subestação (7 elementos) — sistema **ELE**
- 2 × `IfcTransformer` (transformadores a óleo 1000 kVA, VOLTAGE)
- 3 × `IfcElectricDistributionBoard` (Cubículo MT, QGBT, Cubículo de Medição)
- 2 × `IfcCableCarrierSegment` (eletrocalhas perimetrais)
- Agrupados em `ELE-EletricaIluminacao`.

### 1.2 Central de Gás (4 elementos) — **novo sistema GAS**
- `IfcTank` (tanque GLP 2000 L, STORAGE, cilíndrico horizontal)
- `IfcValve` (regulador de 1º estágio, PRESSUREREDUCING)
- 2 × `IfcPipeSegment` (rede de gás, tubo aço SCH40)
- Novo `IfcDistributionSystem` **GAS-CombustivelGLP** (PredefinedType GAS) +
  `IfcRelServicesBuildings` ligando ao edifício.

### 1.3 Quadras (48 elementos)
- Postes de rede (`IfcMember` POST) + redes (`IfcRailing`) em cada quadra
- 16 postes de iluminação (`IfcMember`) + **16 refletores LED** (`IfcLightFixture`,
  DIRECTIONSOURCE) → agrupados em `ELE-EletricaIluminacao`
- Alambrado perimetral da quadra polidesportiva (`IfcRailing`, 4 m)

Todos com material, cor (estilo de superfície) e contenção espacial corretos.
Sistemas de distribuição passam de 5 para **6** (incluindo GAS).

---

## 2. Clash Detection multidisciplinar (v90)

Varredura geométrica **broad‑phase (AABB mundo) + narrow‑phase (interpenetração
real de malhas)** sobre **3.303 elementos** (MEP + equipamentos × estrutura, e
MEP × MEP), tolerância 1 cm.

| Resultado | Valor |
|-----------|-------|
| Interferências reais totais | **1** |
| **Envolvendo o novo programa** | **0** ✅ |
| Conflitos resolvidos nesta etapa | 2 (eletrocalha A‑11 × estrada/guia, reposicionada +0,32 m em Y) |
| Remanescente | 1 — captor SPDA na cumeeira da Boîte (**por projeto, NBR 5419**, não‑conflito) |

> **Conclusão:** o programa adicionado na v89 (estacionamentos, área desportiva,
> pista, subestação, gás, apoio) e os equipamentos LOD 300 da v90 estão
> **100 % livres de interferência** com a estrutura e o MEP existentes.

Registro: `HVG_v90_Clash_Report.csv`.

---

## 3. Arquivos
| Arquivo | Conteúdo |
|---------|----------|
| `HVG_MASTER_v90_LOD300.ifc` | Modelo com equipamentos LOD 300 + clash resolvido |
| `HVG_v90_Clash_Report.csv` | Registro de clash detection |
| `HVG_Brumadinho_LOD300_e_Clash_v90.md` | Este relatório |
| `detail_lod300.py`, `clash_v90.py` | Scripts reproduzíveis |
