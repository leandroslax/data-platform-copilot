variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "Primary GCP region."
  type        = string
  default     = "us-central1"
}

variable "bucket_location" {
  description = "GCS bucket location."
  type        = string
  default     = "US"
}

variable "bigquery_location" {
  description = "BigQuery location."
  type        = string
  default     = "US"
}

variable "bootstrap_image" {
  description = "Container image deployed to Cloud Run."
  type        = string
  default     = "us-central1-docker.pkg.dev/data-platform-copilot-dev/data-platform-copilot/api:latest"
}

variable "enable_composer" {
  description = "Whether to provision the Cloud Composer environment."
  type        = bool
  default     = false
}

variable "composer_environment_name" {
  description = "Cloud Composer environment name for orchestration."
  type        = string
  default     = "novadrive-orchestrator-dev"
}

variable "composer_image_version" {
  description = "Explicit Cloud Composer image version."
  type        = string
  default     = "composer-2.16.1-airflow-2.10.5"
}
