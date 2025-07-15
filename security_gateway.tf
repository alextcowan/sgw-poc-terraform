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

resource "google_beyondcorp_security_gateway_iam_binding" "gw_binding" {
  security_gateway_id = google_beyondcorp_security_gateway.default.security_gateway_id
  role                 = "roles/beyondcorp.securityGatewayUser"
  members = var.access_members
}
