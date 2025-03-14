terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "1.70.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "rg-platform-001"
    storage_account_name = "bg55tfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
    use_azuread_auth     = true
  }
}

locals {
  dbx_account_id = "29e51d61-8494-44d4-91c7-afa5d7aee854"
}

provider "azurerm" {
  features {}
}

provider "databricks" {
  alias      = "account"
  host       = "https://accounts.azuredatabricks.net"
  account_id = local.dbx_account_id
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.product_name}-${var.environment}-001"
  location = var.location

  tags = {
    Environment = var.environment
  }
}

resource "random_string" "random" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-${var.product_name}-${var.environment}-001"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = [var.cidr]
}

resource "azurerm_network_security_group" "nsg" {
  name                = "nsg-${var.product_name}-${var.environment}-001"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_subnet" "public" {
  name                 = "snet-${var.product_name}-${var.environment}-public-001"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [cidrsubnet(var.cidr, 3, 0)]

  delegation {
    name = "databricks"
    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

resource "azurerm_subnet_network_security_group_association" "snet-nsg-public" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_subnet" "private" {
  name                 = "snet-${var.product_name}-${var.environment}-private-001"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [cidrsubnet(var.cidr, 3, 1)]

  delegation {
    name = "databricks"
    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

resource "azurerm_subnet_network_security_group_association" "snet-nsg-private" {
  subnet_id                 = azurerm_subnet.private.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_databricks_workspace" "adb" {
  name                        = "adb-${var.product_name}-${var.environment}-001"
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  sku                         = "premium"
  managed_resource_group_name = "rg-${var.product_name}-${var.environment}-adb-001"

  custom_parameters {
    no_public_ip                                         = var.no_public_ip
    virtual_network_id                                   = azurerm_virtual_network.vnet.id
    private_subnet_name                                  = azurerm_subnet.private.name
    public_subnet_name                                   = azurerm_subnet.public.name
    public_subnet_network_security_group_association_id  = azurerm_subnet_network_security_group_association.snet-nsg-public.id
    private_subnet_network_security_group_association_id = azurerm_subnet_network_security_group_association.snet-nsg-private.id
  }
}

resource "databricks_metastore" "metastore" {
  provider      = databricks.account
  name          = "metastore_azure_northeurope"
  force_destroy = true
  region        = azurerm_resource_group.rg.location
}

resource "databricks_metastore_assignment" "metastore_assignment" {
  provider     = databricks.account
  workspace_id = azurerm_databricks_workspace.adb.workspace_id
  metastore_id = databricks_metastore.metastore.id
}
