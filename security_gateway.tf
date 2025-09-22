locals {
  pwa_app_exists = length([for app in var.applications : app if app.is_pwa]) > 0
}

#############################################################################
##
## Create Secure Web Gateway Instance, firewall rule, and IAM binding
##
#############################################################################
resource "google_beyondcorp_security_gateway" "default" {
  security_gateway_id = var.security_gateway_id
  display_name        = var.display_name

  dynamic "hubs" {
    for_each = var.region
    content {
      region = hubs.value
    }
  }
}

resource "google_project_iam_member" "gateway_upstream_access_service_account_iam_binding" {
  project = var.project_id
  role    = "roles/beyondcorp.upstreamAccess"
  member  = "serviceAccount:${google_beyondcorp_security_gateway.default.delegating_service_account}"
}

resource "google_compute_firewall" "security_gateway_ingress_firewall_rule" {
  count   = local.pwa_app_exists ? 1 : 0
  name    = "security-gateway-ingress-firewall-rule"
  network = var.vpc_network
  source_ranges = [
    "34.158.8.0/21",
    "136.124.16.0/20"
  ]
  allow {
    protocol = "all"
  }
}