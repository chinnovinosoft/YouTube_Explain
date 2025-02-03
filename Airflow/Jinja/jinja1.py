from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="jinja1",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
) as dag:

    print_date_1 = BashOperator(
        task_id="print_date_1",
        bash_command="echo 'Execution date: {{ ds }}'",  # Jinja template in command
    )

    print_date_2 = BashOperator(
        task_id="print_date_2",
        bash_command="echo 'Execution date is {{ ds }} and previous date is {{ prev_ds }}'",
    )

    print_date_3 = BashOperator(
        task_id="print_date_3",
        bash_command="echo 'Some Jinja macros: {{ macros.datetime.now() }}, {{ next_execution_date }}, {{ macros.datetime.utcnow() }}'",
    )

    print_date_4 = BashOperator(
        task_id="print_date_4",
        bash_command="echo 'Five days ago was {{ macros.ds_add(ds, -5) }}'",
    )

    conditional_scenario = BashOperator(
        task_id="conditional_scenario",
        bash_command="""
        {% if macros.datetime.strptime(ds, '%Y-%m-%d').day == 1 %}
            echo "It's the first day of the month!"
        {% else %}
            echo "It's not the first day."
        {% endif %}
        """,
    )

    print_date_1 >> print_date_2 >> print_date_3 >> print_date_4 >> conditional_scenario 
