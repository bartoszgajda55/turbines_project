import os
import uuid
import pytest
from pathlib import Path
from dotenv import load_dotenv
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession
from turbines.logger import logger

@pytest.fixture(scope="session", autouse=True)
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
        raise ValueError("CLUSTER_ID not found in environment - cannot create Spark session.")
    
    spark = DatabricksSession.builder.clusterId(clusterId=cluster_id).getOrCreate()
    yield spark
    
    spark.stop()

@pytest.fixture(scope="session")
def test_id() -> str:
    """
    Generate a unique ID for testing purposes.
    """
    return "test_" + str(uuid.uuid4().hex)

@pytest.fixture(scope="session")
def csv_test_dir(spark: SparkSession) -> str:
    """
    Return the path to the CSV test directory.
    """
    if not (catalog := os.getenv("CATALOG")):
        raise ValueError("CATALOG not found in environment - cannot create test tables.")
    assert spark.catalog.databaseExists(f"{catalog}.test"), "Database 'test' not found in catalog."
    return f"/Volumes/{catalog}/test/csv"

@pytest.fixture(scope="session")
def delta_test_dir(spark: SparkSession) -> str:
    """
    Return the path to the Delta test directory.
    """
    if not (catalog := os.getenv("CATALOG")):
        raise ValueError("CATALOG not found in environment - cannot create test tables.")
    assert spark.catalog.databaseExists(f"{catalog}.test"), "Database 'test' not found in catalog."
    return f"/Volumes/{catalog}/test/delta"

@pytest.fixture(scope="session")
def table_test_dir(spark: SparkSession) -> str:
    """
    Return the schema/database, used for testing tables. This will not return a table name, as this will be
    constant for sample one, and dynamic for these created by test session.
    """
    if not (catalog := os.getenv("CATALOG")):
        raise ValueError("CATALOG not found in environment - cannot create test tables.")
    assert spark.catalog.databaseExists(f"{catalog}.test"), "Database 'test' not found in catalog."
    return f"{catalog}.test"



@pytest.fixture(scope="session")
def setup_testbed(spark: SparkSession, delta_test_dir: str):
    """
    Setup a test objects to be used by SparkSession.
    """
    spark.copyFromLocalToFs("tests/data/sample.csv", delta_test_dir)