import datetime
import pendulum
from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.trigger_rule import TriggerRule

# Latest Only Example
with DAG(
    dag_id="latest_only_example_dag",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2025, 1, 24, tz="UTC"),
    catchup=True,
    description="Example DAG demonstrating LatestOnlyOperator",
    tags=["example"],
) as dag:

    # LatestOnly Operator
    latest_only = LatestOnlyOperator(task_id="latest_only")

    # Regular tasks
    task1 = EmptyOperator(task_id="task1")
    task2 = EmptyOperator(task_id="task2")
    task3 = EmptyOperator(task_id="task3") #to ensure task3 run always, trigger rule should be added trigger_rule=TriggerRule.ALL_DONE
    task4 = EmptyOperator(task_id="task4", trigger_rule=TriggerRule.ALL_DONE)

    # Dependencies
    latest_only >> task1 >> [task3, task4]
    task2 >> [task3, task4]
