from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import (
    S3DeleteObjectsOperator,
    S3CopyObjectOperator,
    S3ListOperator
)
from datetime import datetime

# Configuration Variables
bucket = "praveen-airflow-athena"
source_key = "source_data/input/data.csv"
dest_key = "target_data/output/data.csv"


with DAG(
    dag_id="s3_copy_delete_list_dag",
    start_date=datetime(2024, 2, 8),
    schedule_interval=None,
    catchup=False,
) as dag:

    copy_object = S3CopyObjectOperator(
        task_id="copy_object",
        source_bucket_name=bucket,
        dest_bucket_name=bucket,
        source_bucket_key=source_key,
        dest_bucket_key=dest_key,
    )

    delete_objects = S3DeleteObjectsOperator(
        task_id="delete_objects",
        bucket=bucket,
        keys=[dest_key],  # keys expects a list of keys to delete.
    )

    copy_object >> delete_objects 