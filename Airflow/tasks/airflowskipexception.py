from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
import datetime

def check_data():
    data_available = False  # Simulating no data condition
    if not data_available:
        raise AirflowSkipException("No data available, skipping task!")

with DAG("skip_example", start_date=datetime.datetime(2025, 2, 2), schedule="@daily") as dag:
    skip_task = PythonOperator(task_id="skip_task", python_callable=check_data)

    skip_task
