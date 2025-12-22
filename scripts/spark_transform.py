from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Ecommerce Data Transformation") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

# Path to CSV in HDFS
input_path = "/user/hadoop/ecommerce_data_part2.csv"
output_path = "/user/output/ecommerce_transformed_data"

# Load data from HDFS
df = spark.read.csv(input_path, header=True, inferSchema=True)

# Remove rows with null values
df = df.na.drop()

# Write transformed data to HDFS (append mode)
df.write.csv(output_path, header=True, mode="append")

print("Transformation complete. Data appended to HDFS at:", output_path)
