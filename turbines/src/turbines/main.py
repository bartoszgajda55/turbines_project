from abc import ABC, abstractmethod
import sys
from pyspark.sql import SparkSession, DataFrame
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
    def process(self, input_repo: Repository, output_repo: Repository):
        pass

class RawToStandardized(Processor):
    def process(self, input_repo: Repository, output_repo: Repository):
        df = input_repo.read(header=True)
        output_repo.save(df)

class StandardizedToEncriched(Processor):
    def process(self, input_repo: Repository, output_repo: Repository):
        df = input_repo.read()
        output_repo.save(df)

class EnrichedToCurated(Processor):
    def process(self, input_repo: Repository, output_repo: Repository):
        df = input_repo.read()
        output_repo.save(df)


def raw_to_standardized():
    catalog = get_catalog_from_params()
    processor = RawToStandardized()
    processor.process(
        CsvRepository(f"/Volumes/{catalog}/raw/input_turbines/*.csv", header=True), 
        DeltaRepository(f"/Volumes/{catalog}/standardized/turbines")
    )

def standardized_to_enriched():
    catalog = get_catalog_from_params()
    processor = StandardizedToEncriched()
    processor.process(
        DeltaRepository(f"/Volumes/{catalog}/standardized/turbines"),
        TableRepository(f"{catalog}.enriched.turbines")
    )

def enriched_to_curated():
    catalog = get_catalog_from_params()
    processor = EnrichedToCurated()
    processor.process(
        TableRepository(f"{catalog}.enriched.turbines"),
        TableRepository(f"{catalog}.curated.turbines")
    )
