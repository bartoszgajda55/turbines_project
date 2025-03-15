# Turbines Project
## 1. Introduction

## 2. Infrastructure Setup
```sh
terraform init
# Then
terraform plan --var-file=tfvars/dev.tfvars
# Then
terraform apply --var-file=tfvars/dev.tfvars
```

## 3. Development Setup
```sh
databricks auth login --host <host>
```