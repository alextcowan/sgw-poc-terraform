terraform {
  required_providers {
    google = {
      source  = "local/hashicorp/google"
      # Ensure this version matches or is compatible with your locally built provider's version.
      version = ">= 6.43.0" # This means 6.43.0 or any newer version is acceptable.
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "global"
}
