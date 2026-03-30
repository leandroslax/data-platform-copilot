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

variable "bootstrap_image" {
  description = "Container image deployed to Cloud Run."
  type        = string
  default     = "us-central1-docker.pkg.dev/data-platform-copilot-dev/data-platform-copilot/api:latest"
}
