import datetime
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models.baseoperator import chain, cross_downstream

# Default arguments
default_args = {
    "retries": 3,
    "retry_delay": datetime.timedelta(minutes=2),
    "timeout": 600,  # 10 minutes
}

# Define a DAG using the @dag decorator
@dag(
    dag_id="dag_example_2",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    # schedule_interval="30 15 * * *"
    catchup=False,
    default_args=default_args,
    description="A second DAG demonstrating advanced Airflow concepts",
    tags=["example", "tutorial"],
)
def example_dag():

    # Tasks
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Workflow started for {{ ds }}'",
    )

    @task
    def extract_data():
        print("Extracting data for the day...")
        # Simulate extracting data logic

    @task
    def transform_data():
        print("Transforming data...")
        # Simulate transformation logic

    @task
    def load_data():
        print("Loading data into the database...")
        # Simulate data loading logic

    archive_data_task = BashOperator(
        task_id="archive_data_task",
        bash_command="aws s3 cp s3://praveen-airflow-bucket-1/data_files/customers-100.csv  s3://praveen-airflow-bucket-1/archieve_data_files/",
    )

    cleanup_task = BashOperator(
        task_id="cleanup_task",
        bash_command="aws s3 rm s3://praveen-airflow-bucket-1/archieve_data_files/customers-100.csv",
    )

    # Dependencies
    start_task >> extract_data()

    # Use cross_downstream for parallel branches
    cross_downstream(
        [extract_data()],
        [transform_data(), archive_data_task]
    )

    # Use chain for sequential tasks
    chain(transform_data(), load_data(), cleanup_task)


# Instantiate the DAG
dag_instance = example_dag()
