# Data Platform Copilot

O Data Platform Copilot é um assistente de metadados e operações orientado a GenAI para times que trabalham com Databricks e GCP.

Hoje o projeto já entrega um MVP funcional com:

- backend FastAPI publicado no Cloud Run
- infraestrutura GCP gerenciada com Terraform
- orquestração em evolução com Cloud Composer
- pipeline medalhão da Novadrive em evolução com PostgreSQL, GCS e BigQuery
- CI/CD com GitHub Actions
- frontend demo em React + Vite
- descoberta real de datasets e detalhes de datasets via Databricks
- consultas analíticas reais da Novadrive via BigQuery Gold
- fallback seguro para mock quando uma fonte ainda não está disponível no workspace

## Status Atual

A plataforma já está utilizável de ponta a ponta para demo e validação técnica.

Na infraestrutura `dev`, o backend e os componentes-base já estão provisionados. A camada de orquestração com Cloud Composer está sendo estabilizada no Terraform e passou por troubleshooting de IAM, naming e quota do GKE durante a criação do ambiente.

### Backend

- `GET /api/v1/health`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/{dataset_id}`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}/incidents`
- `GET /api/v1/lineage/{dataset_id}`
- `GET /api/v1/novadrive/faturamento/concessionarias`
- `GET /api/v1/novadrive/performance/vendedores`
- `POST /api/v1/chat`

### O que já está real hoje

- listagem de datasets via Unity Catalog
- detalhe de dataset via Unity Catalog
- colunas reais dos datasets via Unity Catalog
- datasets analíticos da Novadrive materializados em BigQuery
- endpoints reais de faturamento por concessionária e performance de vendedores
- chat respondendo perguntas sobre indicadores da Novadrive
- chat respondendo perguntas sobre datasets explícitos como `samples.tpch.orders`
- chat respondendo owner e colunas de datasets reais

### O que ainda usa fallback

- jobs usam mock quando o workspace Databricks ainda não possui jobs reais
- lineage usa mock quando o workspace Databricks não expõe uma API utilizável
- o chat ainda usa roteamento determinístico e fontes estruturadas, não um fluxo completo com LLM + RAG
- a ingestão da Novadrive ainda está em fase de estabilização operacional no Cloud Composer

## Direção do Produto

A aplicação já é conversacional, mas hoje ela é melhor descrita como um copilot grounded em fase MVP, e não ainda como um assistente totalmente baseado em LLM.

Modelo atual de interação:

- consultas estruturadas em APIs
- roteamento determinístico de intenção
- respostas em linguagem natural geradas a partir de metadados grounded

Evolução desejada:

- pipelines de ingestão de metadados e documentos reais
- camadas bronze, silver e gold normalizadas
- retrieval semântico e embeddings
- síntese com LLM em cima do contexto grounded da plataforma

## Arquitetura de Alto Nível

- Fontes: PostgreSQL da Novadrive, Databricks Unity Catalog, Databricks Jobs, metadados operacionais, documentação interna e futuros sinais da plataforma
- Bronze: dados brutos e alinhados à origem, incluindo extrações da Novadrive em GCS e tabelas bronze no BigQuery
- Silver: entidades normalizadas e enriquecidas, incluindo a tabela `silver_novadrive.vendas`
- Gold: visões analíticas e product-facing, incluindo `gold_novadrive.faturamento_por_concessionaria` e `gold_novadrive.performance_vendedores`
- Camada de produto: serviços FastAPI, frontend React, CI/CD, infraestrutura Terraform, Cloud Composer e futuros fluxos de RAG

## Arquitetura Medalhão

O projeto segue uma arquitetura medalhão para organizar ingestão, curadoria e consumo analítico:

- `Bronze`: preserva a fidelidade da origem e a rastreabilidade da ingestão
- `Silver`: padroniza entidades e aplica regras de negócio
- `Gold`: expõe modelos analíticos e ativos prontos para API e copiloto

Fluxo principal atual da Novadrive:

```text
PostgreSQL Novadrive
        |
        v
Extração incremental no Cloud Composer
        |
        v
GCS Bronze + BigQuery Bronze
        |
        v
BigQuery Silver
        |
        v
BigQuery Gold
        |
        v
FastAPI / Chat / Frontend Demo
```

Camadas e ativos principais da Novadrive:

- `bronze_novadrive`: dados brutos extraídos do PostgreSQL
- `silver_novadrive.vendas`: visão consolidada e normalizada de vendas
- `gold_novadrive.faturamento_por_concessionaria`: agregado analítico por concessionária
- `gold_novadrive.performance_vendedores`: agregado analítico por vendedor

Arquivos relacionados:

- [pipelines/ingestion/novadrive_postgres_ingestion.py](/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/ingestion/novadrive_postgres_ingestion.py)
- [pipelines/ingestion/novadrive_bronze_to_bigquery.py](/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/ingestion/novadrive_bronze_to_bigquery.py)
- [pipelines/metadata/novadrive/01_silver_vendas.sql](/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/metadata/novadrive/01_silver_vendas.sql)
- [pipelines/metadata/novadrive/02_gold_faturamento_por_concessionaria.sql](/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/metadata/novadrive/02_gold_faturamento_por_concessionaria.sql)
- [pipelines/metadata/novadrive/03_gold_performance_vendedores.sql](/Users/leandrosantos/Downloads/data-platform-copilot/pipelines/metadata/novadrive/03_gold_performance_vendedores.sql)

Documentação de referência:

- [docs/mvp.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/mvp.md)
- [docs/architecture.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/architecture.md)
- [docs/solution-architecture.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/solution-architecture.md)
- [docs/data-model.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/data-model.md)
- [docs/api-contract.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/api-contract.md)

## Estrutura do Repositório

```text
.
├── app/
│   └── api/
├── docs/
├── infra/
│   └── terraform/
├── pipelines/
│   ├── embeddings/
│   ├── ingestion/
│   └── metadata/
├── tests/
├── web/
├── Dockerfile
└── README.md
```

## Configuração do Backend

A API lê configuração por variáveis de ambiente:

- `APP_ENV`: ambiente da aplicação, padrão `dev`
- `DATABRICKS_HOST`: host do workspace Databricks
- `DATABRICKS_TOKEN`: token pessoal do Databricks
- `DATABRICKS_CATALOG`: catálogo do Unity Catalog, padrão `main` no código

Exemplo de arquivo local:

```dotenv
APP_ENV=dev
DATABRICKS_HOST=
DATABRICKS_TOKEN=
DATABRICKS_CATALOG=main
```

Observações:

- se `DATABRICKS_HOST` e `DATABRICKS_TOKEN` estiverem vazios, a API faz fallback para mock quando aplicável
- o ambiente `dev` no Cloud Run está configurado via Terraform para usar o catálogo `samples`
- o desenvolvimento local do frontend está habilitado via CORS para portas comuns do Vite como `5173`, `5174` e `4173`

## Desenvolvimento Local do Backend

Setup recomendado:

- Python 3.11
- ambiente virtual em `.venv`

Instalação e execução:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest tests/api
uvicorn app.api.main:app --reload
```

Checks rápidos:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/datasets
curl http://127.0.0.1:8000/api/v1/datasets/samples.tpch.orders
```

## Rodando o Backend com Metadados Reais do Databricks

Para usar metadados reais localmente:

```bash
export APP_ENV=dev
export DATABRICKS_HOST="https://<seu-workspace>.gcp.databricks.com"
export DATABRICKS_TOKEN="<seu-token>"
export DATABRICKS_CATALOG="samples"
uvicorn app.api.main:app --reload
```

Exemplo:

```bash
curl http://127.0.0.1:8000/api/v1/datasets/samples.tpch.orders
curl http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais colunas existem em samples.tpch.orders?"}'
```

## Frontend Demo

Existe um frontend demo em React + Vite em [web/](/Users/leandrosantos/Downloads/data-platform-copilot/web).

Hoje o frontend suporta:

- envio de perguntas no chat
- renderização de resposta
- lista de datasets da API real
- detalhe do dataset com colunas reais
- painel de jobs
- visualização indireta dos indicadores da Novadrive via chat e endpoints da API
- card de destaque para dataset principal

Para rodar localmente:

```bash
cd web
npm install
npm run dev
```

Abrir:

- [http://localhost:5173](http://localhost:5173)

Se o Vite subir em outra porta, confirme que essa origem está liberada no CORS do backend.

## Testes

Testes da API:

```bash
python -m pytest tests/api
```

Cobertura atual inclui:

- comportamento do cliente Databricks
- fluxo de dataset repository e dataset detail
- fallback de jobs
- fallback de lineage
- endpoints e service layer da Novadrive
- roteamento do chat para owner, colunas, jobs e resposta fallback

Os testes do backend limpam variáveis do Databricks quando necessário para manter o comportamento mock determinístico.

## CI/CD

### Integração contínua

O GitHub Actions CI hoje executa:

- `terraform fmt` e `terraform validate`
- checks de arquivos obrigatórios
- testes da API
- validação de build Docker

Workflow:

- [.github/workflows/ci.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/ci.yml)

### Deploy contínuo

Push em `main` dispara:

- build da imagem Docker
- push para o Artifact Registry
- deploy no Cloud Run

Workflow:

- [.github/workflows/deploy.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/deploy.yml)

## Infraestrutura

O Terraform do ambiente `dev` provisiona:

- APIs necessárias do Google Cloud
- repositório no Artifact Registry
- bucket de artefatos no Cloud Storage
- service account de runtime
- service account dedicada ao Cloud Composer
- grant `roles/composer.ServiceAgentV2Ext` para o service agent do Composer
- secret no Secret Manager para credenciais do Databricks
- serviço Cloud Run para a API
- ambiente Cloud Composer para orquestração
- datasets BigQuery `bronze_novadrive`, `silver_novadrive` e `gold_novadrive`

Stack principal:

- [infra/terraform/envs/dev/main.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/envs/dev/main.tf)

Aplicação local:

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Cloud Composer

O ambiente `dev` está sendo preparado para usar Cloud Composer 2 como camada de orquestração.

O pipeline principal já modelado no repositório é o da Novadrive, com extração incremental de PostgreSQL para Bronze e transformação até Silver e Gold.

Mudanças recentes no Terraform:

- criação fixa da service account do Composer em vez de depender de condição implícita
- grant explícito de `roles/composer.ServiceAgentV2Ext` para o service agent do Composer
- espera de propagação de IAM antes da criação do ambiente
- módulo do Composer ajustado para um perfil mais econômico e explícito
- `ENVIRONMENT_SIZE_SMALL`
- `scheduler` pequeno com `count = 1`
- `web_server` pequeno
- `worker` com `min_count = 1` e `max_count = 2`
- `triggerer` desabilitado por enquanto

Ativos do Composer já criados no repositório:

- DAG `novadrive_medallion_pipeline`
- SQLs de Silver e Gold para a Novadrive
- documentação operacional de variables e connection do Composer

Arquivos principais:

- [infra/terraform/envs/dev/main.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/envs/dev/main.tf)
- [infra/terraform/envs/dev/variables.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/envs/dev/variables.tf)
- [infra/terraform/modules/composer_environment/main.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/modules/composer_environment/main.tf)
- [orchestration/composer/README.md](/Users/leandrosantos/Downloads/data-platform-copilot/orchestration/composer/README.md)

## Troubleshooting Recente

Durante a criação do Composer em `us-central1`, os logs indicaram que o problema principal deixou de ser IAM e passou a ser capacidade/quota do GKE/Compute Engine.

Sinais observados:

- `Node scale up ... failed: GCE quota exceeded`
- `Pod didn't trigger scale-up ... in backoff`
- `Too many pods`
- `node(s) didn't match pod anti-affinity rules`
- `ProgressDeadlineExceeded` para `airflow-webserver`, `airflow-scheduler` e `worker-set`

Leitura atual:

- o Terraform e os grants de IAM necessários para o Composer foram alinhados
- o gargalo mais importante passou a ser quota para scale-up de nós durante o provisionamento do ambiente
- quotas prioritárias para revisão em `us-central1`: `INSTANCES`, `CPUS`, `E2_CPUS`, `N2D_CPUS` e `N2A_CPUS`

## Próximos Passos

- concluir o provisionamento do Cloud Composer com quota suficiente
- publicar DAGs em [orchestration/composer/](/Users/leandrosantos/Downloads/data-platform-copilot/orchestration/composer)
- conectar os pipelines de ingestão e metadados ao Composer
- substituir a execução local/manual da Novadrive por execução orquestrada e rastreável
- evoluir de fallback/mock para fluxos orquestrados de ponta a ponta

## Endpoints do Ambiente Dev

Backend atual no Cloud Run:

- [data-platform-copilot-api-914371024790.us-central1.run.app](https://data-platform-copilot-api-914371024790.us-central1.run.app)

Exemplos:

```bash
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/health
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/datasets
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/datasets/samples.tpch.orders
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/jobs
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/lineage/main.sales.orders
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais colunas existem em samples.tpch.orders?"}'
```

## O que já foi implementado

- scaffold inicial do backend com rotas e schemas FastAPI
- cliente Databricks para datasets, detalhe de dataset, jobs e runs
- fallback seguro de fontes reais para mock quando necessário
- integração real com Databricks para datasets e colunas
- endpoints da Novadrive sobre BigQuery Gold
- service layer e repositório da Novadrive para indicadores analíticos
- pipeline medalhão da Novadrive em código, com ingestão PostgreSQL -> Bronze -> Silver -> Gold
- DAG `novadrive_medallion_pipeline` no Composer
- módulos Terraform e ambiente `dev` no GCP
- deploy da API no Cloud Run
- workflows de CI e deploy no GitHub Actions
- frontend demo em React conectado ao backend real
- melhoria do chat para resolver datasets explícitos e responder colunas
- melhoria do chat para responder perguntas sobre indicadores da Novadrive
- suporte local a CORS para desenvolvimento com Vite

## Próximos Passos Sugeridos

- criar o primeiro pipeline real de ingestão para datasets, colunas, owners e descrições
- persistir metadados ingeridos fora das chamadas diretas da API
- expandir o chat para perguntas mais amplas sobre o ambiente, como consultas por owner
- adicionar retrieval semântico e embeddings
- conectar o copilot a um LLM para síntese grounded de respostas
- publicar o frontend demo
