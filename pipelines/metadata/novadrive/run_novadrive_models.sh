#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-data-platform-copilot-dev}"
MODEL_DIR="/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/metadata/novadrive"

for file in \
  "$MODEL_DIR/01_silver_vendas.sql" \
  "$MODEL_DIR/02_gold_faturamento_por_concessionaria.sql" \
  "$MODEL_DIR/03_gold_performance_vendedores.sql" \
  "$MODEL_DIR/04_ml_receita_diaria_concessionarias.sql" \
  "$MODEL_DIR/05_ml_modelo_previsao_faturamento.sql" \
  "$MODEL_DIR/06_ml_previsao_faturamento_concessionarias.sql"
do
  echo "Running $(basename "$file")"
  bq query --project_id="$PROJECT_ID" --use_legacy_sql=false < "$file"
done
