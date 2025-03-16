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
        volumes = {
          "turbines" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for storing standardized Turbines data in Delta format."
          }
        }
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
      "test" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for test objects, used for Unit/Integration tests"
        volumes = {
          "csv" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for sample CSV"
          }
          "delta" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for sample Delta tables"
          }
        }
      }
    }
  }
  "dc_turbines_prod_001" = { # This should be put in prod.tfvars, but given it's sample solution, this is acceptable
    grants = {
      "account users" = ["USE_CATALOG", "CREATE_SCHEMA"]
    }
    comment = "Catalog for the Turbines project, in Prod environment"
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
            comment = "Volume for storing raw data for Turbines project."
          }
        }
      }
      "standardized" = {
        grants = {
          "account users" = ["USE_SCHEMA"]
        }
        comment = "Schema for storing standardized data, which is a raw data, transformed into Delta format."
        volumes = {
          "turbines" = {
            grants = {
              "account users" = ["READ_VOLUME"]
            }
            comment = "Volume for storing standardized Turbines data in Delta format."
          }
        }
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
