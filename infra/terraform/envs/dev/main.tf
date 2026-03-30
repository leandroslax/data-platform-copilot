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

module "runtime_service_account" {
  source = "../../modules/service_accounts"

  project_id   = var.project_id
  account_id   = "data-platform-copilot-api"
  display_name = "Data Platform Copilot API"
  roles = [
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
    APP_ENV            = "dev"
    DATABRICKS_HOST    = "https://8259560804281928.8.gcp.databricks.com"
    DATABRICKS_CATALOG = "main"
  }

  secret_env_vars = {
    DATABRICKS_TOKEN = {
      secret  = "data-platform-copilot-app-config"
      version = "latest"
    }
  }
}
