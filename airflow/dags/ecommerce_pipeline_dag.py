from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import os
import pymongo
from hdfs import InsecureClient

# Default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

# DAG definition
dag = DAG(
    "ecommerce_bda_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/1 * * * *",  # every minute
    catchup=False
)

# 1️⃣ Generate streaming data
def generate_data_func():
    os.system("python /app/data_generator.py")

generate_data = PythonOperator(
    task_id="generate_data",
    python_callable=generate_data_func,
    dag=dag
)

# 2️⃣ Consume Kafka data and write to Mongo
def consume_kafka_func():
    os.system("python /app/kafkaconsum.py")

consume_kafka = PythonOperator(
    task_id="consume_kafka",
    python_callable=consume_kafka_func,
    dag=dag
)

# 3️⃣ Spark batch analytics
spark_kpi = SparkSubmitOperator(
    task_id="spark_kpi_batch",
    application="/app/spark_kpi_batch.py",
    conn_id="spark_default",
    conf={
        "spark.mongodb.input.uri": "mongodb://mongo:27017/ecommerce",
        "spark.mongodb.output.uri": "mongodb://mongo:27017/ecommerce"
    },
    verbose=True,
    dag=dag
)

# 4️⃣ Archive old data to HDFS if size > 300MB
def archive_data_func():
    # Connect to Mongo and get collection size
    client = pymongo.MongoClient("mongodb://mongo:27017/")
    db = client["ecommerce"]
    collection = db["orders"]
    stats = db.command("collstats", "orders")
    size_mb = stats["size"] / (1024 * 1024)

    if size_mb > 300:
        print(f"Collection size {size_mb:.2f} MB > 300 MB. Archiving to HDFS...")
        os.system("python /app/archive_orders.py")
    else:
        print(f"Collection size {size_mb:.2f} MB < 300 MB. Skipping archive.")

archive_data = PythonOperator(
    task_id="archive_to_hdfs",
    python_callable=archive_data_func,
    dag=dag
)

# Task dependencies
generate_data >> consume_kafka >> spark_kpi >> archive_data
