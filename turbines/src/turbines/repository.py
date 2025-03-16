from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable

class Repository(ABC):
    @abstractmethod
    def read(self, spark: SparkSession) -> DataFrame:
        pass

    @abstractmethod
    def save(self, df: DataFrame) -> None:
        pass

class CsvRepository(Repository):
    def __init__(self, path: str, header: bool, read_kwargs: dict = None, write_kwargs: dict = None):
        self.path = path
        self.header = header
        self.read_kwargs = read_kwargs or {}
        self.write_kwargs = write_kwargs or {}

    def read(self, spark: SparkSession) -> DataFrame:
        return spark.read.csv(path=self.path, header=self.header, **self.read_kwargs)
    
    def save(self, df: DataFrame) -> None:
        df.write.csv(path=self.path, header=self.header, **self.write_kwargs)

class DeltaRepository(Repository):
    def __init__(self, path: str, merge_condition: str = None):
        self.path = path
        self.merge_condition = merge_condition

    def read(self, spark: SparkSession) -> DataFrame:
        return spark.read.format("delta").load(path=self.path)
    
    def save(self, df: DataFrame) -> None:
        if not DeltaTable.isDeltaTable(sparkSession=df.sparkSession, identifier=self.path):
            df.write.format("delta").save(path=self.path)
            return
        existing = DeltaTable.forPath(sparkSession=df.sparkSession, path=self.path)
        existing.alias("existing").merge(
            source=df.alias("new"),
            condition=self.merge_condition,
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

class TableRepository(Repository):
    def __init__(self, qualified_name: str, merge_condition: str = None):
        self.qualified_name = qualified_name
        self.merge_condition = merge_condition

    def read(self, spark: SparkSession) -> DataFrame:
        return spark.read.table(tableName=self.qualified_name)
    
    def save(self, df: DataFrame) -> None:
        if not df.sparkSession.catalog.tableExists(self.qualified_name):
            df.write.saveAsTable(name=self.qualified_name)
            return
        
        existing = DeltaTable.forName(sparkSession=df.sparkSession, tableOrViewName=self.qualified_name)
        existing.alias("existing").merge(
            source=df.alias("new"),
            condition=self.merge_condition,
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()