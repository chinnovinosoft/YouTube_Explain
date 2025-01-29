import datetime
import random
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# Branching Example
@dag(
    dag_id="branching_example_dag",
    start_date=datetime.datetime(2025, 1, 26),
    schedule_interval="@daily",
    catchup=False,
    description="Example DAG showcasing branching with @task.branch",
)
def branching_example():

    def process_task_1():
        print("Processing Task 1")

    def process_task_2():
        print("Processing Task 2")

    # Start task
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Starting branching workflow'",
    )

    # Branching function
    @task.branch(task_id="branch_task")
    def branch_func():
        decision = random.randint(1, 10)  # Random decision logic
        if decision >= 5:
            return "task_1"
        elif decision >= 3:
            return "task_2"
        else:
            return None

    task_1 = PythonOperator(
        task_id="task_1",
        python_callable=process_task_1,
    )

    task_2 = PythonOperator(
        task_id="task_2",
        python_callable=process_task_2,
    )

    # Define task dependencies
    start_task >> branch_func() >> [task_1, task_2]

# Instantiate the DAG
dag_instance = branching_example()
