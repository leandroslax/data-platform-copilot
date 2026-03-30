# Data Platform Copilot

Data Platform Copilot is a GenAI-oriented metadata and operations assistant for teams working on Databricks and GCP.

The project currently delivers a working MVP with:

- a FastAPI backend deployed on Cloud Run
- Terraform-managed GCP infrastructure
- GitHub Actions CI/CD
- a React + Vite frontend demo
- real Databricks-backed dataset discovery and dataset detail
- safe mock fallback for sources that are not yet available in the workspace

## Current Status

The platform is already usable end to end for demo and technical validation.

### Backend

- `GET /api/v1/health`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/{dataset_id}`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}/incidents`
- `GET /api/v1/lineage/{dataset_id}`
- `POST /api/v1/chat`

### What is real today

- dataset list comes from Databricks Unity Catalog
- dataset detail comes from Databricks Unity Catalog
- dataset columns come from Databricks Unity Catalog
- chat can answer questions about explicit datasets such as `samples.tpch.orders`
- chat can answer owner and column questions for real datasets

### What still uses fallback logic

- jobs fall back to mock data when the Databricks workspace has no jobs yet
- lineage falls back to mock data when the Databricks workspace does not expose a usable lineage API
- chat still uses deterministic intent handling and structured sources rather than an LLM + RAG pipeline

## Product Direction

The current application is already conversational, but it is best described as a grounded copilot MVP rather than a full LLM-based assistant.

Current interaction model:

- structured API lookups
- deterministic intent routing
- natural-language answers generated from grounded metadata

Target evolution:

- ingestion pipelines for real metadata and documents
- normalized bronze/silver/gold metadata layers
- semantic retrieval and embeddings
- LLM-based synthesis over grounded platform context

## High-Level Architecture

- Sources: Databricks Unity Catalog, Databricks Jobs, operational metadata, internal documentation, and future platform signals
- Bronze: raw metadata and raw operational records
- Silver: normalized datasets, columns, incidents, lineage edges, documents, and owners
- Gold: API-facing views and future retrieval-ready assets
- Product layer: FastAPI services, React frontend, CI/CD, Terraform-managed infrastructure, and future RAG workflows

Reference docs:

- [docs/mvp.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/mvp.md)
- [docs/architecture.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/architecture.md)
- [docs/solution-architecture.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/solution-architecture.md)
- [docs/data-model.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/data-model.md)
- [docs/api-contract.md](/Users/leandrosantos/Downloads/data-platform-copilot/docs/api-contract.md)

## Repository Structure

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

## Backend Configuration

The API reads configuration from environment variables:

- `APP_ENV`: application environment, defaults to `dev`
- `DATABRICKS_HOST`: Databricks workspace host
- `DATABRICKS_TOKEN`: Databricks personal access token
- `DATABRICKS_CATALOG`: Unity Catalog catalog name, defaults to `main` in code

Example local file:

```dotenv
APP_ENV=dev
DATABRICKS_HOST=
DATABRICKS_TOKEN=
DATABRICKS_CATALOG=main
```

Notes:

- if `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are empty, the API falls back to local mock data where applicable
- the current dev Cloud Run environment is configured via Terraform to use the Databricks `samples` catalog
- local frontend development is enabled via CORS for common Vite ports such as `5173`, `5174`, and `4173`

## Local Backend Development

Recommended setup:

- Python 3.11
- virtual environment in `.venv`

Install and run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest tests/api
uvicorn app.api.main:app --reload
```

Sanity checks:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/datasets
curl http://127.0.0.1:8000/api/v1/datasets/samples.tpch.orders
```

## Running the Backend With Real Databricks Metadata

To use real Databricks metadata locally:

```bash
export APP_ENV=dev
export DATABRICKS_HOST="https://<your-workspace>.gcp.databricks.com"
export DATABRICKS_TOKEN="<your-token>"
export DATABRICKS_CATALOG="samples"
uvicorn app.api.main:app --reload
```

Example:

```bash
curl http://127.0.0.1:8000/api/v1/datasets/samples.tpch.orders
curl http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais colunas existem em samples.tpch.orders?"}'
```

## Frontend Demo

A React + Vite frontend demo now lives in [web/](/Users/leandrosantos/Downloads/data-platform-copilot/web).

The frontend currently supports:

- chat prompt and answer rendering
- dataset list from the live API
- dataset detail with real columns
- jobs snapshot panel
- highlighted featured dataset card

Start locally:

```bash
cd web
npm install
npm run dev
```

Open:

- [http://localhost:5173](http://localhost:5173)

If Vite chooses another port, make sure the backend CORS list includes that local origin.

## Testing

Backend API tests:

```bash
python -m pytest tests/api
```

Current test coverage includes:

- Databricks client behavior
- dataset repository and detail flows
- jobs fallback behavior
- lineage fallback behavior
- chat routing for dataset owner, columns, jobs, and fallback answers

The backend tests explicitly clear Databricks environment variables where needed so mock-backed behavior remains deterministic.

## CI/CD

### Continuous integration

GitHub Actions CI currently runs:

- Terraform format and validate checks
- repository file checks
- API tests
- Docker build validation

Workflow:

- [.github/workflows/ci.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/ci.yml)

### Continuous deployment

Pushes to `main` trigger:

- Docker image build
- image push to Artifact Registry
- Cloud Run deployment

Workflow:

- [.github/workflows/deploy.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/deploy.yml)

## Infrastructure

Terraform for the dev environment provisions:

- required Google APIs
- Artifact Registry repository
- Cloud Storage artifacts bucket
- runtime service account
- Secret Manager secret for Databricks credentials
- Cloud Run service for the API

Main stack:

- [infra/terraform/envs/dev/main.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/envs/dev/main.tf)

Apply locally:

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Live Dev Endpoints

Current Cloud Run backend:

- [data-platform-copilot-api-914371024790.us-central1.run.app](https://data-platform-copilot-api-914371024790.us-central1.run.app)

Examples:

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

## What Has Been Implemented So Far

- initial backend scaffold with FastAPI routes and schemas
- Databricks client for datasets, dataset detail, jobs, and runs
- safe fallback from real sources to mock data where needed
- real Databricks integration for datasets and columns
- Terraform modules and dev environment for GCP
- Cloud Run deployment of the API
- GitHub Actions CI and deploy workflow
- React frontend demo connected to the live backend
- chat improvement for explicit dataset resolution and column answers
- local CORS support for Vite development

## Suggested Next Steps

- build the first real ingestion pipeline for datasets, columns, owners, and descriptions
- persist ingested metadata outside direct API calls
- expand chat to support broader environment questions such as owner-based discovery
- add semantic retrieval and embeddings
- connect the copilot to an LLM for grounded answer synthesis
- publish the frontend demo
