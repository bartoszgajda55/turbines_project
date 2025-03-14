variable "location" {
  type        = string
  default     = "northeurope"
  description = "Azure region for resources"
}
variable "environment" {
  type        = string
  description = "Environment (dev, qa, or prod)"
}

variable "product_name" {
  type        = string
  description = "Name of the Product - it will be used as a prefix for all resources"
}
variable "cidr" {
  type        = string
  default     = "10.10.0.0/20"
  description = "Network range for created virtual network."
}

variable "no_public_ip" {
  type        = bool
  default     = true
  description = "Defines whether Secure Cluster Connectivity (No Public IP) should be enabled."
}
