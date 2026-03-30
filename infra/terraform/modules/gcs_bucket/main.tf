variable "project_id" {
  type = string
}

variable "bucket_name" {
  type = string
}

variable "location" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "force_destroy" {
  type    = bool
  default = false
}

resource "google_storage_bucket" "this" {
  project       = var.project_id
  name          = var.bucket_name
  location      = var.location
  force_destroy = var.force_destroy
  labels        = var.labels

  uniform_bucket_level_access = true
}

output "bucket_name" {
  value = google_storage_bucket.this.name
}
