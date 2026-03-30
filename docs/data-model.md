# Data Model

## Purpose

This document defines the initial medallion data model for the Data Platform Copilot MVP.

The goal is to organize metadata, operational events, and technical documentation in a way that supports:

- dataset discovery
- lineage exploration
- ownership lookup
- incident troubleshooting
- retrieval-augmented generation

## Medallion Strategy

The platform uses a medallion architecture with three logical layers:

- Bronze for raw and source-aligned ingestion
- Silver for canonical and normalized entities
- Gold for product-facing and AI-facing views

## Bronze Layer

The bronze layer preserves source fidelity and ingestion traceability.

### `bronze_databricks_tables`

Source:
- Databricks Unity Catalog

Purpose:
- store raw table and view metadata extracted from Databricks

Expected contents:
- catalog name
- schema name
- table name
- object type
- storage location
- comment or description
- created timestamp
- updated timestamp
- ingestion timestamp
- raw payload

### `bronze_databricks_columns`

Source:
- Databricks Unity Catalog

Purpose:
- store raw column metadata for datasets

Expected contents:
- catalog name
- schema name
- table name
- column name
- data type
- nullable flag
- comment
- ordinal position
- ingestion timestamp
- raw payload

### `bronze_databricks_jobs`

Source:
- Databricks Jobs API

Purpose:
- store raw metadata for jobs

Expected contents:
- job id
- job name
- creator
- schedule metadata
- task metadata
- ingestion timestamp
- raw payload

### `bronze_databricks_job_runs`

Source:
- Databricks Jobs API

Purpose:
- store raw execution history for jobs

Expected contents:
- run id
- job id
- lifecycle state
- result state
- start time
- end time
- duration
- error message
- ingestion timestamp
- raw payload

### `bronze_databricks_lineage`

Source:
- Databricks lineage metadata

Purpose:
- store raw upstream and downstream lineage relationships

Expected contents:
- source object
- target object
- relationship type
- ingestion timestamp
- raw payload

### `bronze_documents`

Source:
- markdown files, wiki exports, technical docs

Purpose:
- store raw documentation snapshots used by the copilot

Expected contents:
- document id
- title
- source path
- source type
- content
- last modified timestamp
- ingestion timestamp

### `bronze_gcp_logs`

Source:
- selected GCP operational logs

Purpose:
- store raw logs that may support troubleshooting use cases

Expected contents:
- log source
- severity
- timestamp
- message
- resource metadata
- ingestion timestamp
- raw payload

## Silver Layer

The silver layer standardizes entities and removes source ambiguity.

### `silver_datasets`

Source:
- bronze_databricks_tables
- bronze_databricks_columns

Purpose:
- canonical representation of datasets exposed to product and AI layers

Expected contents:
- dataset id
- full name
- catalog
- schema
- table name
- dataset type
- description
- storage location
- owner id if available
- created timestamp
- updated timestamp

### `silver_dataset_columns`

Source:
- bronze_databricks_columns

Purpose:
- canonical representation of dataset columns

Expected contents:
- dataset id
- column name
- data type
- nullable
- description
- ordinal position

### `silver_jobs`

Source:
- bronze_databricks_jobs

Purpose:
- canonical representation of jobs

Expected contents:
- job id
- job name
- schedule description
- owner
- active flag
- task count
- source system

### `silver_job_runs`

Source:
- bronze_databricks_job_runs

Purpose:
- normalized execution history used for troubleshooting and product metrics

Expected contents:
- run id
- job id
- start timestamp
- end timestamp
- duration seconds
- lifecycle state
- result state
- error summary
- status classification

### `silver_lineage_edges`

Source:
- bronze_databricks_lineage

Purpose:
- normalized lineage graph edges between platform entities

Expected contents:
- source entity id
- source entity type
- target entity id
- target entity type
- relationship type
- lineage source
- observed timestamp

### `silver_documents`

Source:
- bronze_documents

Purpose:
- cleaned and normalized technical documents for search and chunking

Expected contents:
- document id
- title
- source path
- source type
- cleaned content
- content hash
- last modified timestamp

### `silver_document_chunks`

Source:
- silver_documents

Purpose:
- chunked content units prepared for retrieval and embeddings

Expected contents:
- chunk id
- document id
- chunk order
- chunk text
- token estimate
- semantic section label

### `silver_incident_events`

Source:
- silver_job_runs
- bronze_gcp_logs

Purpose:
- normalized incident-oriented events for troubleshooting support

Expected contents:
- incident event id
- related job id
- run id
- severity
- event type
- event timestamp
- event summary
- supporting source

## Gold Layer

The gold layer provides product-facing and GenAI-facing views.

### `gold_dataset_catalog`

Source:
- silver_datasets
- silver_dataset_columns
- silver_documents

Purpose:
- primary dataset discovery view for the product

Expected contents:
- dataset id
- full dataset name
- description
- owner
- key columns summary
- related documentation
- freshness or updated context if available

### `gold_lineage_summary`

Source:
- silver_lineage_edges
- silver_datasets

Purpose:
- summarize upstream and downstream dependencies for product queries

Expected contents:
- dataset id
- upstream datasets
- downstream datasets
- lineage depth indicators
- related jobs if available

### `gold_job_incidents`

Source:
- silver_job_runs
- silver_incident_events
- silver_jobs

Purpose:
- support operational investigation and failure explanation

Expected contents:
- job id
- job name
- latest run status
- latest error summary
- recent failure count
- recent successful run timestamp
- troubleshooting context

### `gold_search_index_metadata`

Source:
- silver_datasets
- silver_documents
- silver_document_chunks
- gold_lineage_summary

Purpose:
- provide retrieval metadata for the GenAI layer

Expected contents:
- entity id
- entity type
- searchable text
- source reference
- ranking attributes
- access scope if needed

## GenAI Usage

The retrieval layer should combine:

- structured queries against gold views
- semantic retrieval over silver document chunks
- lineage and incident context from normalized entities

This allows the copilot to answer with both precision and context.

## Design Notes

- Bronze tables should preserve raw payloads whenever possible.
- Silver entities should define the canonical naming rules of the platform.
- Gold views should be optimized for product use cases, not just technical storage.
- The model should evolve incrementally as new data sources are added.
- Sensitive metadata should be governed before broader rollout.
