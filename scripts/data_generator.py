import json
import time
import uuid
import random
from datetime import datetime

import numpy as np
from faker import Faker
from confluent_kafka import Producer

KAFKA_BROKER = "kafka:9092"
TOPIC_NAME = "ecommerce_orders"

fake = Faker()

producer_config = {
    "bootstrap.servers": KAFKA_BROKER
}
producer = Producer(producer_config)

PRODUCTS = [
    {"product_id": "P1001", "category": "Electronics", "mean_price": 1200, "std": 300},
    {"product_id": "P1002", "category": "Fashion", "mean_price": 80, "std": 25},
    {"product_id": "P1003", "category": "Home", "mean_price": 300, "std": 70},
    {"product_id": "P1004", "category": "Beauty", "mean_price": 60, "std": 15}
]

PAYMENT_TYPES = ["credit_card", "debit_card", "paypal", "cod"]
PAYMENT_WEIGHTS = [0.45, 0.25, 0.2, 0.1]

CITIES = ["Karachi", "Lahore", "Islamabad", "Faisalabad"]
LOYALTY_TIERS = ["silver", "gold", "platinum"]

def generate_order():
    product = random.choice(PRODUCTS)

    quantity = max(1, np.random.poisson(2))
    unit_price = max(
        5,
        np.random.normal(product["mean_price"], product["std"])
    )

    discount = round(unit_price * random.choice([0, 0.05, 0.1, 0.15]), 2)
    tax = round(unit_price * 0.08, 2)
    shipping_cost = round(max(3, np.random.normal(10, 3)), 2)

    total_amount = round(
        (unit_price * quantity) - discount + tax + shipping_cost,
        2
    )

    order = {
        "order_id": str(uuid.uuid4()),
        "order_timestamp": datetime.utcnow().isoformat(),
        "customer_id": f"CUST-{random.randint(1000, 9999)}",
        "product_id": product["product_id"],
        "category": product["category"],
        "quantity": quantity,
        "unit_price": round(unit_price, 2),
        "discount": discount,
        "tax": tax,
        "shipping_cost": shipping_cost,
        "total_amount": total_amount,
        "payment_type": random.choices(PAYMENT_TYPES, PAYMENT_WEIGHTS)[0],
        "payment_status": random.choices(
            ["success", "failed"], [0.93, 0.07]
        )[0],
        "city": random.choice(CITIES),
        "country": "Pakistan",
        "loyalty_tier": random.choice(LOYALTY_TIERS),
        "order_status": random.choices(
            ["delivered", "cancelled"], [0.9, 0.1]
        )[0]
    }

    return order

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")

def stream_orders():
    print("Ecommerce Data Generator Started...", flush=True)

    counter = 0
    while True:
        order = generate_order()
        producer.produce(TOPIC_NAME, value=json.dumps(order), callback=delivery_report)
        counter += 1

        # Flush every 100 orders
        if counter % 100 == 0:
            producer.flush()
            print(f"Sent {counter} orders so far.", flush=True)

        # tiny sleep to simulate realistic traffic
        time.sleep(0.1)

if __name__ == "__main__":
    stream_orders()
