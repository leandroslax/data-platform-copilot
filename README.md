# Data Platform Copilot

Data Platform Copilot is a GenAI product for data teams operating on Databricks and GCP.

The project starts as an MVP focused on data discovery, lineage understanding, and pipeline troubleshooting. It is designed to evolve into a product with reproducible infrastructure, governed access, and a clear path to production.

## MVP Goal

Deliver an assistant that can answer questions such as:

- Which table should I use for a given business metric?
- Who owns a dataset?
- What are the upstream and downstream dependencies of a table?
- Why did a Databricks job fail?

## Scope

- Ingest metadata from Databricks
- Process and organize metadata with a medallion model
- Build a retrieval layer for semantic search and grounded answers
- Expose a backend API for chat and metadata lookup
- Provision the GCP foundation with Terraform

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
```

## Planned Architecture

- Sources: Databricks Unity Catalog, Databricks Jobs, notebooks, SQL assets, internal documentation, and selected GCP logs
- Bronze: raw metadata, raw logs, raw technical documents
- Silver: normalized entities such as datasets, jobs, lineage edges, documents, and owners
- Gold: product-ready views, retrieval indexes, and API-facing datasets
- Product layer: API, authentication, feedback, auditability, and future UI integrations

## Next Steps

1. Confirm the MVP entities and source systems.
2. Provision the minimal GCP foundation with Terraform.
3. Implement ingestion for Databricks metadata.
4. Model bronze, silver, and gold datasets.
5. Build the first RAG workflow and API endpoints.
