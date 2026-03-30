terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  common_labels = {
    project     = "data-platform-copilot"
    environment = "dev"
    managed_by  = "terraform"
  }
}

module "project_services" {
  source = "../../modules/project_services"

  project_id = var.project_id
  services = [
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
  ]
}

module "artifact_registry" {
  source = "../../modules/artifact_registry"

  project_id    = var.project_id
  region        = var.region
  repository_id = "data-platform-copilot"
  labels        = local.common_labels
}

module "artifacts_bucket" {
  source = "../../modules/gcs_bucket"

  project_id    = var.project_id
  bucket_name   = "${var.project_id}-data-platform-copilot-artifacts"
  location      = var.bucket_location
  labels        = local.common_labels
  force_destroy = false
}

module "bronze_bucket" {
  source = "../../modules/gcs_bucket"

  project_id    = var.project_id
  bucket_name   = "${var.project_id}-data-platform-copilot-bronze"
  location      = var.bucket_location
  labels        = local.common_labels
  force_destroy = false
}

module "bigquery_datasets" {
  source = "../../modules/bigquery_dataset"

  project_id = var.project_id
  location   = var.bigquery_location
  datasets = {
    bronze_novadrive = {
      description = "Camada bronze com dados brutos do PostgreSQL Novadrive."
      labels       = local.common_labels
    }
    silver_novadrive = {
      description = "Camada silver com dados normalizados do dominio Novadrive."
      labels       = local.common_labels
    }
    gold_novadrive = {
      description = "Camada gold com visoes analiticas e prontas para consumo do copilot."
      labels       = local.common_labels
    }
  }
}

module "runtime_service_account" {
  source = "../../modules/service_accounts"

  project_id   = var.project_id
  account_id   = "data-platform-copilot-api"
  display_name = "Data Platform Copilot API"
  roles = [
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/logging.logWriter",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectViewer",
  ]
}

module "app_config_secret" {
  source = "../../modules/secret_manager"

  project_id = var.project_id
  secret_id  = "data-platform-copilot-app-config"
  labels     = local.common_labels
}

module "cloud_run" {
  source = "../../modules/cloud_run"

  project_id            = var.project_id
  region                = var.region
  service_name          = "data-platform-copilot-api"
  image                 = var.bootstrap_image
  service_account_email = module.runtime_service_account.email
  labels                = local.common_labels

  env_vars = {
    APP_ENV                = "dev"
    BIGQUERY_PROJECT_ID    = var.project_id
    DATABRICKS_HOST        = "https://8259560804281928.8.gcp.databricks.com"
    DATABRICKS_CATALOG     = "samples"
    NOVADRIVE_GOLD_DATASET = "gold_novadrive"
    NOVADRIVE_SILVER_DATASET = "silver_novadrive"
  }

  secret_env_vars = {
    DATABRICKS_TOKEN = {
      secret  = "data-platform-copilot-app-config"
      version = "latest"
    }
  }
}
