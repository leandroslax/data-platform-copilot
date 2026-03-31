terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.11"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

data "google_project" "current" {
  project_id = var.project_id
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
    "composer.googleapis.com",
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
      labels      = local.common_labels
    }
    silver_novadrive = {
      description = "Camada silver com dados normalizados do dominio Novadrive."
      labels      = local.common_labels
    }
    gold_novadrive = {
      description = "Camada gold com visoes analiticas e prontas para consumo do copilot."
      labels      = local.common_labels
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

module "composer_service_account" {
  source = "../../modules/service_accounts"

  project_id   = var.project_id
  account_id   = "data-platform-composer-v2"
  display_name = "Data Platform Copilot Composer"
  roles = [
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/composer.worker",
    "roles/logging.logWriter",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
  ]
}

resource "google_service_account_iam_member" "composer_service_agent_extension" {
  provider           = google-beta
  service_account_id = "projects/${var.project_id}/serviceAccounts/${module.composer_service_account.email}"
  role               = "roles/composer.ServiceAgentV2Ext"
  member             = "serviceAccount:service-${data.google_project.current.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "time_sleep" "composer_iam_propagation" {
  count           = var.enable_composer ? 1 : 0
  create_duration = "180s"

  depends_on = [
    module.composer_service_account,
    google_service_account_iam_member.composer_service_agent_extension,
  ]
}

module "composer_environment" {
  count  = var.enable_composer ? 1 : 0
  source = "../../modules/composer_environment"

  providers = {
    google-beta = google-beta
  }

  project_id            = var.project_id
  region                = var.region
  name                  = var.composer_environment_name
  service_account_email = module.composer_service_account.email
  image_version         = var.composer_image_version
  labels                = local.common_labels

  depends_on = [
    module.project_services,
    time_sleep.composer_iam_propagation,
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
    APP_ENV                  = "dev"
    BIGQUERY_PROJECT_ID      = var.project_id
    DATABRICKS_HOST          = "https://8259560804281928.8.gcp.databricks.com"
    DATABRICKS_CATALOG       = "samples"
    NOVADRIVE_GOLD_DATASET   = "gold_novadrive"
    NOVADRIVE_SILVER_DATASET = "silver_novadrive"
  }

  secret_env_vars = {
    DATABRICKS_TOKEN = {
      secret  = "data-platform-copilot-app-config"
      version = "latest"
    }
  }
}
