import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.edgemodifier import Label

# Define the DAG
with DAG(
    dag_id="example_edge_labels",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    catchup=False,
    description="A DAG demonstrating edge labels for dependencies",
) as dag:

    # Define tasks
    start_task = EmptyOperator(task_id="start")
    data_ingestion = EmptyOperator(task_id="data_ingestion")
    data_validation = EmptyOperator(task_id="data_validation")
    validation_success = EmptyOperator(task_id="validation_success")
    validation_failure = EmptyOperator(task_id="validation_failure")
    notify_team = EmptyOperator(task_id="notify_team")
    end_task = EmptyOperator(task_id="end")

    # Define dependencies with labels
    start_task >> Label("Begin Process") >> data_ingestion
    data_ingestion >> Label("Perform Validation") >> data_validation
    data_validation >> Label("Validation Passed") >> validation_success >> Label("Proceed to Completion") >> end_task
    data_validation >> Label("Validation Failed") >> validation_failure >> Label("Alert Team") >> notify_team >> end_task
