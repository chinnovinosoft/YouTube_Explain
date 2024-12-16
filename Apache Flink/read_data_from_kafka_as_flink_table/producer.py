from confluent_kafka import Producer
import random
import json
# Configure Kafka producer
conf = {
    'bootstrap.servers': 'localhost:9092'  # Kafka server address
}

# Create producer instance
producer = Producer(conf)

# Callback to check message delivery
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Produce messages
topic = "test_topic"
greet_strings = ["Hi",'Hello','Good Day','Namaste']
for i in range(10):
    message = {
        "key":str(i),
        "data":random.choice(greet_strings)
    }
    # Serialize the message to JSON
    serialized_message = json.dumps(message)
    # Produce the message
    producer.produce(topic, value=serialized_message.encode('utf-8'), callback=delivery_report)

# Flush producer to ensure all messages are sent
producer.flush()
print("Messages published successfully.")