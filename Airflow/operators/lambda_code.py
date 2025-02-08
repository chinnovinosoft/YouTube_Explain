import json
import boto3

def lambda_handler(event, context):
    # Log the received event
    print("Received event:", json.dumps(event))
    
    try:
        # Expecting an event with Records from an S3 upload
        records = event.get("Records", [])
        if records:
            s3_client = boto3.client('s3')
            for record in records:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                print(f"Processing file from bucket: {bucket}, key: {key}")
                
                # Read the object content from S3
                response = s3_client.get_object(Bucket=bucket, Key=key)
                file_content = response['Body'].read().decode('utf-8')
                print(f"Content of {key}:")
                print(file_content)
        else:
            print("No S3 Records found in event.")
    except Exception as e:
        print("Error processing event:", str(e))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda executed successfully!')
    }
