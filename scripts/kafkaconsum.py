import ast
import time
from confluent_kafka import Consumer, KafkaException, KafkaError
from pymongo import MongoClient, errors

# --------------------- CONFIG ---------------------
KAFKA_BROKER = 'kafka:9092'            # Kafka service name inside Docker network
KAFKA_TOPIC = 'ecommerce_orders'
GROUP_ID = 'ecommerce-consumer-group'

MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "ecommerce"
COLLECTION_NAME = "orders_live"

# ------------------- MONGO SETUP -------------------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
orders_live = db[COLLECTION_NAME]

# Ensure unique index on order_id to prevent duplicates
orders_live.create_index("order_id", unique=True)

print("MongoDB connected and index ensured.")

# ------------------- KAFKA SETUP -------------------
def create_consumer(retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            consumer = Consumer({
                'bootstrap.servers': KAFKA_BROKER,
                'group.id': GROUP_ID,
                'auto.offset.reset': 'earliest',
                'fetch.min.bytes': 1048576  # Fetch at least 1 MB of data
            })
            print("Kafka consumer connected successfully.")
            return consumer
        except KafkaException as e:
            print(f"[Attempt {attempt}] Kafka not ready: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

consumer = create_consumer()
consumer.subscribe([KAFKA_TOPIC])
print(f"Listening to Kafka topic: {KAFKA_TOPIC}")

# ------------------- CONSUMER LOOP -------------------
counter = 0

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            # Ignore partition EOF
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break

        raw_message = msg.value().decode('utf-8')

        try:
            # Safely parse the Kafka message
            message = ast.literal_eval(raw_message)

            # Insert into MongoDB
            try:
                orders_live.insert_one(message)
            except errors.DuplicateKeyError:
                print(f"Duplicate order skipped: {message['order_id']}")
            except Exception as mongo_err:
                print(f"Mongo insert error: {mongo_err}")

        except Exception as parse_error:
            print(f"Error parsing message: {parse_error}")
            continue

        counter += 1
        # Log every 100 messages
        if counter % 100 == 0:
            print(f"[{counter} messages consumed] Latest message: {message}")

except KeyboardInterrupt:
    print("Consumer stopped manually.")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    consumer.close()
    print("Kafka consumer closed.")
