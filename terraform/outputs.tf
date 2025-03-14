output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.adb.workspace_url
}
output "databricks_host" {
  value = "https://${azurerm_databricks_workspace.adb.workspace_url}/"
}
