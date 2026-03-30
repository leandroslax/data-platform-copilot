# Data Platform Copilot

Data Platform Copilot is a GenAI-first data platform product for teams operating on Databricks and GCP.

The platform is designed to help data engineers, analytics engineers, analysts, and platform teams discover trusted datasets, understand lineage, identify ownership, and troubleshoot operational incidents using grounded AI experiences.

## Vision

Build a product-ready copilot for the data platform with strong engineering foundations from day one:

- Infrastructure as Code with Terraform
- CI/CD for validation and deployment
- Medallion architecture for metadata and operational data
- GenAI with retrieval-augmented generation and grounded answers
- Security, observability, and reproducibility as default behaviors

## MVP Goal

Deliver an assistant that can answer questions such as:

- Which table should I use for a given business metric?
- Who owns a dataset?
- What are the upstream and downstream dependencies of a table?
- Why did a Databricks job fail?

## Core Scope

- Ingest metadata from Databricks and selected GCP sources
- Organize platform knowledge with a bronze, silver, and gold model
- Build a retrieval layer for semantic and structured search
- Expose a backend API for chat and metadata lookup
- Provision the GCP foundation with Terraform
- Prepare the repository for CI/CD and future productization

## High-Level Architecture

- Sources: Databricks Unity Catalog, Databricks Jobs, notebooks, SQL assets, internal documentation, and selected GCP logs
- Bronze: raw metadata, raw logs, raw technical documents
- Silver: normalized entities such as datasets, jobs, lineage edges, documents, and owners
- Gold: product-ready views, retrieval indexes, and API-facing datasets
- Product layer: APIs, authentication, feedback, auditability, and future UI integrations

See the detailed architecture in [docs/solution-architecture.md](docs/solution-architecture.md).

## Repository Structure

```text
.
├── app/
│   └── api/
├── docs/
├── infra/
│   └── terraform/
└── pipelines/
    ├── embeddings/
    ├── ingestion/
    └── metadata/
Backend Status
The current FastAPI backend already exposes MVP endpoints for:

datasets
jobs
lineage
chat
health
Repository access follows a hybrid pattern:

use Databricks APIs when DATABRICKS_HOST and DATABRICKS_TOKEN are configured
use local mock data when Databricks is not configured
This hybrid behavior is already implemented for:

dataset repository
job repository
lineage repository
The DatabricksClient currently supports:

Unity Catalog tables
Databricks jobs
Databricks job runs
Databricks lineage
Environment Variables
The backend currently supports these environment variables:

APP_ENV: application environment, defaults to dev
DATABRICKS_HOST: Databricks workspace host, for example https://<workspace>.cloud.databricks.com
DATABRICKS_TOKEN: Databricks personal access token or service token
DATABRICKS_CATALOG: Unity Catalog catalog name, defaults to main
If DATABRICKS_HOST and DATABRICKS_TOKEN are not defined, the API automatically falls back to local mock data for MVP development and tests.

Local Development
Recommended local setup:

Python 3.11
Virtual environment in .venv
Example:

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
