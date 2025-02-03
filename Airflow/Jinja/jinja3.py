from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define a function that processes data based on params
def process_sales_data(my_params, **kwargs):
    print("🔹 Received Parameters:", my_params)

    # Extract values
    region = my_params.get("region", "Global")
    category = my_params.get("category", "All")
    discount = my_params.get("discount", 0)

    # Simulate fetching data (this would be from a database in real life)
    sales_data = [
        {"product": "Laptop", "category": "Electronics", "price": 1000, "region": "USA"},
        {"product": "Phone", "category": "Electronics", "price": 500, "region": "Europe"},
        {"product": "Shoes", "category": "Fashion", "price": 200, "region": "USA"},
    ]

    # Filter data based on params
    filtered_data = [
        item for item in sales_data
        if (item["region"] == region or region == "Global")
        and (item["category"] == category or category == "All")
    ]

    # Apply discount if provided
    for item in filtered_data:
        item["discounted_price"] = item["price"] * (1 - discount / 100)

    print("📊 Processed Sales Data:", filtered_data)
    return filtered_data  

# Define Airflow DAG
dag = DAG(
    dag_id="jinja3",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
)

# Define PythonOperator with `op_kwargs`
process_sales_task = PythonOperator(
    task_id="process_sales",
    python_callable=process_sales_data,
    op_kwargs={
        "my_params": {  # Passing parameters dynamically
            "region": "USA",
            "category": "Electronics",
            "discount": 10,
        }
    },
    dag=dag,
)

# Set task dependencies (if needed)
process_sales_task
