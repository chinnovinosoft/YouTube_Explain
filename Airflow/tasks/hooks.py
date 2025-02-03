from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


def dag_hook(context):
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    print(f"DAG Hook: Task {task_id} is starting at {execution_date}")

# Define a Pre-Task Hook
def pre_task(context):
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    print(f"⚡ Pre-Task Hook: Task {task_id} is starting at {execution_date}")

# Define a Post-Task Hook
def post_task(context):
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    print(f"✅ Post-Task Hook: Task {task_id} finished execution at {execution_date}")

# Define the DAG
with DAG(
    dag_id="example_pre_post_task_hooks",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
    # on_execute_callback=pre_task,  # Set Pre-Task Hook applied to each and every task 
    on_success_callback=dag_hook,  # Set Post-Task Hook applied to each and every task 
    on_failure_callback=dag_hook,  # Call post-task on failure too
) as dag:

    # Define a sample task
    my_task_1 = BashOperator(
        task_id="my_task_1",
        bash_command="echo 'Hello, Praveen Reddy C !!!'",
    )

    my_task_2 = BashOperator(
        task_id="my_task_2",
        bash_command="echo 'Running prehook, posthook for specific task'",
        on_execute_callback=pre_task,   # Pre-task hook
        on_success_callback=post_task,  # Post-task hook for success
        on_failure_callback=post_task,  # Post-task hook for failure
    )

    my_task_1 >> my_task_2