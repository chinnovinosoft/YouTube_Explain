import logging
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

# Function to log all available context variables, including params and macros
def log_context_variables(**kwargs):
    logging.info("🔹 DAG Info 🔹")
    logging.info(f"DAG ID: {kwargs['dag'].dag_id}")
    logging.info(f"Run ID: {kwargs['run_id']}")
    logging.info(f"DAG Run: {kwargs['dag_run']}")
    
    logging.info("\n🔹 Task Info 🔹")
    logging.info(f"Task ID: {kwargs['task'].task_id}")
    logging.info(f"Task Instance: {kwargs['task_instance']}")

    logging.info("\n🔹 Execution Dates 🔹")
    logging.info(f"Execution Date (pendulum): {kwargs['execution_date']}")
    logging.info(f"Execution Date (string): {kwargs['ds']}")
    logging.info(f"Execution Date (no dash): {kwargs['ds_nodash']}")
    logging.info(f"Previous Execution Date: {kwargs['prev_ds']}")
    logging.info(f"Next Execution Date: {kwargs['next_ds']}")
    logging.info(f"Previous Execution Date (no dash): {kwargs['prev_ds_nodash']}")
    logging.info(f"Next Execution Date (no dash): {kwargs['next_ds_nodash']}")
    
    logging.info("\n🔹 Timestamp Info 🔹")
    logging.info(f"Timestamp (ISO 8601): {kwargs['ts']}")
    logging.info(f"Timestamp (no dash): {kwargs['ts_nodash']}")
    
    logging.info("\n🔹 Logical Dates 🔹")
    logging.info(f"Logical Date: {kwargs['logical_date']}")
    logging.info(f"Previous Execution Date (pendulum): {kwargs['prev_execution_date']}")
    logging.info(f"Next Execution Date (pendulum): {kwargs['next_execution_date']}")

    logging.info("\n🔹 Parameters (`params`) 🔹")
    logging.info(f"Params Dictionary: {kwargs.get('params', {})}")
    if "name" in kwargs["params"]:
        logging.info(f"Custom Param: {kwargs['params']['name']}")

    logging.info("\n🔹 Macros (`macros`) 🔹")
    logging.info(f"Available Macros: {kwargs['macros']}")
    logging.info(f"Today's Date: {kwargs['macros'].ds_format(kwargs['ds'], '%Y-%m-%d', '%d-%m-%Y')}")
    logging.info(f"Yesterday: {kwargs['macros'].ds_add(kwargs['ds'], -1)}")
    logging.info(f"Next Week: {kwargs['macros'].ds_add(kwargs['ds'], 7)}")

# Define the DAG
with DAG(
    dag_id="kwargs",
    start_date=pendulum.datetime(2025, 2, 2, tz="UTC"),
    schedule_interval="@daily",
    catchup=False,
    params={"name": "praveen"},  # Use the standard `params` key
) as dag:

    log_task = PythonOperator(
        task_id="log_context",
        python_callable=log_context_variables,
        # provide_context=True is optional in Airflow 2.x when using **kwargs
        provide_context=True,
    )

    log_task
