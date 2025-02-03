from airflow import DAG
from airflow.operators.bash import BashOperator
import datetime

default_args = {
    "start_date": datetime.datetime(2025, 2, 2),
    "retries": 2,
}

with DAG(
    dag_id="execution_timeout_example",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    slow_task = BashOperator(
        task_id="slow_task",
        bash_command="sleep 120",  # Simulating a long-running task
        execution_timeout=datetime.timedelta(seconds=60),  # Timeout after 60s
    )

    slow_task
