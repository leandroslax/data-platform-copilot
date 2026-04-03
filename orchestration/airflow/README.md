# Apache Airflow via Docker

Esta pasta oferece uma alternativa local ao Cloud Composer para desenvolvimento e validacao das DAGs do projeto.

## Objetivo

Usar Apache Airflow via Docker Compose para:

- subir um ambiente local de orquestracao
- validar a DAG `novadrive_medallion_pipeline`
- testar integracoes com PostgreSQL, GCS e BigQuery
- continuar a evolucao do pipeline enquanto o Cloud Composer estiver bloqueado por quota

## Estrutura

- `docker-compose.yml`: stack local do Airflow
- `Dockerfile`: imagem customizada com providers e dependencias
- `requirements-airflow.txt`: dependencias Python adicionais para o Airflow
- `.env.example`: variaveis de ambiente base para o Compose
- `../observability/`: stack local de Prometheus e Grafana

## Pre-requisitos

- Docker Desktop
- credenciais GCP locais para BigQuery e GCS
- acesso ao PostgreSQL da Novadrive

## Subindo o ambiente

Copie o arquivo de ambiente:

```bash
cd /Users/leandrosantos/Downloads/data-platform-copilot/orchestration/airflow
cp .env.example .env
mkdir -p logs plugins config
```

Suba a stack:

```bash
docker compose up airflow-init
docker compose up -d
```

UI local do Airflow:

- [http://localhost:8081](http://localhost:8081)

Observabilidade local:

- Grafana: [http://localhost:3000](http://localhost:3000)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- cAdvisor: [http://localhost:8083](http://localhost:8083)

Credenciais padrao:

- usuario: `airflow`
- senha: `airflow`

## Credenciais GCP

Monte um service account JSON local e exporte o caminho em `.env`:

- `GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/gcp-service-account.json`

Depois monte esse arquivo em `./keys/gcp-service-account.json`.

## Connection e Variables

Depois que o Airflow subir, configure a connection do PostgreSQL:

```bash
docker compose exec airflow-webserver airflow connections add novadrive_postgres \
  --conn-type postgres \
  --conn-host 159.223.187.110 \
  --conn-login etlreadonly \
  --conn-password SUA_SENHA \
  --conn-port 5432 \
  --conn-schema novadrive
```

Configure as variables da DAG:

```bash
docker compose exec airflow-webserver airflow variables set gcp_project_id data-platform-copilot-dev
docker compose exec airflow-webserver airflow variables set novadrive_bronze_bucket data-platform-copilot-dev-data-platform-copilot-bronze
docker compose exec airflow-webserver airflow variables set novadrive_bronze_dataset bronze_novadrive
docker compose exec airflow-webserver airflow variables set novadrive_silver_dataset silver_novadrive
docker compose exec airflow-webserver airflow variables set novadrive_gold_dataset gold_novadrive
docker compose exec airflow-webserver airflow variables set novadrive_postgres_conn_id novadrive_postgres
docker compose exec airflow-webserver airflow variables set novadrive_checkpoint_object novadrive/_control/checkpoints.json
docker compose exec airflow-webserver airflow variables set novadrive_bronze_load_state_object novadrive/_control/bronze_load_state.json
```

## DAG publicada

O Compose monta automaticamente:

- `/Users/leandrosantos/Downloads/data-platform-copilot/orchestration/composer/dags`

Entao a DAG abaixo deve aparecer na UI:

- `novadrive_medallion_pipeline`

## Encerrando

```bash
docker compose down
```

Para limpar volumes do metadata DB:

```bash
docker compose down -v
```

## API local com metricas

Para a observabilidade ficar completa, suba tambem a API local com metricas Prometheus:

```bash
cd /Users/leandrosantos/Downloads/data-platform-copilot
source .venv/bin/activate
uvicorn app.api.main:app --reload
```

Endpoint local de metricas:

- [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)
