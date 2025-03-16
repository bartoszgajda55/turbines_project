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

## 2. Development and Test Setup
### 2.1 Infrastructure Setup
In order to start using this project, first some infrastructure will be needed. The basic ones for working has already been defined in the folder `terraform` and can be deployed using the following commands:
```sh
terraform init
# Then
terraform plan --var-file=tfvars/dev.tfvars
# Then
terraform apply --var-file=tfvars/dev.tfvars
```

**Note:** the above commands will work if you are already logged in to Azure CLI and privileged enough to provision these resources. Additionally, the backend for the Terraform is configured to use Azure Storage - this you will have to create manually before running `init`, in order to successfully initalize it. 

### 2.2 Development Setup
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

### 2.3 Using Tags to Publish DABs
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

## 3. Sample Output Data
### 3.1 Standardized Layer
```
+-------------------+----------+----------+--------------+------------+
|          timestamp|turbine_id|wind_speed|wind_direction|power_output|
+-------------------+----------+----------+--------------+------------+
|2022-03-01 00:00:00|         1|      11.8|           169|         2.7|
|2022-03-01 00:00:00|         2|      11.6|            24|         2.2|
|2022-03-01 00:00:00|         3|      13.8|           335|         2.3|
|2022-03-01 00:00:00|         4|      12.8|           238|         1.9|
|2022-03-01 00:00:00|         5|      11.4|           103|         3.5|
|2022-03-01 01:00:00|         1|      11.6|           152|         4.4|
|2022-03-01 01:00:00|         2|      12.8|            35|         4.2|
|2022-03-01 01:00:00|         3|      10.4|           169|         1.9|
|2022-03-01 01:00:00|         4|      13.9|           170|         2.4|
|2022-03-01 01:00:00|         5|      12.1|           165|         4.0|
```

### 3.2 Enriched Layer
```
+----------+-------------------+----------+--------------+------------+----------+------------+-----------+-----------+----------+
|turbine_id|          timestamp|wind_speed|wind_direction|power_output|mean_power|stddev_power|upper_bound|lower_bound|is_anomaly|
+----------+-------------------+----------+--------------+------------+----------+------------+-----------+-----------+----------+
|         1|2022-03-01 00:00:00|      11.8|           169|         2.7|       3.0|         1.0|        5.0|        1.0|     false|
|         2|2022-03-01 00:00:00|      11.6|            24|         2.2|       3.0|         1.0|        5.0|        1.0|     false|
|         3|2022-03-01 00:00:00|      13.8|           335|         2.3|       3.0|         1.0|        5.0|        1.0|     false|
|         4|2022-03-01 00:00:00|      12.8|           238|         1.9|       3.0|         1.0|        5.0|        1.0|     false|
|         5|2022-03-01 00:00:00|      11.4|           103|         3.5|       3.0|         1.0|        5.0|        1.0|     false|
|         1|2022-03-01 01:00:00|      11.6|           152|         4.4|       3.0|         1.0|        5.0|        1.0|     false|
|         2|2022-03-01 01:00:00|      12.8|            35|         4.2|       3.0|         1.0|        5.0|        1.0|     false|
|         3|2022-03-01 01:00:00|      10.4|           169|         1.9|       3.0|         1.0|        5.0|        1.0|     false|
|         4|2022-03-01 01:00:00|      13.9|           170|         2.4|       3.0|         1.0|        5.0|        1.0|     false|
|         5|2022-03-01 01:00:00|      12.1|           165|         4.0|       3.0|         1.0|        5.0|        1.0|     false|
```

### 3.3 Curated Layer
```
+----------+----------+---------+---------+---------+
|turbine_id|      date|min_power|max_power|avg_power|
+----------+----------+---------+---------+---------+
|        13|2022-03-25|      1.5|      4.4|      3.0|
|        11|2022-03-26|      1.6|      4.5|      3.0|
|        11|2022-03-03|      1.6|      4.5|      3.0|
|        11|2022-03-09|      1.6|      4.4|      3.0|
|        14|2022-03-30|      1.5|      4.4|      3.0|
|        11|2022-03-07|      1.5|      4.5|      3.0|
|        14|2022-03-18|      1.6|      4.5|      3.0|
|        14|2022-03-20|      1.6|      4.4|      3.0|
|        12|2022-03-23|      1.5|      4.4|      3.0|
|        15|2022-03-24|      1.8|      4.4|      3.0|
|        13|2022-03-07|      1.7|      4.4|      3.0|
|        11|2022-03-24|      1.8|      4.3|      3.0|
|        15|2022-03-19|      1.5|      4.3|      3.0|
|        12|2022-03-25|      1.7|      4.5|      3.0|
```