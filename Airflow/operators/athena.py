from airflow import DAG
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from datetime import datetime

# Configuration variables
s3_bucket = "praveen-airflow-bucket-1"
raw_data_path = f"s3://{s3_bucket}/raw_data/"           # S3 path for raw CSV files
transformed_data_path = f"s3://{s3_bucket}/transformed_data/"  # S3 path for transformed output
athena_database = "athena_db_airflow"
query_results = f"s3://{s3_bucket}/query-results/"        # S3 path where Athena query results are stored

with DAG(
    dag_id="athena_s3_1",
    start_date=datetime(2024, 2, 8),
    schedule_interval=None,
    catchup=False
) as dag:

    # Step 1: Create a table on top of the raw CSV files
    create_raw_table = AthenaOperator(
        task_id="create_raw_table",
        query=f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {athena_database}.raw_table (
                id INT,
                name STRING,
                age INT
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
            LOCATION '{raw_data_path}'
        """,
        database=athena_database,
        output_location=query_results,
    )

    # Step 2: Transform the data using a CTAS query
    transform_data = AthenaOperator(
        task_id="transform_data",
        query=f"""
            CREATE TABLE {athena_database}.temp_transformed
            WITH (
                format = 'PARQUET',
                external_location = '{transformed_data_path}'
            ) AS
            SELECT 
                id,
                UPPER(name) AS name_upper,
                age + 1 AS age_plus_one
            FROM {athena_database}.raw_table
        """,
        database=athena_database,
        output_location=query_results,
    )

    # Step 3: Create an external table over the transformed data
    create_transformed_table = AthenaOperator(
        task_id="create_transformed_table",
        query=f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {athena_database}.transformed_table (
                id INT,
                name_upper STRING,
                age_plus_one INT
            )
            STORED AS PARQUET
            LOCATION '{transformed_data_path}'
        """,
        database=athena_database,
        output_location=query_results,
    )

    # Define task dependencies
    create_raw_table >> transform_data >> create_transformed_table
