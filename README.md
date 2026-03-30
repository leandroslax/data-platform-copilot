# Data Platform Copilot

Data Platform Copilot is a GenAI-first metadata and operations assistant for teams working on Databricks and GCP.

The current MVP focuses on grounded discovery and troubleshooting workflows for datasets, jobs, lineage, and chat-backed Q&A through a FastAPI backend deployed on Cloud Run.

## Current Status

- FastAPI backend is live on Cloud Run
- Terraform provisions the GCP foundation for the dev environment
- GitHub Actions runs CI and deploys the API on pushes to `main`
- Databricks integration is active for dataset discovery and dataset detail
- Mock fallback remains in place for local development and for endpoints that do not yet have real data available

## What Works Today

### API endpoints

- `GET /api/v1/health`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/{dataset_id}`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}/incidents`
- `GET /api/v1/lineage/{dataset_id}`
- `POST /api/v1/chat`

### Databricks integration

- Real dataset list from Unity Catalog
- Real dataset detail, including columns
- Dev environment currently points to the Databricks `samples` catalog
- Jobs and lineage still support fallback to local mock data when the Databricks workspace does not return usable records

## High-Level Architecture

- Sources: Databricks Unity Catalog, Databricks Jobs, operational metadata, and internal documentation
- Bronze: raw metadata and raw operational signals
- Silver: normalized datasets, jobs, lineage edges, incidents, and documents
- Gold: API-facing views and future retrieval-ready assets
- Product layer: FastAPI services, CI/CD, Terraform-managed infrastructure, and future UI/RAG integrations

See:

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
├── Dockerfile
└── README.md
```

## Environment Variables

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

- If `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are empty, the API falls back to local mock data
- The dev Cloud Run environment is currently configured via Terraform to use the Databricks `samples` catalog

## Local Development

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

Once the server is running:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/datasets
```

## Running With Databricks Locally

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
```

## Testing

API tests:

```bash
python -m pytest tests/api
```

The API tests explicitly clear Databricks environment variables where needed so they can validate mock-backed behavior deterministically.

## CI/CD

### Continuous integration

GitHub Actions CI currently runs:

- Terraform format and validate checks
- repository file checks
- API tests
- Docker build validation

Workflow file:

- [.github/workflows/ci.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/ci.yml)

### Continuous deployment

Pushes to `main` trigger:

- Docker image build
- image push to Artifact Registry
- Cloud Run deployment

Workflow file:

- [.github/workflows/deploy.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/deploy.yml)

## Infrastructure

Terraform for the dev environment provisions:

- required Google APIs
- Artifact Registry repository
- Cloud Storage artifacts bucket
- runtime service account
- Secret Manager secret for Databricks credentials
- Cloud Run service for the API

Main dev stack:

- [infra/terraform/envs/dev/main.tf](/Users/leandrosantos/Downloads/data-platform-copilot/infra/terraform/envs/dev/main.tf)

Apply locally:

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Live Dev API

Current dev Cloud Run endpoint:

- [data-platform-copilot-api-914371024790.us-central1.run.app](https://data-platform-copilot-api-914371024790.us-central1.run.app)

Examples:

```bash
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/health
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/datasets
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/datasets/samples.tpch.orders
curl https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1/jobs
```

## Near-Term Roadmap

- Integrate real lineage where supported by the Databricks workspace
- Integrate real jobs and incidents when workspace jobs exist
- Improve chat grounding over real dataset and operational metadata
- Add retrieval and embeddings pipelines
- Add a product UI on top of the API
