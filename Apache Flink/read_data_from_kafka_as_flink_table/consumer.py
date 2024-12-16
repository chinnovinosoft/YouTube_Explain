from confluent_kafka import Consumer, KafkaException, KafkaError

# Configure Kafka consumer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka server address
    'group.id': 'test_group',               # Consumer group ID
    'auto.offset.reset': 'earliest'         # Start consuming from earliest message
}

# Create consumer instance
consumer = Consumer(conf)

# Subscribe to topic
topic = "test_topic"
consumer.subscribe([topic])

print(f"Subscribed to {topic}")

# Poll messages
try:
    while True:
        msg = consumer.poll(1.0)  # Poll messages with a 1-second timeout
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            print(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    consumer.close()

