# Observability Stack

Esta pasta adiciona uma camada local de observabilidade para o projeto com:

- `Prometheus` para coleta de métricas
- `Grafana` para dashboards
- `cAdvisor` para métricas dos containers Docker
- `postgres-exporter` para métricas do metadata DB do Airflow

## O que é monitorado

- containers do Airflow local
- Postgres do metadata DB
- API FastAPI local via endpoint `/metrics`

## URLs locais

- Grafana: [http://localhost:3000](http://localhost:3000)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- cAdvisor: [http://localhost:8083](http://localhost:8083)

Credenciais padrão do Grafana:

- usuário: `admin`
- senha: `admin`

## Como subir

Suba primeiro a API local com métricas:

```bash
cd /Users/leandrosantos/Downloads/data-platform-copilot
source .venv/bin/activate
uvicorn app.api.main:app --reload
```

Depois suba a stack do Airflow com observabilidade:

```bash
cd /Users/leandrosantos/Downloads/data-platform-copilot/orchestration/airflow
docker compose up -d
```

O Prometheus vai coletar a API local em:

- `host.docker.internal:8000/metrics`

## Dashboard provisionado

O Grafana sobe com um dashboard inicial:

- `Data Platform Copilot Overview`
- `Visão Executiva da Novadrive`
- `Qualidade de Dados e Pipeline da Novadrive`

Ele mostra:

- disponibilidade da FastAPI
- disponibilidade do exporter do Postgres
- throughput da API
- latência média da API
- row count de `silver_novadrive.vendas`
- row count dos marts `gold_novadrive`
- última ingestão observada em `silver_novadrive.vendas`
- faturamento total agregado nos marts Gold
- uso dos endpoints da API, chat e Novadrive
- visão dedicada da Novadrive com volume, freshness, receita e tráfego de endpoints
- dashboard executivo da Novadrive para receita, geografia, ranking comercial e ticket médio
- dashboard separado de qualidade e pipeline para freshness, duplicidade, snapshots diários e consumo operacional
