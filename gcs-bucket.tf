#############################################################################
##
## Create public Google Cloud Storage Bucket and upload PAC file
##
#############################################################################
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
  name = basename(var.pac_file_path)
  bucket = google_storage_bucket.public_bucket.name
  source = var.pac_file_path
  cache_control = "no-cache"
  depends_on = [
    google_storage_bucket_iam_member.public_access
  ]
}
