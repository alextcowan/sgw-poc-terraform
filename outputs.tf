### SECURITY GATEWAY OUTPUTS
output "security_gateway_id" {
  value       = google_beyondcorp_security_gateway.default.security_gateway_id
}

output "security_gateway_resource" {
  value       = google_beyondcorp_security_gateway.default.id
}

output "security_gateway_delegating_service_account" {
  value       = google_beyondcorp_security_gateway.default.delegating_service_account
}

output "firewall_rule_name" {
  description = "The name of the firewall rule created for the security gateway."
  value       = join("", google_compute_firewall.security_gateway_ingress_firewall_rule.*.name)
}

output "security_gateway_hub_ips" {
  value = {
    for hub in google_beyondcorp_security_gateway.default.hubs :
    hub.region => hub.internet_gateway[0].assigned_ips
  }
}

### GCS BUCKET OUTPUTS
output "bucket_url" {
  value       = google_storage_bucket.public_bucket.url
}

output "object_public_url" {
  value       = "https://storage.googleapis.com/${google_storage_bucket.public_bucket.name}/${google_storage_bucket_object.pac_object.name}"
}


### APPLICATION OUTPUTS
output "applications" {
  value = {
    for key, app in google_beyondcorp_security_gateway_application.application : key => {
      application_id = app.application_id
      display_name   = app.display_name
      full_id        = app.id
      hostnames      = [for matcher in app.endpoint_matchers : matcher.hostname]
    }
  }
}

output "application_iam_policies" {
  value = {
    for key, policy in data.google_iam_policy.policy : key => {
      role    = tolist(policy.binding)[0].role
      members = tolist(policy.binding)[0].members
    }
  }
}