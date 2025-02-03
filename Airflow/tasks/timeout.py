from airflow.sensors.filesystem import FileSensor
import datetime
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

with DAG(
    dag_id="sensor_timeout_example",
    default_args={"start_date": datetime.datetime(2025, 2, 2)},
    schedule_interval="@daily",
    catchup=False,
) as dag:

    # file_sensor = FileSensor(
    #     task_id="wait_for_file",
    #     filepath="s3://praveen-airflow-bucket-1/data_files/my_file.txt",
    #     execution_timeout=datetime.timedelta(seconds=20),  # Each poke has 60s max
    #     timeout=100,  # Total time to wait for file: 3600s (1 hour). Unlike poke_timeout, this includes all retry attempts over multiple reschedules.
    #     mode="reschedule",
    #     retries=2,
    # )
    file_sensor = S3KeySensor(
        task_id="wait_for_file",
        bucket_name="praveen-airflow-bucket-1",
        bucket_key="data_files/my_file.txt",
        aws_conn_id="aws_default",  # Ensure this connection exists in Airflow
        execution_timeout=datetime.timedelta(seconds=20),
        timeout=datetime.timedelta(seconds=200),
        mode="reschedule",
        retries=2,
    )

    file_sensor
