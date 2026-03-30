variable "project_id" {
  type = string
}

variable "secret_id" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_secret_manager_secret" "this" {
  project   = var.project_id
  secret_id = var.secret_id
  labels    = var.labels

  replication {
    auto {}
  }
}

output "secret_name" {
  value = google_secret_manager_secret.this.name
}
