import json
import pendulum
import requests
from airflow.io.path import ObjectStoragePath
from airflow.decorators import dag, task

BUCKET_NAME = "praveen-airflow-bucket-1"
AWS_CONN_ID = "aws_default"
BASE_PATH = f"s3://{BUCKET_NAME}/airflow_stuff/"
base = ObjectStoragePath(BASE_PATH, conn_id=AWS_CONN_ID)
# Use the @task decorator to convert a regular Python function into an Airflow task
# When a task function returns a value, it is automatically pushed to XCom
# 2.0 Airflow
@dag(
    dag_id="taskflow",
    start_date=pendulum.datetime(2025, 2, 8, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["realistic", "etl", "weather"],
    description="A realistic ETL pipeline that extracts weather data, transforms it, and loads it to a JSON file."
)
def realistic_weather_etl():
    # Task 1: Extract weather data for a given city using OpenWeatherMap API.
    @task()
    def extract_weather_data(city: str) -> dict:
        # Retrieve API key from Airflow variables (ensure to set this in the UI or via the CLI)
        api_key = 'a813c1dd464d874fdab7c2f91ae04e05'
        # Build the API URL. The units=metric parameter gets the temperature in Celsius.
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data

    # Task 2: Transform the raw weather data by extracting key fields and converting the temperature.
    @task()
    def transform_weather_data(raw_data: dict) -> dict:
        main = raw_data.get("main", {})
        weather_info = raw_data.get("weather", [{}])[0]
        temperature_c = main.get("temp")
        if temperature_c is None:
            raise ValueError("Temperature value not found in the API response.")
        # Convert Celsius to Fahrenheit
        temperature_f = (temperature_c * 9 / 5) + 32

        transformed = {
            "city": raw_data.get("name"),
            "temperature_celsius": temperature_c,
            "temperature_fahrenheit": temperature_f,
            "weather_description": weather_info.get("description"),
            "timestamp": raw_data.get("dt")  # Unix timestamp from the API
        }
        return transformed

    # Task 3: Load the transformed data by writing it to a local JSON file.
    @task()
    def load_weather_data(data: dict) -> str:
        path = base / "taskflow/weather_data.txt"
        str_data = str(data)
        with path.open("wb") as f:
            f.write(f"Weather data :: {str_data} ".encode("utf-8"))

    # Define the city you want to query (this could also come from a Variable or configuration)
    city = "London"

    # Build the task flow
    raw_data = extract_weather_data(city)
    transformed_data = transform_weather_data(raw_data)
    load_weather_data(transformed_data)

# Instantiate the DAG
realistic_weather_etl()
