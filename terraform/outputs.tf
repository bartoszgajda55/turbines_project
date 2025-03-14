output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.adb.workspace_url
}
output "databricks_host" {
  value = "https://${azurerm_databricks_workspace.adb.workspace_url}/"
}
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}
