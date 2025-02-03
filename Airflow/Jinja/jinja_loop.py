from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="jinja_loop",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
) as dag:

    loop_example = BashOperator(
        task_id="loop_example",
        bash_command="""
            {% set fruits = ["apple", "banana", "cherry"] %}
            {% for fruit in fruits %}
                echo "I like {{ fruit }}"
            {% endfor %}
        """,
    )

    loop_example
