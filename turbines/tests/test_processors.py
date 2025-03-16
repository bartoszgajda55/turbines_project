import pytest
from datetime import datetime
from turbines.processors import RawToStandardized, StandardizedToEncriched, EnrichedToCurated
from turbines.repository import Repository

@pytest.fixture
def sample_data(spark):
    data = [
        ("1", datetime(2022, 3, 1, 0, 0, 0), 4.0),
        ("1", datetime(2022, 3, 1, 0, 0, 0), 2.5),
        ("2", datetime(2022, 3, 1, 0, 0, 0), 3.1),
        ("2", datetime(2022, 3, 1, 0, 0, 0), 1.8),
    ]
    return spark.createDataFrame(data, schema="turbine_id STRING, timestamp TIMESTAMP, power_output DOUBLE")

class FakeRepository(Repository):
    def __init__(self, df=None):
        self.df = df
        self.saved_df = None
    
    def read(self, spark):
        return self.df
        
    def save(self, df):
        self.saved_df = df

class TestProcessors:
    def test_raw_to_standardized(spark, sample_data):
        # Given
        input_repo = FakeRepository(sample_data)
        output_repo = FakeRepository()
        processor = RawToStandardized()
        # When
        processor.process(spark, input_repo, output_repo)
        # Then
        assert output_repo.saved_df.count() == sample_data.count()

    def test_standardized_to_enriched(spark, sample_data):
        # Given
        input_repo = FakeRepository(sample_data)
        output_repo = FakeRepository()
        processor = StandardizedToEncriched()
        # When
        processor.process(spark, input_repo, output_repo)
        result_df = output_repo.saved_df
        # Then
        assert "mean_power" in result_df.columns
        assert "stddev_power" in result_df.columns
        assert "is_anomaly" in result_df.columns
        assert result_df.count() == sample_data.count()

    def test_enriched_to_curated(spark, sample_data):
        # Given
        input_repo = FakeRepository(sample_data)
        output_repo = FakeRepository()
        processor = EnrichedToCurated()
        # When
        processor.process(spark, input_repo, output_repo)
        result_df = output_repo.saved_df
        # Then
        assert "min_power" in result_df.columns
        assert "max_power" in result_df.columns
        assert "avg_power" in result_df.columns
        assert result_df.count() == 2  # Should be grouped by date and turbine_id
