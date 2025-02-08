import pendulum
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.python import PythonOperator

# Define a simple Python function to simulate processing the detected file
def process_file(task_type):
    print(f"The file was detected in S3 and processing has started ({task_type} mode).")

# Define the DAG
with DAG(
    dag_id="sensor",
    start_date=pendulum.datetime(2025, 2, 8, tz="UTC"),
    schedule="@daily",
    catchup=False,
) as dag:

    # Task 1: S3KeySensor in POKE mode (low-latency, holds worker slot)
    wait_for_file_poke = S3KeySensor(
        task_id="wait_for_file_in_s3_poke",
        bucket_name="praveen-airflow-bucket-1",      # Replace with your bucket name
        bucket_key="data_files/data_poke.csv", # Path/key for the file in S3
        poke_interval=10,                      # Checks every 10 seconds
        timeout=300,                           # Times out after 5 minutes
        mode="poke",                           # Holds a worker slot while checking
    )

    # Task 2: S3KeySensor in RESCHEDULE mode (efficient, releases worker slot)
    wait_for_file_reschedule = S3KeySensor(
        task_id="wait_for_file_in_s3_reschedule",
        bucket_name="praveen-airflow-bucket-1",           # Replace with your bucket name
        bucket_key="data_files/data_reschedule.csv", # Path/key for the file in S3
        poke_interval=40,                            # Checks every 60 seconds
        timeout=300,                                # Times out after 1 hour
        mode="reschedule",                           # Releases worker slot between checks
    )

    # Processing tasks after file detection
    process_file_poke = PythonOperator(
        task_id="process_file_poke",
        python_callable=process_file,
        op_kwargs={"task_type": "poke"},
    )

    process_file_reschedule = PythonOperator(
        task_id="process_file_reschedule",
        python_callable=process_file,
        op_kwargs={"task_type": "reschedule"},
    )

    # Define dependencies: Each sensor must complete before processing starts
    wait_for_file_poke >> process_file_poke
    wait_for_file_reschedule >> process_file_reschedule
