from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Custom Jinja filter
def reverse_string(value):
    return value[::-1]

# Define the DAG
with DAG(
    dag_id="jinja_filter",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
    jinja_environment_kwargs={"filters": {"reverse": reverse_string}},
) as dag:

    print_reverse = BashOperator(
        task_id="print_reverse",
        bash_command="echo '{{ 'airflow' | reverse }}'",  
    )

    print_reverse
