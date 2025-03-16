import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from databricks.connect import DatabricksSession
from turbines.logger import logger

@pytest.fixture(scope="session")
def spark():
    """
    Create a Spark session using Databricks Connect.
    Cluster ID is read from .env file.
    """
    dotenv_file = (
        Path(__file__).parent.parent / ".env"
    )  # Assumes .env file is in the root of the Python project (not whole project)
    if dotenv_file:
        logger.info(f"Loading environment variables from {dotenv_file}")
        load_dotenv(dotenv_file)
    else:
        logger.warning("No .env file found. Testing might not work locally if Env Vars are not set elsewhere.")
    
    cluster_id = os.getenv("CLUSTER_ID")
    if not cluster_id:
        raise ValueError("CLUSTER_ID not found in .env file")
    
    spark = DatabricksSession.builder.clusterId(clusterId=cluster_id).getOrCreate()
    yield spark
    
    spark.stop()