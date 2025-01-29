import datetime
from airflow import DAG
from airflow.decorators import task_group
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Define Python functions for PythonOperator
def process_data():
    print("Processing data...")

def transform_data():
    print("Transforming data...")

# Define the DAG
with DAG(
    dag_id="taskgroup_example_dag",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    catchup=False,
    default_args={"retries": 1},
) as dag:

    # Define a TaskGroup
    @task_group(group_id="data_pipeline", tooltip="Data processing and transformation tasks")
    def data_pipeline_group():
        # Tasks inside the TaskGroup
        process_task = PythonOperator(
            task_id="process_data",
            python_callable=process_data,
        )
        transform_task = PythonOperator(
            task_id="transform_data",
            python_callable=transform_data,
        )
        archive_task = BashOperator(
            task_id="archive_data",
            bash_command="tar -czf /tmp/data_archive.tar.gz /tmp/data/",
        )

        # Define dependencies within the TaskGroup
        process_task >> transform_task >> archive_task

    # Define tasks outside the TaskGroup
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Starting the workflow...'",
    )

    end_task = BashOperator(
        task_id="end_task",
        bash_command="echo 'Workflow complete!'",
    )

    # Create an instance of the TaskGroup
    data_group = data_pipeline_group()

    # Set dependencies between the TaskGroup and other tasks
    start_task >> data_group >> end_task
