import sys
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from turbines.repository import Repository, CsvRepository, DeltaRepository, TableRepository

def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()

def get_catalog_from_params() -> str:
    args = sys.argv
    if len(args) < 2:
        raise ValueError("Catalog name is required")
    return args[1]

class Processor(ABC):
    @abstractmethod
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        pass

class RawToStandardized(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        output_repo.save(df)

class StandardizedToEncriched(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        output_repo.save(df)

class EnrichedToCurated(Processor):
    def process(self, spark: SparkSession, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(spark=spark)
        output_repo.save(df)


def raw_to_standardized():
    catalog = get_catalog_from_params()
    processor = RawToStandardized()
    processor.process(
        get_spark(),
        CsvRepository(path=f"/Volumes/{catalog}/raw/input_turbines/*.csv", header=True, read_kwargs={"schema": "timestamp TIMESTAMP, turbine_id INT, wind_speed DOUBLE, wind_direction INT, power_output DOUBLE"}), 
        DeltaRepository(path=f"/Volumes/{catalog}/standardized/turbines", merge_condition="existing.timestamp = new.timestamp AND existing.turbine_id = new.turbine_id")
    )

def standardized_to_enriched():
    catalog = get_catalog_from_params()
    processor = StandardizedToEncriched()
    processor.process(
        get_spark(),
        DeltaRepository(path=f"/Volumes/{catalog}/standardized/turbines"),
        TableRepository(qualified_name=f"{catalog}.enriched.turbines", merge_condition="existing.timestamp = new.timestamp AND existing.turbine_id = new.turbine_id")
    )

def enriched_to_curated():
    catalog = get_catalog_from_params()
    processor = EnrichedToCurated()
    processor.process(
        get_spark(),
        TableRepository(qualified_name=f"{catalog}.enriched.turbines"),
        TableRepository(qualified_name=f"{catalog}.curated.turbines", merge_condition="existing.timestamp = new.timestamp AND existing.turbine_id = new.turbine_id")
    )
