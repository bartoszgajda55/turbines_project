from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from turbines.repository import Repository

class Processor(ABC):
    @abstractmethod
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        pass

class RawToStandardized(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        # No transformation needed for now - just saving the data in standardized (Delta) format
        output_repo.save(df)

class StandardizedToEncriched(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        # Calculate mean and standard deviation for each turbine
        stats = df.groupBy("turbine_id").agg(
            F.mean("power_output").alias("mean_power"),
            F.stddev("power_output").alias("stddev_power")
        )
        # Join stats back to original data
        df = df.join(stats, on="turbine_id", how="left")

        # Add columns for upper and lower bounds
        df = df.withColumn("upper_bound", F.col("mean_power") + (2 * F.col("stddev_power")))
        df = df.withColumn("lower_bound", F.col("mean_power") - (2 * F.col("stddev_power")))

        # Flag anomalies
        df = df.withColumn(
            "is_anomaly",
            (F.col("power_output") > F.col("upper_bound")) | 
            (F.col("power_output") < F.col("lower_bound"))
        )
        output_repo.save(df)

class EnrichedToCurated(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        # Convert timestamp to date for daily aggregation
        df = df.withColumn("date", df.timestamp.cast("date"))

        # Group by turbine_id and date, then calculate statistics
        df = df.groupBy("turbine_id", "date").agg(
            F.min("power_output").alias("min_power"),
            F.max("power_output").alias("max_power"),
            F.avg("power_output").alias("avg_power")
        )
        output_repo.save(df)