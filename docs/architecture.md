# Architecture Overview

## High-Level Flow

```text
Databricks + GCP + Documentation
              |
              v
      Ingestion Connectors
              |
              v
        Bronze / Silver / Gold
              |
              v
      Retrieval and AI Services
              |
              v
           API Layer
              |
              v
       Product Interfaces
```

## Core Layers

### Source Layer

- Databricks Unity Catalog
- Databricks Jobs
- Databricks notebooks
- SQL assets
- GCP operational logs
- Internal documentation

### Ingestion Layer

- Scheduled metadata extraction jobs
- Incremental sync where possible
- Raw document and log collection

### Knowledge Layer

- Canonical entities: dataset, owner, job, job_run, document, lineage_edge
- Metadata normalization
- Technical document chunking
- Embedding generation pipeline

### Serving Layer

- Backend API for chat and metadata lookup
- Retrieval service for hybrid search
- Prompt assembly and grounded response generation

### Product Layer

- Authentication and authorization
- Conversation history
- User feedback
- Audit and observability

## GCP Foundation

- Cloud Run for backend service
- GCS for artifacts and ingestion exports
- Secret Manager for credentials
- Artifact Registry for container images
- IAM service accounts for workload identity

## Design Principles

- Start lean to respect GCP trial limits
- Keep raw and curated layers separate
- Prefer simple, replaceable infrastructure
- Design for later productization from day one
