import os
import pytest
from dotenv import load_dotenv
from databricks.connect import DatabricksSession
from turbines.logger import logger

@pytest.fixture(scope="session")
def spark():
    """
    Create a Spark session using Databricks Connect.
    Cluster ID is read from .env file.
    """
    logger.info("Loading environment variables from .env file")
    load_dotenv()
    
    cluster_id = os.getenv("CLUSTER_ID")
    if not cluster_id:
        raise ValueError("CLUSTER_ID not found in Env Variables. Set it in .env file (if locally) or in the GH Variables (if run in Actions).")
    
    spark = DatabricksSession.builder.clusterId(clusterId=cluster_id).getOrCreate()
    yield spark
    
    spark.stop()