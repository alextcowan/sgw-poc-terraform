variable "project_id" {
  type        = string
  description = "The GCP project ID to deploy resources to"
}

variable "security_gateway_id" {
  type        = string
  description = "Admin defined id for SGW creation"
}

variable "display_name" {
  type        = string
  description = "Admin defined display name of SGW"
  default     = "SBC Gateway"
}

variable "region" {
  type        = list(string)
  description = "SGW region(s)"
}

variable "access_members" {
  type        = list(string)
  description = "Groups / Users that will have access to SGW/Apps"
}

variable "vpc_network" {
  type        = string
  description = "Full resource name of VPC network with private web apps access/connectivity"
}

variable "applications" {
  description = "A map of application configurations to be created"
  
  type = map(object({
    display_name = string
    hostnames    = list(string)
    is_pwa     = bool
  }))
}

variable "bucket_region" {
  description = "The GCP region for the storage bucket"
  type        = string
}

variable "bucket_name" {
  description = "The globally unique name for the GCS bucket"
  type        = string
}

variable "pac_file_path" {
  description = "The local path to the pac file to upload"
  type        = string
  default     = "./swg-pac.js"
  #TODO - Add in precondition check for file if on terraform 0.13+
}
