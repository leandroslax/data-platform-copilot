terraform {
  required_providers {
    google-beta = {
      source = "hashicorp/google-beta"
    }
  }
}

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "name" {
  type = string
}

variable "service_account_email" {
  type = string
}

variable "image_version" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_composer_environment" "this" {
  provider = google-beta
  project  = var.project_id
  region   = var.region
  name     = var.name
  labels   = var.labels

  config {
    software_config {
      image_version = var.image_version
    }

    # Use an explicit low-cost baseline instead of relying on provider defaults.
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    workloads_config {
      scheduler {
        count      = 1
        cpu        = 0.5
        memory_gb  = 1.875
        storage_gb = 1
      }

      web_server {
        cpu        = 0.5
        memory_gb  = 1.875
        storage_gb = 1
      }

      worker {
        min_count  = 1
        max_count  = 2
        cpu        = 0.5
        memory_gb  = 1
        storage_gb = 1
      }

      triggerer {
        count     = 0
        cpu       = 0.5
        memory_gb = 0.5
      }
    }

    node_config {
      service_account = var.service_account_email
    }
  }
}

output "name" {
  value = google_composer_environment.this.name
}

output "dag_gcs_prefix" {
  value = google_composer_environment.this.config[0].dag_gcs_prefix
}

output "airflow_uri" {
  value = google_composer_environment.this.config[0].airflow_uri
}
