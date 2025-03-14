# Turbines Project
## 1. Infrastructure Setup
```sh
terraform init
# Then
terraform plan --var-file=tfvars/dev.tfvars
# Then
terraform apply --var-file=tfvars/dev.tfvars
```

## 2. Development Setup
```sh
databricks auth login --host https://adb-1402730492326749.9.azuredatabricks.net
```