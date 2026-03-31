output "artifact_registry_repository" {
  value = module.artifact_registry.repository_name
}

output "artifacts_bucket_name" {
  value = module.artifacts_bucket.bucket_name
}

output "bronze_bucket_name" {
  value = module.bronze_bucket.bucket_name
}

output "bigquery_dataset_ids" {
  value = module.bigquery_datasets.dataset_ids
}

output "cloud_run_url" {
  value = module.cloud_run.url
}

output "runtime_service_account_email" {
  value = module.runtime_service_account.email
}

output "composer_service_account_email" {
  value = module.composer_service_account.email
}

output "composer_environment_name" {
  value = try(module.composer_environment[0].name, null)
}

output "composer_airflow_uri" {
  value = try(module.composer_environment[0].airflow_uri, null)
}

output "composer_dag_gcs_prefix" {
  value = try(module.composer_environment[0].dag_gcs_prefix, null)
}
