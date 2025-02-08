import json
import pendulum
import requests
from typing import ClassVar, Dict

from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator

# -------------------------------
# Example DAG Using XComs
# -------------------------------
default_args = {"retries": 1}

with DAG(
    dag_id="xcom_example_dag",
    start_date=pendulum.datetime(2025, 2, 8, tz="UTC"),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["example", "xcom"],
) as dag:

    # Task 1: Explicitly push an XCom value
    def push_data(**kwargs):
        ti = kwargs["ti"]
        sample_data = {"value": 123, "message": "Hello from push_data"}
        # Pushing data with a custom key
        ti.xcom_push(key="custom_key", value=sample_data)
        # Also returning a value automatically pushes it under 'return_value'
        return "Return value from push_data"

    push_task = PythonOperator(
        task_id="push_task",
        python_callable=push_data,
        do_xcom_push=True,
    )

    # Task 2: Pull the XCom values from the previous task
    def pull_data(**kwargs):
        ti = kwargs["ti"]
        # Pull using explicit key and task_id
        pushed_value = ti.xcom_pull(key="custom_key", task_ids="push_task")
        # Pulling the automatic return_value (if no key is provided, default is 'return_value')
        return_value = ti.xcom_pull(task_ids="push_task")
        print("Pulled custom key value:", pushed_value)
        print("Pulled return value:", return_value)
        # Return both values as a dictionary to demonstrate multiple outputs
        return {"pushed": pushed_value, "return": return_value}

    pull_task = PythonOperator(
        task_id="pull_task",
        python_callable=pull_data,
        do_xcom_push=True,
    )

    # Task 3: A TaskFlow-decorated task returning multiple outputs
    @task(multiple_outputs=True)
    def multi_output_task() -> Dict[str, int]:
        # Returning multiple values pushes each key/value pair as separate XCom entries
        return {"a": 1, "b": 2, "c": 3}

    # Task 4: Demonstrate templated XCom access (simulated)
    def final_pull(**kwargs):
        ti = kwargs["ti"]
        # Pulling the output from the multi_output_task
        multi_output = ti.xcom_pull(task_ids="multi_output_task")
        print("Multi Pull Value is:", multi_output)

    final_task = PythonOperator(
        task_id="final_task",
        python_callable=final_pull,
        do_xcom_push=True,
    )

    # Setting up dependencies:
    push_task >> pull_task >> multi_output_task() >> final_task
