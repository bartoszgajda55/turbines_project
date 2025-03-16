from pathlib import Path
from turbines.repository import CsvRepository, DeltaRepository, TableRepository

class TestCsvRepository:
    def test_read(self, spark, csv_test_dir):
        # Given
        path = Path(csv_test_dir) / "sample.csv"
        repository = CsvRepository(path=path.as_posix(), header=True)
        # When
        df = repository.read(spark)
        # Then
        assert df.count() == 15
        assert df.columns == ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"]

    def test_save(self, spark, csv_test_dir, test_id):
        # Given
        path = Path(csv_test_dir) / test_id / "output.csv"
        repository = CsvRepository(path=path.as_posix(), header=True)
        sample_data = spark.createDataFrame(
            [
                ("2021-01-01T00:00:00Z", 1, 10.0, 90, 100.0),
                ("2021-01-01T00:00:00Z", 2, 15.0, 180, 200.0),
            ],
            ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"],
        )
        # When
        repository.save(sample_data)
        output = repository.read(spark)
        # Then
        assert output.count() == 2
        # Finally

class TestDeltaRepository:
    def test_read(self, spark, delta_test_dir):
        # Given
        path = Path(delta_test_dir) / "sample"
        repository = DeltaRepository(path=path.as_posix())
        # When
        df = repository.read(spark)
        # Then
        assert df.count() == 15
        assert df.columns == ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"]

    def test_save(self, spark, delta_test_dir, test_id):
        # Given
        path = Path(delta_test_dir) / test_id / "output"
        repository = DeltaRepository(path=path.as_posix())
        sample_data = spark.createDataFrame(
            [
                ("2021-01-01T00:00:00Z", 1, 10.0, 90, 100.0),
                ("2021-01-01T00:00:00Z", 2, 15.0, 180, 200.0),
            ],
            ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"],
        )
        # When
        repository.save(sample_data)
        output = repository.read(spark)
        # Then
        assert output.count() == 2
        # Finally

class TestTableRepository:
    def test_read(self, spark, table_test_dir):
        # Given
        repository = TableRepository(qualified_name=f"{table_test_dir}.table")
        # When
        df = repository.read(spark)
        # Then
        assert df.count() == 15
        assert df.columns == ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"]

    def test_save(self, spark, table_test_dir, test_id):
        # Given
        repository = TableRepository(qualified_name=f"{table_test_dir}.{test_id}")
        sample_data = spark.createDataFrame(
            [
                ("2021-01-01T00:00:00Z", 1, 10.0, 90, 100.0),
                ("2021-01-01T00:00:00Z", 2, 15.0, 180, 200.0),
            ],
            ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"],
        )
        # When
        repository.save(sample_data)
        output = repository.read(spark)
        # Then
        assert output.count() == 2
        # Finally
        spark.sql(f"DROP TABLE IF EXISTS {table_test_dir}.{test_id}")