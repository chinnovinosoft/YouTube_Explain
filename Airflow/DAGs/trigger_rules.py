import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models.baseoperator import chain, cross_downstream
from airflow.utils.trigger_rule import TriggerRule

def process_data():
    print("Processing data for the day...")
    # Simulate data processing logic

def generate_report():
    print("Generating the daily report...")
    # Simulate report generation logic

def send_notification():
    print("Sending notification about the report...")
    # Simulate notification logic

# DAG definition
with DAG(
    dag_id="trigger_rules_example_dag",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": datetime.timedelta(minutes=1), "timeout": 300},
    description="A DAG demonstrating trigger rules and dependencies",
) as dag:

    # Tasks
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Starting the daily workflow'",
    )

    data_processing_task = PythonOperator(
        task_id="data_processing_task",
        python_callable=process_data,
    )

    report_generation_task = PythonOperator(
        task_id="report_generation_task",
        python_callable=generate_report,
        trigger_rule=TriggerRule.ONE_SUCCESS,  # Runs if at least one upstream task succeeds
    )

    archive_data_task = BashOperator(
        task_id="archive_data_task",
        bash_command="aws s3 cp s3://praveen-airflow-bucket-1/data_files/customers-100.csv  s3://praveen-airflow-bucket-1/archieve_data_files/",
        trigger_rule=TriggerRule.ALL_FAILED,  # Runs if all upstream tasks fail
    )

    send_notification_task = PythonOperator(
        task_id="send_notification_task",
        python_callable=send_notification,
        trigger_rule=TriggerRule.ALL_DONE,  # Runs regardless of the outcome of upstream tasks
    )

    cleanup_task = BashOperator(
        task_id="cleanup_task",
        bash_command="aws s3 rm s3://praveen-airflow-bucket-1/archieve_data_files/customers-100.csv",
    )

    # Dependencies

    # Basic chaining
    start_task >> data_processing_task

    # Cross downstream --> If you want to make a list of tasks depend on another list of tasks
    cross_downstream([data_processing_task], [report_generation_task, archive_data_task])

    # Chain for complex dependencies
    chain(report_generation_task, send_notification_task, cleanup_task)
