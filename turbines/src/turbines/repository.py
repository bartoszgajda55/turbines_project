from pyspark.sql import DataFrame, SparkSession
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def read(self, spark: SparkSession, **kwargs) -> DataFrame:
        pass

    @abstractmethod
    def save(self, df: DataFrame, **kwargs) -> None:
        pass

class CsvRepository(Repository):
    def __init__(self, path: str, header: bool = False):
        self.path = path
        self.header = header

    def read(self, spark: SparkSession, **kwargs) -> DataFrame:
        return spark.read.csv(path=self.path, header=self.header, **kwargs)
    
    def save(self, df: DataFrame, **kwargs) -> None:
        df.write.csv(path=self.path, header=self.header, **kwargs)

class DeltaRepository(Repository):
    def __init__(self, path: str):
        self.path = path

    def read(self, spark: SparkSession, **kwargs) -> DataFrame:
        return spark.read.format("delta").load(path=self.path, **kwargs)
    
    def save(self, df: DataFrame, **kwargs) -> None:
        df.write.format("delta").save(path=self.path, **kwargs)

class TableRepository(Repository):
    def __init__(self, qualified_name: str):
        self.qualified_name = qualified_name

    def read(self, spark: SparkSession, **kwargs) -> DataFrame:
        return spark.read.table(tableName=self.qualified_name)
    
    def save(self, df: DataFrame, **kwargs) -> None:
        df.write.saveAsTable(name=self.qualified_name, **kwargs)