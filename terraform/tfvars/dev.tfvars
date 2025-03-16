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
      "raw" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for raw data"
        volumes = {
          "input_turbines" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for storing raw data for Turbines project"
          }
        }
      }
      "standardized" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for storing standardized data, which is a raw data, transformed into Delta format."
      }
      "enriched" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for enriched data, which is standardized data, with some level of aggregation applied."
      }
      "curated" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for curated data, which is enriched data, transformed to the final format, ready for consumption."
      }
    }
  }
}
