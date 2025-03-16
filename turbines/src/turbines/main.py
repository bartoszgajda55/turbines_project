from pyspark.sql import SparkSession, DataFrame


def get_taxis(spark: SparkSession) -> DataFrame:
    return spark.read.table("samples.nyctaxi.trips")

def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()

def main():
    get_taxis(get_spark()).show(5)

if __name__ == "__main__":
    main()
