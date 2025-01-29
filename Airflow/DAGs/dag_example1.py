import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models.baseoperator import chain, cross_downstream


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
    dag_id="dag_example_1",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    # schedule_interval="30 15 * * 1-5"
    catchup=False,
    default_args={"retries": 2, "retry_delay": datetime.timedelta(minutes=1), "timeout": 300},
#     default_args = {
#     "owner": "airflow",                           # Owner of the DAG or tasks
#     "depends_on_past": False,                     # Tasks don't depend on the previous run's state
#     "email_on_failure": True,                     # Send email if a task fails
#     "email_on_retry": False,                      # Send email on retry
#     "email": ["example@example.com"],             # List of email recipients
#     "retries": 3,                                 # Number of retries for failed tasks
#     "retry_delay": datetime.timedelta(minutes=5), # Delay between retries
#     "retry_exponential_backoff": True,            # Exponential backoff for retries
#     "max_retry_delay": datetime.timedelta(minutes=60), # Maximum retry delay (used with exponential backoff)
#     "execution_timeout": datetime.timedelta(hours=2), # Timeout for task execution
#     "on_failure_callback": None,                  # Custom function to execute on task failure
#     "on_success_callback": None,                  # Custom function to execute on task success
#     "on_retry_callback": None,                    # Custom function to execute on task retry
#     "start_date": datetime.datetime(2025, 1, 20), # Start date for scheduling the DAG
#     "end_date": datetime.datetime(2025, 1, 30),   # End date for scheduling the DAG
#     "task_concurrency": 2,                        # Max number of concurrent task instances
#     "wait_for_downstream": False,                 # If downstream tasks should wait before running
#     "priority_weight": 1,                         # Task priority for the scheduler
#     "queue": "default",                           # Queue to run the task in (for CeleryExecutor)
#     "pool": "default_pool",                       # Pool to run the task in
#     "sla": datetime.timedelta(hours=1),           # SLA (Service Level Agreement) time for the task
#     "trigger_rule": "all_success",                # Trigger rule (when the task runs based on upstream states)
#     "do_xcom_push": True,                         # Whether the task pushes results to XCom
# }
    description="A first DAG explaining Airflow Concepts",
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
    )

    archive_data_task = BashOperator(
        task_id="archive_data_task",
        bash_command="aws s3 cp s3://praveen-airflow-bucket-1/data_files/customers-100.csv  s3://praveen-airflow-bucket-1/archieve_data_files/",
    )

    send_notification_task = PythonOperator(
        task_id="send_notification_task",
        python_callable=send_notification,
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
