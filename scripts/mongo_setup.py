from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["ecommerce"]

# Collections
orders_live = db["orders_live"]
archive_metadata = db["archive_metadata"]

# Create indexes
orders_live.create_index("order_id", unique=True)
orders_live.create_index("order_timestamp")
orders_live.create_index([("city", 1), ("loyalty_tier", 1)])

archive_metadata.create_index("archive_id", unique=True)

print("MongoDB setup completed!")
