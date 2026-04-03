# Cloud Composer

Esta pasta mantém uma referência técnica dos artefatos de orquestração originalmente preparados para Cloud Composer.

O Cloud Composer foi descartado como caminho operacional neste projeto. A execução oficial da DAG acontece em Apache Airflow local via Docker, mas os arquivos desta pasta continuam úteis como referência da DAG e das SQLs.

## DAG principal

- `dags/novadrive_medallion_pipeline.py`

Fluxo:

1. extracao incremental PostgreSQL -> GCS Bronze
2. carga GCS -> BigQuery Bronze
3. construcao da Silver
4. construcao da Gold
5. data quality basica

## Arquivos SQL

- `dags/sql/01_silver_vendas.sql`
- `dags/sql/02_gold_faturamento_por_concessionaria.sql`
- `dags/sql/03_gold_performance_vendedores.sql`

## Referência de configuração no Composer

Antes da primeira execucao, configure:

### Airflow Connection

Crie uma connection chamada `novadrive_postgres` do tipo Postgres com:

- host: `159.223.187.110`
- schema/database: `novadrive`
- login: `etlreadonly`
- password: credencial do banco
- port: `5432`

### Airflow Variables

As variaveis abaixo sao opcionais, porque a DAG ja tem defaults para `dev`, mas e recomendado defini-las explicitamente:

- `gcp_project_id`
- `novadrive_bronze_bucket`
- `novadrive_bronze_dataset`
- `novadrive_silver_dataset`
- `novadrive_gold_dataset`
- `novadrive_postgres_conn_id`
- `novadrive_checkpoint_object`
- `novadrive_bronze_load_state_object`

Valores recomendados em `dev`:

- `gcp_project_id = data-platform-copilot-dev`
- `novadrive_bronze_bucket = data-platform-copilot-dev-data-platform-copilot-bronze`
- `novadrive_bronze_dataset = bronze_novadrive`
- `novadrive_silver_dataset = silver_novadrive`
- `novadrive_gold_dataset = gold_novadrive`
- `novadrive_postgres_conn_id = novadrive_postgres`
- `novadrive_checkpoint_object = novadrive/_control/checkpoints.json`
- `novadrive_bronze_load_state_object = novadrive/_control/bronze_load_state.json`

## Publicacao da DAG

Se esta estrutura vier a ser reutilizada em outro ambiente com Composer disponível, publique os arquivos para o bucket do ambiente:

```bash
gcloud storage cp \
  /Users/leandrosantos/Downloads/data-platform-copilot/orchestration/composer/dags/novadrive_medallion_pipeline.py \
  gs://SEU_BUCKET_DO_COMPOSER/dags/
```

```bash
gcloud storage cp \
  /Users/leandrosantos/Downloads/data-platform-copilot/orchestration/composer/dags/sql/*.sql \
  gs://SEU_BUCKET_DO_COMPOSER/dags/sql/
```

## Evolucao recomendada

- mover credenciais da Novadrive para Secret Manager
- parametrizar SQL por ambiente
- adicionar checks de integridade referencial e freshness
- adicionar alertas e observabilidade por tarefa
