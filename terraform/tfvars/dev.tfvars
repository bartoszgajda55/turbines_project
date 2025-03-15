environment  = "dev"
product_name = "turbines"
catalogs = {
  "dc_turbines_dev_001" = {
    grants = {
      "account users" = ["USE_CATALOG", "CREATE_SCHEMA"]
    }
    comment = "Catalog for the Turbines project, in Dev environment"
    schemas = {
      "platform" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for 'platform' assets, like .whl files"
        volumes = {
          "wheels" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for storing .whl files"
          }
        }
      }
    }
  }
}
