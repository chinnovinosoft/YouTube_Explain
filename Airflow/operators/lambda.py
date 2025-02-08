import json
from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from datetime import datetime

with DAG(
    dag_id="lambda_trigger_dag",
    start_date=datetime(2024, 2, 8),
    schedule_interval=None,
    catchup=False,
) as dag:

    # This operator invokes the Lambda function with a payload that mimics an S3 file upload event.
    # s3://praveen-airflow-lambda/input_data/
    invoke_lambda = LambdaInvokeFunctionOperator(
        task_id="invoke_lambda_function",
        function_name='airflow_lambda',
        payload=json.dumps({
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "praveen-airflow-lambda"},  
                        "object": {"key": "input_data/test_file.txt"}  
                    }
                }
            ]
        }),
    )

    # The DAG consists of a single task in this example.
    invoke_lambda
