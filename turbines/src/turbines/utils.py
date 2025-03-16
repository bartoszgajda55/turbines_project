import sys
from pyspark.sql import SparkSession

def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()

def get_catalog_from_params() -> str:
    args = sys.argv
    if len(args) < 2:
        raise ValueError("Catalog name is required")
    return args[1]