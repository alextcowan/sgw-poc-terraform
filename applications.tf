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
      ports = lookup(each.value,"ports",[443])
    }
  }

  dynamic "upstreams" {
    # Only create upstream for private web apps
    for_each = each.value.is_pwa ? [1] : []

    content {
      network {
        name = var.vpc_network
      }
      dynamic "egress_policy" {
        for_each = each.value.egress_regions != null ? [1] : []
        content {
          regions = each.value.egress_regions
        }
      }
    }
  }

  depends_on = [google_beyondcorp_security_gateway.default] 
}

data "google_iam_policy" "policy" {
  for_each = var.applications

  binding {
    role    = "roles/beyondcorp.securityGatewayUser"
    members = var.access_members

    dynamic "condition" {
      for_each = each.value.access_level == null ? [] : [each.value]
      content {
        description = "Access level condition for SGW application"
        title = "Security Gateway Access Condition"
        expression  = "'${condition.value.access_level}' in request.auth.access_levels"
      }
    }
  }
}

resource "google_beyondcorp_security_gateway_application_iam_policy" "app_policy" {
  for_each = var.applications

  security_gateway_id = google_beyondcorp_security_gateway.default.security_gateway_id
  application_id      = google_beyondcorp_security_gateway_application.application[each.key].application_id
  policy_data         = data.google_iam_policy.policy[each.key].policy_data
}
