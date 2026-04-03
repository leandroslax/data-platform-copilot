CREATE OR REPLACE TABLE `data-platform-copilot-dev.gold_novadrive.ml_receita_diaria_concessionarias` AS
SELECT
  DATE(data_venda) AS data_referencia,
  id_concessionarias,
  concessionaria,
  cidade,
  estado,
  sigla_estado,
  COUNT(*) AS total_vendas,
  SUM(valor_pago) AS faturamento_total,
  AVG(valor_pago) AS ticket_medio
FROM `data-platform-copilot-dev.silver_novadrive.vendas`
GROUP BY
  data_referencia,
  id_concessionarias,
  concessionaria,
  cidade,
  estado,
  sigla_estado
