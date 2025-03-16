from turbines.utils import get_spark, get_catalog_from_params
from turbines.repository import CsvRepository, DeltaRepository, TableRepository
from turbines.processors import RawToStandardized, StandardizedToEncriched, EnrichedToCurated


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
        TableRepository(qualified_name=f"{catalog}.curated.turbines", merge_condition="existing.date = new.date AND existing.turbine_id = new.turbine_id")
    )
