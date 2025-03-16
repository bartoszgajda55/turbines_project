from pathlib import Path
from turbines.repository import CsvRepository, DeltaRepository

class TestCsvRepository:
    def test_read(self, spark, csv_test_dir):
        # Given
        repository = CsvRepository()
        path = Path(csv_test_dir) / "sample.csv"
        # When
        df = repository.read(spark, path.as_posix(), header=True)
        # Then
        assert df.count() == 15
        assert df.columns == ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"]

    def test_save(self, spark, csv_test_dir, test_id):
        # Given
        repository = CsvRepository()
        path = Path(csv_test_dir) / test_id / "output.csv"
        sample_data = spark.createDataFrame(
            [
                ("2021-01-01T00:00:00Z", 1, 10.0, 90, 100.0),
                ("2021-01-01T00:00:00Z", 2, 15.0, 180, 200.0),
            ],
            ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"],
        )
        # When
        repository.save(sample_data, path.as_posix(), header=True)
        output = repository.read(spark, path.as_posix(), header=True)
        # Then
        assert output.count() == 2
        # Finally

class TestDeltaRepository:
    def test_read(self, spark, delta_test_dir):
        # Given
        repository = DeltaRepository()
        path = Path(delta_test_dir) / "sample"
        # When
        df = repository.read(spark, path.as_posix())
        # Then
        assert df.count() == 15
        assert df.columns == ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"]

    def test_save(self, spark, delta_test_dir, test_id):
        # Given
        repository = DeltaRepository()
        path = Path(delta_test_dir) / test_id / "output"
        sample_data = spark.createDataFrame(
            [
                ("2021-01-01T00:00:00Z", 1, 10.0, 90, 100.0),
                ("2021-01-01T00:00:00Z", 2, 15.0, 180, 200.0),
            ],
            ["timestamp", "turbine_id", "wind_speed", "wind_direction", "power_output"],
        )
        # When
        repository.save(sample_data, path.as_posix())
        output = repository.read(spark, path.as_posix())
        # Then
        assert output.count() == 2
        # Finally