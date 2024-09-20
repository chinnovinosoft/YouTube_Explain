import boto3
import os
import json
import time
import logging
from botocore.exceptions import BotoCoreError, NoCredentialsError, PartialCredentialsError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Constants
STREAM_NAME = "StockTradeStream"
SLEEP_INTERVAL = 2
LIMIT = 10
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = "+"

def create_kinesis_client():
    """Create a Kinesis client using environment variables for credentials."""
    try:
        return boto3.client(
            "kinesis",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )
    except (BotoCoreError, NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Error creating Kinesis client: {e}")
        raise

def describe_stream(kinesis_client):
    """Describe the Kinesis stream and retrieve shard IDs."""
    try:
        response = kinesis_client.describe_stream(StreamName=STREAM_NAME)
        shards = response['StreamDescription']['Shards']
        logging.info(f"Stream {STREAM_NAME} has {len(shards)} shards.")
        return shards
    except BotoCoreError as e:
        logging.error(f"Error describing stream {STREAM_NAME}: {e}")
        raise

def get_shard_iterator(kinesis_client, shard_id):
    """Get the shard iterator for a given shard ID."""
    try:
        shard_iterator_response = kinesis_client.get_shard_iterator(
            StreamName=STREAM_NAME,
            ShardId=shard_id,
            ShardIteratorType="TRIM_HORIZON"  # Options: AT_SEQUENCE_NUMBER, AFTER_SEQUENCE_NUMBER, TRIM_HORIZON, LATEST
        )
        return shard_iterator_response['ShardIterator']
    except BotoCoreError as e:
        logging.error(f"Error getting shard iterator for shard {shard_id}: {e}")
        raise

def get_records_from_shard(kinesis_client, shard_id, shard_iterator):
    """Get records from a shard using the shard iterator."""
    while shard_iterator:
        try:
            record_response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=LIMIT)
            
            # Check if records exist
            if 'Records' in record_response and len(record_response['Records']) > 0:
                logging.info(f"Shard ID: {shard_id} - Retrieved {len(record_response['Records'])} records.")
                for record in record_response['Records']:
                    logging.info(f"Record Data: {record['Data']}")
            else:
                logging.info(f"Shard ID: {shard_id} - No new records.")
            
            # Get the next shard iterator (to continue reading if there are more records)
            shard_iterator = record_response.get('NextShardIterator', None)
            
            # Wait before fetching more records
            time.sleep(SLEEP_INTERVAL)
        except BotoCoreError as e:
            logging.error(f"Error retrieving records from shard {shard_id}: {e}")
            break

if __name__ == "__main__":
    # Main execution block
    try:
        kinesis_client = create_kinesis_client()
        shards = describe_stream(kinesis_client)
        
        for shard in shards:
            shard_id = "shardId-000000000003" #shard['ShardId'] 
            logging.info(f"Processing Shard ID: {shard_id}")
            shard_iterator = get_shard_iterator(kinesis_client, shard_id)
            get_records_from_shard(kinesis_client, shard_id, shard_iterator)
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


