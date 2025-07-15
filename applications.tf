#############################################################################
##
## Create Secure Web Gateway Applications and associated access bindings
##
#############################################################################

resource "google_beyondcorp_security_gateway_application" "application" {
  for_each = var.applications

  security_gateway_id = google_beyondcorp_security_gateway.default.security_gateway_id
  application_id       = each.key 
  display_name         = each.value.display_name

 dynamic "endpoint_matchers" {
    for_each = each.value.hostnames
    content {
      hostname = endpoint_matchers.value
    }
  }

  dynamic "upstreams" {
    # Only create upstream for private web apps
    for_each = each.value.is_pwa ? [1] : []

    content {
      network {
        name = var.vpc_network
      }
      #egress_policy { #optional depending on VPC routing
      #  regions = ["us-central1"]
      #}
    }
  }

  depends_on = [google_beyondcorp_security_gateway.default] 
}

resource "google_beyondcorp_application_iam_binding" "binding" {
  for_each = var.applications

  security_gateways_id = google_beyondcorp_security_gateway.default.security_gateway_id
  application_id       = "${each.key}"
  role                 = "roles/beyondcorp.securityGatewayUser"
  members = var.access_members
}
