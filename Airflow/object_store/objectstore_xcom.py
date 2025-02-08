import pendulum
from airflow import DAG
from airflow.decorators import task


with DAG(
    dag_id="s3_xcom",
    start_date=pendulum.datetime(2024, 2, 8, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["xcom", "s3"],
) as dag:

    @task
    def push_large_data() -> dict:
        """
        Create and return a large payload.
        The payload is intentionally large (2 MB) so that it exceeds the configured
        threshold (1 MB) and gets stored in S3 via the XCom object storage backend.
        """
        large_text = "id,name,city" * (2 * 1024 * 1024) 
        payload = {"data": large_text}
        return payload

    @task
    def pull_large_data(payload: dict) -> str:
        """
        Pull the large payload from XCom and print its size.
        """
        data_length = len(payload.get("data", ""))
        print("Length of data received:", data_length)
        return "Data pulled successfully"

    # Build the task flow: push the data then pull it
    large_payload = push_large_data()
    confirmation = pull_large_data(large_payload)
