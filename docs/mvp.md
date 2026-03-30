# MVP Definition

## Product Theme

Data Platform Copilot is an assistant for data platform users working with Databricks and GCP.

## Problem

Data teams lose time trying to locate reliable datasets, understand lineage, identify ownership, and troubleshoot failed jobs. This knowledge is often fragmented across technical systems and informal documentation.

## Target Users

- Data Engineers
- Analytics Engineers
- Data Analysts
- Data Platform Operations
- Governance teams

## MVP Capabilities

- Search datasets and technical documentation
- Return schema and ownership details
- Explain basic lineage relationships
- Surface recent job failures and technical context
- Provide grounded answers with cited internal sources

## Initial Data Sources

- Databricks Unity Catalog metadata
- Databricks Jobs runs and execution status
- Databricks notebooks and SQL assets
- Internal documentation in markdown or wiki exports
- Selected GCP logs related to platform operations

## Medallion Design

### Bronze

- Raw catalog extracts
- Raw job execution logs
- Raw notebook exports
- Raw documentation snapshots

### Silver

- Normalized datasets
- Normalized jobs and runs
- Parsed failure events
- Cleaned technical documents
- Canonical lineage edges

### Gold

- Dataset catalog for product queries
- Ownership and lineage summaries
- Incident-oriented job views
- Retrieval-ready chunks and embeddings metadata

## MVP Deliverables

- Terraform bootstrap for the GCP foundation
- Repository structure for application and pipelines
- Metadata model for bronze, silver, and gold
- First API service contract
- First ingestion workflow design
