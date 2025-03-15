import os
import pytest
from dotenv import load_dotenv
from databricks.connect import DatabricksSession

@pytest.fixture(scope="session")
def spark():
    """
    Create a Spark session using Databricks Connect.
    Cluster ID is read from .env file.
    """
    load_dotenv()
    
    cluster_id = os.getenv("INTERACTIVE_CLUSTER_ID")
    if not cluster_id:
        raise ValueError("INTERACTIVE_CLUSTER_ID not found in .env file")
    
    spark = DatabricksSession.builder.clusterId(clusterId=cluster_id).getOrCreate()
    yield spark
    
    spark.stop()