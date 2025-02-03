import time
import datetime
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging

# SLA Miss Callback Function
def sla_miss_callback(dag, task_list, blocking_task_list, slas):
    logging.info("⚠️ SLA Miss Detected!")
    logging.info(f"📌 DAG: {dag.dag_id}")
    logging.info(f"🚨 Affected Tasks: {task_list}")
    logging.info(f"🔗 Blocking Tasks: {blocking_task_list}")
    logging.info(f"⏳ SLA Details: {slas}")

# Python function that simulates delay
def slow_python_task():
    time.sleep(50)  # Sleeps for 20 seconds

# Define DAG
with DAG(
    dag_id="sla_example",
    start_date=pendulum.datetime(2025, 2, 2, tz="UTC"),
    schedule_interval="@daily",  # Runs every 2 minutes
    catchup=False,
    sla_miss_callback=sla_miss_callback,  # SLA miss handler
    default_args={"email": ["mailpraveenreddy.c@gmail.com"],"email_on_sla_miss": True},
    description="DAG demonstrating multiple SLA settings",
) as dag:

    # Python Task with SLA
    python_task = PythonOperator(
        task_id="python_sla_task",
        python_callable=slow_python_task,
        sla=datetime.timedelta(seconds=10),  # SLA of 10 seconds
        # on_failure_callback=sla_miss_callback,  # Task-level callback
    )

    # Bash Task with SLA
    bash_task = BashOperator(
        task_id="bash_sla_task",
        bash_command="sleep 50",  # Simulating delay
        sla=datetime.timedelta(seconds=15),  # SLA of 15 seconds
    )

    python_task >> bash_task  # Set dependency

