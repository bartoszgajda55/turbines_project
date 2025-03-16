from pyspark.sql import DataFrame, SparkSession
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def read(self, spark: SparkSession, path: str, **kwargs) -> DataFrame:
        pass

    @abstractmethod
    def save(self, df: DataFrame, path: str, **kwargs) -> None:
        pass

class CsvRepository(Repository):
    def read(self, spark: SparkSession, path: str, **kwargs) -> DataFrame:
        return spark.read.csv(path, **kwargs)
    
    def save(self, df: DataFrame, path: str, **kwargs) -> None:
        df.write.csv(path, **kwargs)

class DeltaRepository(Repository):
    def read(self, spark: SparkSession, path: str, **kwargs) -> DataFrame:
        return spark.read.format("delta").load(path, **kwargs)
    
    def save(self, df: DataFrame, path: str, **kwargs) -> None:
        df.write.format("delta").save(path, **kwargs)