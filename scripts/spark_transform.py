from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_date, hour, minute, sum, avg, count, when
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType

# ---------------------- CONFIG ----------------------
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "ecommerce_orders"
MONGO_URI = "mongodb://mongo:27017/ecommerce"

# Fact and dimension collections
FACT_COLLECTION = "fact_orders"
DIM_COLLECTIONS = {
    "customers": "dim_customers",
    "products": "dim_products",
    "time": "dim_time",
    "location": "dim_location",
    "payments": "dim_payments",
    "kpis": "kpis"
}

# ---------------------- SPARK SESSION ----------------------
spark = SparkSession.builder \
    .appName("Ecommerce Streaming ETL") \
    .config("spark.mongodb.output.uri", MONGO_URI) \
    .getOrCreate()

# ---------------------- DEFINE SCHEMA ----------------------
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

# ---------------------- READ FROM KAFKA ----------------------
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Decode binary Kafka value to string
df_string = df_raw.selectExpr("CAST(value AS STRING) as json_str")

# Parse JSON to structured DataFrame
df_parsed = df_string.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# Clean null values
df_clean = df_parsed.na.drop()

# ---------------------- HELPER FUNCTION ----------------------
def write_to_mongo(df, collection_name):
    df.write \
      .format("mongo") \
      .mode("append") \
      .option("collection", collection_name) \
      .save()

# ---------------------- PROCESS EACH MICRO-BATCH ----------------------
def process_batch(df, epoch_id):
    # ------------------ DIMENSIONS ------------------
    dim_customers = df.select("customer_id", "loyalty_tier").dropDuplicates()
    dim_products = df.select("product_id", "category").dropDuplicates()
    dim_time = df.withColumn("date", to_date("order_timestamp")) \
                 .withColumn("hour", hour("order_timestamp")) \
                 .withColumn("minute", minute("order_timestamp")) \
                 .select("order_timestamp", "date", "hour", "minute").dropDuplicates()
    dim_location = df.select("city", "country").dropDuplicates()
    dim_payments = df.select("payment_type", "payment_status").dropDuplicates()

    write_to_mongo(dim_customers, DIM_COLLECTIONS["customers"])
    write_to_mongo(dim_products, DIM_COLLECTIONS["products"])
    write_to_mongo(dim_time, DIM_COLLECTIONS["time"])
    write_to_mongo(dim_location, DIM_COLLECTIONS["location"])
    write_to_mongo(dim_payments, DIM_COLLECTIONS["payments"])

    # ------------------ FACT TABLE ------------------
    fact_orders = df.select(
        "order_id", "customer_id", "product_id", "order_timestamp",
        "city", "country", "payment_type", "payment_status",
        "quantity", "unit_price", "discount", "tax", "shipping_cost",
        "total_amount", "order_status"
    )
    write_to_mongo(fact_orders, FACT_COLLECTION)

    # ------------------ DERIVED KPIs ------------------
    kpi_df = df.groupBy("city").agg(
        sum("total_amount").alias("revenue"),
        avg("total_amount").alias("avg_order_value"),
        count(when(col("payment_status")=="failed", True)).alias("failed_payments"),
        count(when(col("order_status")=="cancelled", True)).alias("cancelled_orders")
    )
    write_to_mongo(kpi_df, DIM_COLLECTIONS["kpis"])

# ---------------------- STREAMING WRITE ----------------------
query = df_clean.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("update") \
    .trigger(processingTime="10 seconds") \
    .start()

print("Spark Streaming ETL started, listening to Kafka topic:", KAFKA_TOPIC)

query.awaitTermination()
