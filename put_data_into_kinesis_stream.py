import boto3
from faker import Faker
import json
import time
import os
import logging
from botocore.exceptions import BotoCoreError, NoCredentialsError, PartialCredentialsError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Constants
STREAM_NAME = "StockTradeStream"
MAX_RECORDS = 20
SLEEP_INTERVAL = 5
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

# Initialize Faker
fake = Faker()

def generate_random_person():
    """Generate random person data."""
    return {
        'name': fake.name(),
        'phone_number': fake.phone_number(),
        'city': fake.city(),
        'country': "India",
        'height': fake.random_int(min=150, max=190),
        'weight': fake.random_int(min=50, max=90)
    }

def create_kinesis_client():
    """Create a Kinesis client with credentials from environment variables."""
    try:
        kinesis_client = boto3.client(
            "kinesis",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )
        return kinesis_client
    except (BotoCoreError, NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Failed to create Kinesis client: {e}")
        raise

def describe_stream(kinesis_client):
    """Describe the Kinesis stream and log stream details."""
    try:
        response = kinesis_client.describe_stream(StreamName=STREAM_NAME)
        logging.info(f"Stream {STREAM_NAME} description: {response['StreamDescription']}")
    except BotoCoreError as e:
        logging.error(f"Error describing stream {STREAM_NAME}: {e}")
        raise

def send_records_to_kinesis(kinesis_client):
    """Send random person data records to Kinesis."""
    for i in range(MAX_RECORDS):
        data = generate_random_person()
        try:
            response = kinesis_client.put_record(
                StreamName=STREAM_NAME,
                Data=json.dumps(data),
                PartitionKey="1"  # Can use a more meaningful partition key in real use cases
            )
            shard_id = response['ShardId']
            sequence_number = response['SequenceNumber']
            logging.info(f"Record {data['name']} sent to Shard ID: {shard_id}, Sequence Number: {sequence_number}")
        except BotoCoreError as e:
            logging.error(f"Error sending record to Kinesis: {e}")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    # Main execution block
    try:
        kinesis_client = create_kinesis_client()
        describe_stream(kinesis_client)
        send_records_to_kinesis(kinesis_client)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

