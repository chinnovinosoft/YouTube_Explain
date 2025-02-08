from airflow import DAG
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from datetime import datetime

# Configuration Variables
bucket_name = "praveen-airflow-glue"  
role_name = "AmazonMWAA-praveen-airflow-6-LlqsbD"         
glue_database = "glue_db_airflow"    
glue_table = "glue_table_airflow"           
glue_crawler_name = "glue_crawler_airflow" 
glue_job_name = "glue_job_airflow"     

# Glue crawler configuration
glue_crawler_config = {
    "Name": glue_crawler_name,
    "Role": role_name,
    "DatabaseName": glue_database,
    "Targets": {
        "S3Targets": [
            {"Path": f"s3://{bucket_name}/crawler_data/"}  
        ]
    },
    "SchemaChangePolicy": {
        "UpdateBehavior": "UPDATE_IN_DATABASE",
        "DeleteBehavior": "DEPRECATE_IN_DATABASE"
    }
}

with DAG(
    dag_id="glue_crawler_and_job_dag",
    start_date=datetime(2024, 2, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    # 1. Trigger the Glue crawler to update the Glue table based on S3 data.
    crawl_s3 = GlueCrawlerOperator(
        task_id="crawl_s3",
        config=glue_crawler_config,
    )

    # 2. Submit the Glue job that executes the ETL script.
    submit_glue_job = GlueJobOperator(
        task_id="submit_glue_job",
        job_name=glue_job_name,
        script_location=f"s3://{bucket_name}/scripts/etl_script.py",  # Location of the ETL script in S3
        s3_bucket=bucket_name,
        iam_role_name=role_name,
        create_job_kwargs={
            "GlueVersion": "3.0",
            "NumberOfWorkers": 1,
            "WorkerType": "G.1X"
        },
    )

    # Define the task dependencies (crawler runs first, then job submission)
    crawl_s3 >> submit_glue_job
