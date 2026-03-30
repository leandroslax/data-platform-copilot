CREATE OR REPLACE TABLE `data-platform-copilot-dev.gold_novadrive.faturamento_por_concessionaria` AS
SELECT
  id_concessionarias,
  concessionaria,
  cidade,
  estado,
  sigla_estado,
  COUNT(*) AS total_vendas,
  SUM(valor_pago) AS faturamento_total,
  AVG(valor_pago) AS ticket_medio,
  MIN(data_venda) AS primeira_venda,
  MAX(data_venda) AS ultima_venda
FROM `data-platform-copilot-dev.silver_novadrive.vendas`
GROUP BY
  id_concessionarias,
  concessionaria,
  cidade,
  estado,
  sigla_estado
