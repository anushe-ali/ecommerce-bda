from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType

# ---------------------- Spark Session ----------------------
spark = SparkSession.builder \
    .appName("Ecommerce Data Streaming Transformation") \
    .getOrCreate()

# ---------------------- Kafka Config ----------------------
KAFKA_BROKER = "kafka:9092"  # Docker network Kafka broker
KAFKA_TOPIC = "ecommerce_orders"

# ---------------------- Define Schema ----------------------
schema = StructType() \
    .add("order_id", StringType()) \
    .add("order_timestamp", StringType()) \
    .add("customer_id", StringType()) \
    .add("product_id", StringType()) \
    .add("category", StringType()) \
    .add("quantity", IntegerType()) \
    .add("unit_price", DoubleType()) \
    .add("discount", DoubleType()) \
    .add("tax", DoubleType()) \
    .add("shipping_cost", DoubleType()) \
    .add("total_amount", DoubleType()) \
    .add("payment_type", StringType()) \
    .add("payment_status", StringType()) \
    .add("city", StringType()) \
    .add("country", StringType()) \
    .add("loyalty_tier", StringType()) \
    .add("order_status", StringType())

# ---------------------- Read from Kafka ----------------------
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Kafka value is in binary, decode to string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_str")

# Parse JSON strings
df_parsed = df_string.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# Remove nulls
df_clean = df_parsed.na.drop()

# ---------------------- Write to HDFS ----------------------
output_path = "/user/output/ecommerce_transformed_data"

hdfs_query = df_clean.writeStream \
    .format("csv") \
    .option("path", output_path) \
    .option("checkpointLocation", "/user/output/checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

# Write to console for debugging
console_query = df_clean.writeStream \
    .format("console") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

print("Streaming job started. Listening to Kafka topic:", KAFKA_TOPIC)

# Keep the stream running
hdfs_query.awaitTermination()
console_query.awaitTermination()
