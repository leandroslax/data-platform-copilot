output "artifact_registry_repository" {
  value = module.artifact_registry.repository_name
}

output "artifacts_bucket_name" {
  value = module.artifacts_bucket.bucket_name
}

output "cloud_run_url" {
  value = module.cloud_run.url
}

output "runtime_service_account_email" {
  value = module.runtime_service_account.email
}
