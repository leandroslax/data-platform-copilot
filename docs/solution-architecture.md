# Solution Architecture

## Purpose

Data Platform Copilot is a GenAI product designed to improve data discovery, lineage understanding, operational troubleshooting, and platform knowledge access for teams working with Databricks and GCP.

The solution must be built with product-grade engineering practices from the beginning so it can evolve from MVP to a production-ready internal platform.

## Engineering Principles

- Infrastructure must be provisioned with Terraform.
- Environments must be reproducible and version-controlled.
- CI/CD must validate infrastructure and application changes before deployment.
- Data must be modeled with a medallion architecture.
- AI responses must be grounded in trusted internal sources.
- Security, observability, and auditability must be built into the platform.
- Components should be modular and replaceable as the product evolves.

## Target Capabilities

The platform should support these initial product capabilities:

- Dataset discovery
- Ownership lookup
- Lineage exploration
- Job and pipeline troubleshooting
- Grounded conversational answers with source attribution

## Architecture Overview

```text
Databricks + GCP + Documentation + Git
                  |
                  v
         Ingestion and Connectors
                  |
                  v
          Bronze / Silver / Gold
                  |
                  v
      Retrieval, Search, and GenAI Layer
                  |
                  v
             API and Product Layer
                  |
                  v
        Web UI / Chat UI / Integrations

