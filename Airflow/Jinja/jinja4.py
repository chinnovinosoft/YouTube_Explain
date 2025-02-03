from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

#context is a dictionary containing runtime information passed automatically to tasks
def build_complex_command(**context):
    print(f"Execution Date (ds): {context['ds']}")
    print(f"Execution Date (ds_nodash): {context['ds_nodash']}")
    print(f"Data Interval Start: {context['data_interval_start']}")
    print(f"Data Interval End: {context['data_interval_end']}")
    print(f"Execution Timestamp: {context['ts']}")
    print(f"Logical Date: {context['logical_date']}")
    print(f"Run ID: {context['run_id']}")
    print(f"DAG Name: {context['dag'].dag_id}")
    print(f"Task Name: {context['task'].task_id}")
    print(f"Try Number: {context['ti'].try_number}")


# Define the DAG
with DAG(
    dag_id="jinja4",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
) as dag:

    # BashOperator with callable for dynamic command generation
    task1 = PythonOperator(
        task_id="task1",
        python_callable=build_complex_command,
        provide_context=True,
    )

    task2 = BashOperator(
        task_id="task",
        bash_command="""
            echo 'Execution Date (ds): {{ ds }}' &&
            echo 'Execution Date (ds_nodash): {{ ds_nodash }}' &&
            echo 'Data Interval Start: {{ data_interval_start }}' &&
            echo 'Data Interval End: {{ data_interval_end }}' &&
            echo 'Execution Timestamp: {{ ts }}' &&
            echo 'Logical Date: {{ logical_date }}' &&
            echo 'Run ID: {{ run_id }}' &&
            echo 'DAG Name: {{ dag.dag_id }}' &&
            echo 'Task Name: {{ task.task_id }}' &&
            echo 'Try Number: {{ ti.try_number }}'
            """,
        )

    task1 >> task2
