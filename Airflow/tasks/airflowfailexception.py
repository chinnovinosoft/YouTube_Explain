from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowFailException
import datetime

def validate_api_key():
    api_key_valid = False  # Simulating invalid API key
    if not api_key_valid:
        raise AirflowFailException("API key is invalid, failing task!")

with DAG("fail_example", start_date=datetime.datetime(2025, 2, 2), schedule="@daily") as dag:
    fail_task = PythonOperator(task_id="fail_task", python_callable=validate_api_key)

    fail_task
