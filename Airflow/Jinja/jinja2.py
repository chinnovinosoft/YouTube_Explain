from airflow import DAG
from airflow.operators.python import PythonOperator
from typing import Sequence
from datetime import datetime

class MyDataReader:
    template_fields: Sequence[str] = ("path",)  # Ensuring 'path' supports Jinja templating

    def __init__(self, my_path):
        self.path = my_path

def process_data(**kwargs):
    """Function that reads and processes data using templated path."""
    execution_date = kwargs["ds"]  # Extract execution date
    path = f"s3://praveen-airflow-bucket-1/data_files/{execution_date}/file.csv"
    reader = MyDataReader(path)
    print(f"Reading data from: {reader.path}")

def print_execution_info(**kwargs):
    """Logs execution details."""
    print(f"Execution Date (ds): {kwargs['ds']}")
    print(f"Previous Execution Date (prev_ds): {kwargs['prev_ds']}")
    print(f"Next Execution Date (next_ds): {kwargs['next_ds']}")
    print(f"Year: {kwargs['execution_date'].year}, Month: {kwargs['execution_date'].month}, Day: {kwargs['execution_date'].day}")


with DAG(
    dag_id="jinja2",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="read_data",
        python_callable=process_data,
        provide_context=True,  # Ensures kwargs contains execution context
    )

    task2 = PythonOperator(
        task_id="print_execution_info",
        python_callable=print_execution_info,
        provide_context=True,
    )

    task1 >> task2
