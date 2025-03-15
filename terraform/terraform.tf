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
  backend "azurerm" { # Resource for the backend has to be created manually (unless starting with a local and then migrating)
    resource_group_name  = "rg-platform-001"
    storage_account_name = "bg55tfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
    use_azuread_auth     = true # Access Keys / SAS tokens disabled, for security reasons
  }
}

locals {
  dbx_account_id = "29e51d61-8494-44d4-91c7-afa5d7aee854" # Assumes an Account exists - if creating from scratch, then this value will be present only after first Workspace will be provisioned.
}

provider "azurerm" {
  features {}
}

provider "databricks" {
  alias      = "account"
  host       = "https://accounts.azuredatabricks.net"
  account_id = local.dbx_account_id
}

# Resource Group
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

# Databricks Workspace
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

# Databricks Unity Catalog
resource "databricks_metastore" "metastore" {
  provider      = databricks.account
  name          = "metastore_azure_northeurope"
  region        = azurerm_resource_group.rg.location
  owner         = "G_DATABRICKS_METASTORE_OWNERS"
  force_destroy = true
}

resource "databricks_metastore_assignment" "metastore_assignment" {
  provider     = databricks.account
  workspace_id = azurerm_databricks_workspace.adb.workspace_id
  metastore_id = databricks_metastore.metastore.id
}

resource "azurerm_databricks_access_connector" "access_connector" {
  name                = "ac_${var.product_name}_${var.environment}_001"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "sa" {
  name                     = "sa${var.product_name}${var.environment}001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

resource "azurerm_storage_container" "sc" {
  name                  = "sc${var.product_name}${var.environment}001"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_role_assignment" "sa_rbac" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.access_connector.identity[0].principal_id
}

resource "databricks_storage_credential" "sc" {
  name          = "sc_${var.product_name}_${var.environment}_001"
  force_destroy = true
  force_update  = true
  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.access_connector.id
  }
  depends_on = [
    databricks_metastore_assignment.metastore_assignment
  ]
}

resource "databricks_grants" "sc_grants" {
  storage_credential = databricks_storage_credential.sc.id
  grant {
    principal  = "account users"
    privileges = ["CREATE_EXTERNAL_LOCATION"]
  }
}

resource "databricks_external_location" "el" {
  name            = "el_${var.product_name}_${var.environment}_001"
  url             = "abfss://${azurerm_storage_container.sc.name}@${azurerm_storage_account.sa.name}.dfs.core.windows.net"
  credential_name = databricks_storage_credential.sc.id
  force_destroy   = true
  force_update    = true
  depends_on = [
    databricks_storage_credential.sc
  ]
}

resource "databricks_grants" "el_grants" {
  external_location = databricks_external_location.el.id
  grant {
    principal  = "account users"
    privileges = ["CREATE_MANAGED_STORAGE"]
  }
}

resource "databricks_catalog" "dc" {
  for_each     = { for catalog_name, catalog in var.catalogs : catalog_name => catalog }
  name         = each.key
  storage_root = "abfss://${azurerm_storage_container.sc.name}@${azurerm_storage_account.sa.name}.dfs.core.windows.net"
  comment      = each.value.comment
  depends_on   = [databricks_external_location.el]
}

resource "databricks_grants" "dc_grants" {
  for_each = { for catalog_name, catalog in var.catalogs : catalog_name => catalog }
  catalog  = each.key

  dynamic "grant" {
    for_each = { for principal, grants in each.value.grants : principal => grants }
    content {
      principal  = grant.key
      privileges = grant.value
    }
  }
  depends_on = [databricks_catalog.dc]
}

resource "databricks_schema" "sch" {
  for_each = merge([
    for catalog_name, catalog in var.catalogs :
    {
      for schema_name, schema in catalog.schemas :
      "${catalog_name}-${schema_name}" => {
        catalog_name = catalog_name,
        schema_name  = schema_name
        comment      = schema.comment
      }
    }
  ]...)
  catalog_name = each.value.catalog_name
  name         = each.value.schema_name
  comment      = each.value.comment
  depends_on   = [databricks_catalog.dc]
}

resource "databricks_grants" "sch_grants" {
  for_each = merge([
    for catalog_name, catalog in var.catalogs :
    {
      for schema_name, schema in catalog.schemas :
      "${catalog_name}-${schema_name}" => {
        catalog_name = catalog_name,
        schema_name  = schema_name
        comment      = schema.comment
      }
    }
  ]...)
  schema = databricks_schema.sch[each.key].id
  dynamic "grant" {
    for_each = { for principal, grants in var.catalogs[each.value.catalog_name].schemas[each.value.schema_name].grants : principal => grants }
    content {
      principal  = grant.key
      privileges = grant.value
    }
  }
  depends_on = [databricks_schema.sch]
}

resource "databricks_volume" "vol" {
  for_each = merge(flatten([
    for catalog_name, catalog in var.catalogs : [
      for schema_name, schema in catalog.schemas : [
        for volume_name, volume in schema.volumes : {
          "${catalog_name}-${schema_name}-${volume_name}" = {
            catalog_name = catalog_name
            schema_name  = schema_name
            volume_name  = volume_name
            comment      = volume.comment
          }
        }
      ]
    ]
  ])...)
  name         = each.value.volume_name
  catalog_name = each.value.catalog_name
  schema_name  = each.value.schema_name
  volume_type  = "MANAGED"
  comment      = each.value.comment
  depends_on   = [databricks_schema.sch]
}

resource "databricks_grants" "vol_grants" {
  for_each = merge(flatten([
    for catalog_name, catalog in var.catalogs : [
      for schema_name, schema in catalog.schemas : [
        for volume_name, volume in schema.volumes : [
          for principal, grants in volume.grants : {
            "${catalog_name}-${schema_name}-${volume_name}" = {
              catalog_name = catalog_name
              schema_name  = schema_name
              volume_name  = volume_name
              principal    = principal
              grants       = grants
            }
          }
        ]
      ]
    ]
  ])...)
  volume = databricks_volume.vol[each.key].id
  dynamic "grant" {
    for_each = { for principal, grants in var.catalogs[each.value.catalog_name].schemas[each.value.schema_name].volumes[each.value.volume_name].grants : principal => grants }
    content {
      principal  = grant.key
      privileges = grant.value
    }
  }
  depends_on = [databricks_volume.vol]
}
