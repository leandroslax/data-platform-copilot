variable "project_id" {
  type = string
}

variable "location" {
  type = string
}

variable "datasets" {
  type = map(object({
    description                = string
    delete_contents_on_destroy = optional(bool, false)
    labels                     = optional(map(string), {})
  }))
}

resource "google_bigquery_dataset" "this" {
  for_each = var.datasets

  project                    = var.project_id
  dataset_id                 = each.key
  location                   = var.location
  description                = each.value.description
  delete_contents_on_destroy = each.value.delete_contents_on_destroy
  labels                     = each.value.labels
}

output "dataset_ids" {
  value = [for dataset in google_bigquery_dataset.this : dataset.dataset_id]
}
