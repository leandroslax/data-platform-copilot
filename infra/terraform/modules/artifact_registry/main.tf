variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "repository_id" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_id
  description   = "Container images for Data Platform Copilot"
  format        = "DOCKER"
  labels        = var.labels
}

output "repository_name" {
  value = google_artifact_registry_repository.this.name
}
