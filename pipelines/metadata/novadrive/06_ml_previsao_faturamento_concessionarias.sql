CREATE OR REPLACE TABLE `data-platform-copilot-dev.gold_novadrive.previsao_faturamento_concessionarias` AS
WITH dealership_info AS (
  SELECT
    id_concessionarias,
    ANY_VALUE(concessionaria) AS concessionaria,
    ANY_VALUE(cidade) AS cidade,
    ANY_VALUE(estado) AS estado,
    ANY_VALUE(sigla_estado) AS sigla_estado
  FROM `data-platform-copilot-dev.gold_novadrive.ml_receita_diaria_concessionarias`
  GROUP BY id_concessionarias
)
SELECT
  CAST(forecast_timestamp AS DATE) AS data_previsao,
  id_concessionarias,
  info.concessionaria,
  info.cidade,
  info.estado,
  info.sigla_estado,
  CAST(forecast_value AS FLOAT64) AS faturamento_previsto,
  CAST(prediction_interval_lower_bound AS FLOAT64) AS limite_inferior,
  CAST(prediction_interval_upper_bound AS FLOAT64) AS limite_superior,
  CAST(confidence_level AS FLOAT64) AS confidence_level,
  CURRENT_TIMESTAMP() AS generated_at
FROM ML.FORECAST(
  MODEL `data-platform-copilot-dev.gold_novadrive.modelo_previsao_faturamento_concessionarias`,
  STRUCT(7 AS horizon, 0.8 AS confidence_level)
) AS forecast
LEFT JOIN dealership_info AS info USING (id_concessionarias)
