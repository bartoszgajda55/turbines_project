# Turbines Project
## 1. Infrastructure Setup
```sh
terraform init
# Then
terraform plan --var-file=tfvars/dev.tfvars
# Then
terraform apply --var-file=tfvars/dev.tfvars
``` 