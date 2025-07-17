#############################################################################
##
## Create public Google Cloud Storage Bucket and upload PAC file
##
#############################################################################

locals {
  all_hostnames = flatten([
    for app in values(var.applications) : app.hostnames
  ])

  pac_sites_list_string = join(", ", [
    for hostname in local.all_hostnames : "\"${hostname}\""
  ])
}

resource "google_storage_bucket" "public_bucket" {
  name     = var.bucket_name
  location = var.bucket_region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "public_access" {
  bucket = google_storage_bucket.public_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_object" "pac_object" {
  name = "sgw-pac.js"
  bucket = google_storage_bucket.public_bucket.name
  
  content = templatefile("${path.module}/sgw-pac.js.tpl", {
    sites_list = local.pac_sites_list_string
  })

  content_type = "text/javascript"

  cache_control = "no-cache"
  depends_on = [
    google_storage_bucket_iam_member.public_access
  ]
}
