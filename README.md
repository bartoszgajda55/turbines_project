# Turbines Project
## 1. Introduction
This is a source code for the Turbines project - an assignment to provide a full-featured Data Solution to the processing of data from wind turbines.

### 1.1 Technical Stack
The project utilizes the following technical solutions:

- **Azure Databricks**: Main compute platform for data processing
- **Unity Catalog**: Data governance and management layer
- **Terraform**: Infrastructure as Code for resource provisioning
- **Databricks Asset Bundles (DABs)**: Package management and deployment solution
- **GitHub Actions**: CI/CD automation for DAB deployments
- **Python**: Primary programming language for data processing
- **SemVer**: Version control strategy for releases

The solution follows a multi-environment architecture (dev/prod) with separate Unity Catalog spaces for isolation.

### 1.2 Data Layers
The solution implements a multi-layer data architecture:

1. **Standardized Layer (Bronze)**
    - Raw ingestion of turbine sensor data in delta format
    - Schema enforcement with mandatory fields: id, timestamp, value
    - Data validation for numeric ranges
    - Partitioned by ingestion_date

2. **Enriched Layer (Silver)**
    - Quality-checked data with valid readings
    - Timestamp normalization to UTC
    - Derived metrics: power_output, efficiency_score
    - Deduplication based on id and timestamp
    - Error detection flags

3. **Curated Layer (Gold)**
    - Hourly and daily aggregations
    - Performance metrics by turbine
    - Efficiency calculations and thresholds
    - Z-score anomaly detection
    - Optimized for business intelligence queries

### 1.3 Incremental Processing
The solution supports incremental data processing through the use of Delta Lake's Merge operations, which facilitate upsert patterns. This approach ensures that only new or changed data is processed and stored, optimizing performance and resource usage.

When saving data, the system checks if the target location (either a Delta table or a managed table) already exists. If it does not exist, the data is written as a new table. If the table does exist, a merge operation is performed. This merge operation updates existing records and inserts new records based on a specified condition, ensuring that only the incremental changes are applied. This method is implemented in both the Delta and managed table repositories, ensuring consistent incremental processing across different storage formats.

### 1.4 Event-Based Triggering
The data processing pipeline is triggered automatically through file arrival events in the raw data storage location. This event-driven architecture ensures:

- **Online Processing**: Immediate data processing when new files arrive
- **Resource Efficiency**: Compute resources are utilized only when needed
- **Scalability**: Automatic handling of varying data volumes
- **Error Recovery**: Failed processing attempts are automatically retried
- **Monitoring**: Event logs for tracking processing status and latency

The system uses Databricks File Event Trigger to monitor data storage and trigger workflows automatically. When new files arrive in the monitored locations, the trigger initiates the processing pipeline, enabling real-time data ingestion with configurable batch windows for optimal performance.


## 2. Infrastructure Setup
In order to start using this project, first some infrastructure will be needed. The basic ones for working has already been defined in the folder `terraform` and can be deployed using the following commands:
```sh
terraform init
# Then
terraform plan --var-file=tfvars/dev.tfvars
# Then
terraform apply --var-file=tfvars/dev.tfvars
```

**Note:** the above commands will work if you are already logged in to Azure CLI and privileged enough to provision these resources. Additionally, the backend for the Terraform is configured to use Azure Storage - this you will have to create manually before running `init`, in order to successfully initalize it. 

## 3. Development Setup
To work with Databricks Connect (for which this project has been setup), you will need to connect to Databricks, using command like:
```sh
databricks auth login --host <host>
```

Alternatively, you can also use other Auth methods, like PATs.

In addition to above, you will also need to setup the `.env` file, as the following parameters are expected:
```
CLUSTER_ID=123-456
CATALOG=uc_catalog_dev_001
```
First is the ID of cluster to which attach Spark Session - interactive cluster will do just fine.
Second is for catalog on which code should be executed. Assumption taken is that there are separate catalogs per-env, so process isolation is done at this level.

## 4. Using Tags to Publish DABs
The DABs deployment has been automated with GitHub Action pipelines, which are triggered whenever an expected Git Tag is pushed to ref. You can deploy the DAB using the below commands:
```sh
# On feature branch
git tag v0.3.0-rc9
# And then
git push origin v0.3.0-rc9
```

When publishing from `main` branch, then use SemVer tags, without any annotations, like following:
```sh
git tag v0.3.0
```

**Note:** when publishing tag on `main` branch, then the DABs will be deployed in `prod` mode.