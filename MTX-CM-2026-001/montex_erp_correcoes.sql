-- ============================================================================
-- MONTEX ERP v5 — CORREÇÕES DE HIGIENE DE DADOS
-- Origem: análise de cenários 04/07/2026 | REVISAR ANTES DE APLICAR EM PRODUÇÃO
-- Ordem recomendada: rodar em staging/branch primeiro; cada bloco é independente.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1) TRIGGER: preencher datas de fim de etapa automaticamente no kanban
-- Problema: data_fim_fabricacao/solda/pintura não vêm sendo gravadas nas peças;
-- o throughput só é reconstituível via producao_historico.
-- Solução: ao mudar a etapa da peça, gravar o timestamp de fim da etapa anterior
-- e de início da nova — de graça, sem mudar o frontend.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_pecas_producao_etapa_timestamps()
RETURNS trigger AS $$
BEGIN
  IF NEW.etapa IS DISTINCT FROM OLD.etapa THEN
    -- fecha a etapa anterior
    IF OLD.etapa = 'fabricacao' AND NEW.data_fim_fabricacao IS NULL THEN
      NEW.data_fim_fabricacao := now();
    ELSIF OLD.etapa = 'solda' AND NEW.data_fim_solda IS NULL THEN
      NEW.data_fim_solda := now();
    ELSIF OLD.etapa = 'pintura' AND NEW.data_fim_pintura IS NULL THEN
      NEW.data_fim_pintura := now();
    END IF;
    -- abre a nova etapa
    IF NEW.etapa = 'fabricacao' AND NEW.data_inicio_fabricacao IS NULL THEN
      NEW.data_inicio_fabricacao := now();
    ELSIF NEW.etapa = 'solda' AND NEW.data_inicio_solda IS NULL THEN
      NEW.data_inicio_solda := now();
    ELSIF NEW.etapa = 'pintura' AND NEW.data_inicio_pintura IS NULL THEN
      NEW.data_inicio_pintura := now();
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_pecas_etapa_ts ON pecas_producao;
CREATE TRIGGER trg_pecas_etapa_ts
  BEFORE UPDATE ON pecas_producao
  FOR EACH ROW EXECUTE FUNCTION fn_pecas_producao_etapa_timestamps();

-- ----------------------------------------------------------------------------
-- 2) NORMALIZAÇÃO: setores da folha com grafia duplicada
-- Problema: 'Solda'/'solda', 'Montagem'/'montagem', 'Fabricação'/'fabricacao'
-- quebram relatórios por setor.
-- Solução: padronizar em minúsculas sem acento + constraint de domínio.
-- ----------------------------------------------------------------------------
UPDATE funcionarios SET setor = CASE
  WHEN lower(setor) IN ('solda')                    THEN 'solda'
  WHEN lower(setor) IN ('montagem')                 THEN 'montagem'
  WHEN lower(setor) IN ('fabricação','fabricacao')  THEN 'fabricacao'
  WHEN lower(setor) IN ('pintura')                  THEN 'pintura'
  WHEN lower(setor) IN ('produção','producao')      THEN 'producao'
  WHEN lower(setor) IN ('alumínio','aluminio')      THEN 'aluminio'
  WHEN lower(setor) IN ('administrativo geral','administrativo','geral') THEN 'administrativo'
  ELSE lower(setor) END
WHERE setor IS NOT NULL;

ALTER TABLE funcionarios DROP CONSTRAINT IF EXISTS chk_funcionarios_setor;
ALTER TABLE funcionarios ADD CONSTRAINT chk_funcionarios_setor
  CHECK (setor IS NULL OR setor IN
    ('solda','montagem','fabricacao','pintura','producao','aluminio','administrativo','expedicao'));

-- Mesma padronização nas despesas (categoria tem 'Mão de Obra' vs 'mao_de_obra_fabrica' etc.)
-- ATENÇÃO: revisar mapeamento antes de rodar — pode haver semântica diferente entre categorias.
-- UPDATE lancamentos_despesas SET categoria = ... (mapear após validação com financeiro)

-- ----------------------------------------------------------------------------
-- 3) DADO FALTANTE: contrato SPASSO G1 sem valor (150.240 kg = 42% do peso da carteira)
-- >>> SUBSTITUIR :valor_contrato pelo valor real antes de rodar <<<
-- ----------------------------------------------------------------------------
-- UPDATE obras SET contrato_valor_total = :valor_contrato, updated_at = now()
-- WHERE nome = 'SPASSO - GALPÃO G1 - VIA EXPRESSA' AND contrato_valor_total IS NULL;

-- ----------------------------------------------------------------------------
-- 4) GUARDA-CORPO: impedir obra ativa sem valor de contrato daqui pra frente
-- (constraint suave via trigger de aviso — não bloqueia, registra pendência)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pendencias_cadastro (
  id bigserial PRIMARY KEY,
  tabela text NOT NULL, registro_id text NOT NULL,
  campo text NOT NULL, criado_em timestamptz DEFAULT now(), resolvido boolean DEFAULT false
);
ALTER TABLE pendencias_cadastro ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_pendencias_auth ON pendencias_cadastro;
CREATE POLICY p_pendencias_auth ON pendencias_cadastro
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE OR REPLACE FUNCTION fn_obras_valor_pendente() RETURNS trigger AS $$
BEGIN
  IF NEW.status = 'ativo' AND NEW.contrato_valor_total IS NULL THEN
    INSERT INTO pendencias_cadastro(tabela, registro_id, campo)
    VALUES ('obras', NEW.id, 'contrato_valor_total')
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_obras_valor ON obras;
CREATE TRIGGER trg_obras_valor AFTER INSERT OR UPDATE ON obras
  FOR EACH ROW EXECUTE FUNCTION fn_obras_valor_pendente();

-- ----------------------------------------------------------------------------
-- 5) VIEW GERENCIAL: throughput mensal em kg (a fonte única do indicador
-- que alimentou a análise Igarapé — pronto para o painel do ERP)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_throughput_mensal AS
SELECT date_trunc('month', ph.created_at)::date AS mes,
       ph.etapa_para,
       round(sum(pp.peso_total)) AS kg,
       count(*) AS movimentacoes
FROM producao_historico ph
JOIN pecas_producao pp ON pp.id = ph.peca_id
GROUP BY 1, 2;

CREATE OR REPLACE VIEW vw_backlog_atual AS
SELECT etapa, round(sum(peso_total)) AS kg, count(*) AS pecas
FROM pecas_producao
WHERE etapa NOT IN ('expedido','enviado','entregue')
GROUP BY etapa;
