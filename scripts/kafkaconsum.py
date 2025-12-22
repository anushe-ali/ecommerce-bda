import ast
from confluent_kafka import Consumer, KafkaException

print("Consumer started")

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'  # Update with your Kafka broker address
KAFKA_TOPIC = 'bda_proj'  # Replace with your Kafka topic
GROUP_ID = 'ecommerce-consumer-group'  # Consumer group ID

# Initialize Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',
    'fetch.min.bytes': 1048576  # Fetch at least 1 MB of data
})

# Subscribe to the Kafka topic
consumer.subscribe([KAFKA_TOPIC])

try:
    print(f"Listening to topic: {KAFKA_TOPIC}")
    while True:
        # Poll for messages with a timeout
        msg = consumer.poll(timeout=1.0)

        if msg is None:  # No message
            continue
        if msg.error():  # Error occurred
            if msg.error().code() == KafkaException._PARTITION_EOF:
                continue  # End of partition
            else:
                print(f"Error: {msg.error()}")
                break

        # Message received
        raw_message = msg.value().decode('utf-8')
        print(f"Received message: {raw_message}")

        # Parse the message safely
        try:
            message = ast.literal_eval(raw_message)  # Convert to Python dictionary
            print(f"Parsed message: {message}")
            # Process the message (e.g., write to HDFS or HBase)
        except Exception as parse_error:
            print(f"Error parsing message: {parse_error}")

except KeyboardInterrupt:
    print("Consumer stopped manually.")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Close the consumer
    consumer.close()
    print("Consumer closed.")
