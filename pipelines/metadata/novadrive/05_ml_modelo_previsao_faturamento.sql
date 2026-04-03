CREATE OR REPLACE MODEL `data-platform-copilot-dev.gold_novadrive.modelo_previsao_faturamento_concessionarias`
OPTIONS(
  MODEL_TYPE = 'ARIMA_PLUS',
  TIME_SERIES_TIMESTAMP_COL = 'data_referencia',
  TIME_SERIES_DATA_COL = 'faturamento_total',
  TIME_SERIES_ID_COL = 'id_concessionarias',
  DATA_FREQUENCY = 'DAILY',
  HOLIDAY_REGION = 'BR',
  CLEAN_SPIKES_AND_DIPS = TRUE,
  ADJUST_STEP_CHANGES = TRUE,
  DECOMPOSE_TIME_SERIES = TRUE
) AS
SELECT
  data_referencia,
  id_concessionarias,
  faturamento_total
FROM `data-platform-copilot-dev.gold_novadrive.ml_receita_diaria_concessionarias`
WHERE faturamento_total IS NOT NULL
