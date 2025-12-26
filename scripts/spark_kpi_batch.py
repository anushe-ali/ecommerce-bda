from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KPI Batch Analytics") \
    .config("spark.mongodb.input.uri", "mongodb://mongo:27017/ecommerce") \
    .config("spark.mongodb.output.uri", "mongodb://mongo:27017/ecommerce") \
    .getOrCreate()

fact_orders = spark.read.format("mongo").option("collection", "fact_orders").load()

fact_orders.createOrReplaceTempView("orders")

kpis = spark.sql("""
SELECT
  city,
  SUM(total_amount) AS revenue,
  AVG(total_amount) AS avg_order_value,
  SUM(CASE WHEN payment_status = 'failed' THEN 1 ELSE 0 END) AS failed_payments,
  SUM(CASE WHEN order_status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders
FROM orders
GROUP BY city
""")

kpis.write.format("mongo") \
    .mode("overwrite") \
    .option("collection", "kpi_city") \
    .save()
