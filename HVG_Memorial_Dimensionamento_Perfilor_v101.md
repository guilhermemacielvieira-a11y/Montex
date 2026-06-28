# Memorial de Pré-Dimensionamento — Lajes Steel Deck, Vigas e Fechamento Termilor Wall (Perfilor)

**Empreendimento:** Hotel Vila Galé Collection Brumadinho · **Modelo:** `HVG_MASTER_v101_DIMENSIONADO.ifc`
**Sistema:** estrutura metálica + laje mista steel deck + fechamento em painel termoisolante
**Fabricante de referência:** **ArcelorMittal Perfilor** (Steel Deck MF-75 · Painel Termilor Wall® PIR)
**Normas:** NBR 6120 (ações), NBR 8800 (aço laminado), NBR 14762 (perfis formados a frio), NBR 6123 (vento), NBR 14323 (incêndio)
**Grupo Montex · 28/06/2026**

> ⚠️ **Pré-dimensionamento** para nível de projeto BIM. Os valores de catálogo da Perfilor são de
> **referência** e devem ser confirmados na ficha técnica vigente do fabricante; o dimensionamento
> executivo exige verificação peça a peça e projeto de estrutura assinado por responsável técnico.

---

## 0. Parâmetros de projeto

| Parâmetro | Valor |
|-----------|-------|
| Vão estrutural (bay) | **4,00 m** |
| Pé-direito (fechamento) | **2,79 m** |
| Uso | Hoteleiro / residencial |
| Aço estrutural | ASTM A572 Gr.50 (fy = 34,5 kN/cm²) |
| Concreto da capa | C25 (fck = 25 MPa) |

---

## 1. Laje mista — Steel Deck Perfilor **MF-75**

**Geometria MF-75:** altura da nervura 75 mm · largura útil 915 mm · chapa Zincada.
**Altura total adotada:** h = **130 mm** (75 deck + 55 capa C25) · consumo de concreto ≈ **0,096 m³/m²**.

### 1.1 Ações na laje (NBR 6120)
| Ação | kN/m² |
|------|-------|
| Peso próprio (deck 0,80 mm ~0,10 + concreto 0,096 × 25 = 2,40) | 2,50 |
| Contrapiso + revestimento | 1,00 |
| Divisórias leves (painel) | 0,50 |
| Sobrecarga de utilização (uso misto hotel) | 2,00 |
| **Total característico (g + q)** | **6,00** |
| **Total de cálculo (γ = 1,4) — ELU** | **8,40** |

### 1.2 Vão da laje × escoramento
O MF-75 chapa **0,80 mm** vence, **sem escoramento**, vãos de ~2,5–3,0 m (regime de vão duplo/contínuo).
Para o bay de 4,00 m adota-se **viga secundária intermediária**, reduzindo o vão da laje a **2,00 m**:

- Momento na laje: M_d = q_d·L²/8 = 8,40 × 2,00²/8 = **4,2 kN·m/m** ≪ capacidade da seção mista MF-75 h=130 (~15 kN·m/m) → **OK com folga**.
- Flecha de serviço (L = 2,0 m): ≪ L/350 → **OK**.

**Especificação:** Steel Deck **MF-75 t = 0,80 mm**, h = 130 mm, **vão 2,0 m sem escoramento**,
capa C25, **tela soldada Q-92** (retração + momento negativo sobre apoios), conectores de cisalhamento
(stud bolt ø19) nas vigas de apoio.

---

## 2. Vigas metálicas (NBR 8800) — perfis Gerdau/ArcelorMittal

### 2.1 Viga secundária (VS) — apoia a laje, vão 4,00 m, faixa de influência 2,00 m
- Carga: q_k = 6,00 × 2,00 = 12,0 kN/m → q_d = 16,8 kN/m
- Momento: **M_Sd = q_d·L²/8 = 16,8 × 4,00²/8 = 33,6 kN·m**
- Módulo necessário: W_x ≥ M_Sd/(φ_b·f_y) = 3360/(0,90 × 34,5) = **108 cm³**
- **Flecha governa:** para δ ≤ L/350 = 11,4 mm com q_serv = 12 kN/m → I_x ≥ 1.754 cm⁴
- **Perfil adotado: W 250 × 17,9** (I_x = 2.291 cm⁴ · W_x = 180 cm³): φM_n = 55,9 kN·m > 33,6 ✓ · δ ≈ 8,7 mm < 11,4 ✓

### 2.2 Viga principal (VP) — apoia as secundárias, vão 4,00 m
- Reações das VS: ≈ 96 kN no vão → M_Sd ≈ q_eq·L²/8 ≈ 33,6 × 4²/8 = **67,2 kN·m**
- W_x ≥ 6720/(0,90 × 34,5) = **216 cm³**
- **Perfil adotado: W 310 × 28,3** (I_x = 5.500 cm⁴ · W_x = 351 cm³): φM_n = 109 kN·m > 67,2 ✓ · flecha ✓ (folga para carga concentrada)

### 2.3 Resumo de perfis
| Elemento | Vão | M_Sd | Perfil | Verificação |
|----------|-----|------|--------|-------------|
| Viga secundária (VS) | 4,00 m | 33,6 kN·m | **W 250 × 17,9** | M e flecha OK |
| Viga principal (VP) | 4,00 m | 67,2 kN·m | **W 310 × 28,3** | M e flecha OK |

Aço A572 Gr.50 · pintura anticorrosiva · ligações parafusadas A325 · proteção ao fogo TRRF conforme NBR 14432.

---

## 3. Fechamento — Painel **Termilor Wall® PIR 50 mm** (Perfilor)

Painel sanduíche autoportante: chapa externa micronervurada + núcleo **PIR 50 mm** + chapa interna nervurada.

| Propriedade (referência Perfilor) | Valor |
|-----------------------------------|-------|
| Espessura do núcleo (PIR) | 50 mm |
| Largura útil | 1.000 mm |
| Peso próprio | ≈ 10,7 kg/m² (0,107 kN/m²) |
| Transmitância térmica U | ≈ 0,43 W/m²·K |
| Chapas de aço | 0,43–0,50 mm (ArcelorMittal) |

### 3.1 Verificação do fechamento (vão vertical = pé-direito 2,79 m)
- Carga de vento (NBR 6123, V₀ ≈ 30 m/s, Brumadinho): q ≈ 0,8 kN/m² (sucção/sobrepressão de cálculo)
- Peso próprio: 0,107 kN/m²
- O painel PIR 50 mm vence **vão vertical de até ~3,5–4,0 m** para q ≈ 1,0 kN/m² → **2,79 m: OK sem montante intermediário**
- Fixação: parafusos autobrocantes nas vigas/travessas de borda; juntas macho-fêmea com vedação.
- Desempenho: térmico U ≈ 0,43 W/m²·K · reação ao fogo do núcleo PIR (classe conforme catálogo).

**Especificação:** Painel **Termilor Wall PIR 50 mm**, largura útil 1.000 mm, montado na vertical entre
piso e viga de borda, vão 2,79 m sem travessa intermediária; acabamento externo na cor do projeto.

---

## 4. Quantitativos e dados aplicados ao BIM (v101)

| Sistema | Elementos no modelo | Especificação aplicada |
|---------|---------------------|------------------------|
| Laje mista | 125 lajes de piso | Steel Deck MF-75 t=0,80 / h=130 / Q-92 |
| Vigas | 492 | VS W250×17,9 / VP W310×28,3 |
| Fechamento | 636 paredes | Termilor Wall PIR 50 mm |

Cada elemento recebe os PSets **`Pset_Dimensionamento`** (sistema, cargas, esforços, verificação) e
**`Pset_Perfilor_Produto`** (linha, espessura, peso, norma) — rastreáveis no modelo federado.

---

## 5. Fontes (dados de referência do fabricante)

- ArcelorMittal Perfilor — Steel Deck MF-75 e Painel Termilor Wall® (catálogos do fabricante)
- Tabela MF-75 (geometria de mercado): h=130–200 mm, consumo 0,093–0,163 m³/m², telas Q-75…Q-138

> Os perfis e cargas admissíveis devem ser confirmados nas fichas técnicas vigentes da Perfilor e no
> projeto estrutural executivo.
