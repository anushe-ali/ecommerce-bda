import time
import socket
import json
from datetime import datetime, timezone as UTC

from pymongo import MongoClient
from hdfs import InsecureClient

# ===============================
# CONFIG
# ===============================

MONGO_URI = "mongodb://mongo:27017"
DB_NAME = "ecommerce"
COLLECTION_NAME = "orders_live"

SIZE_THRESHOLD_MB = 300  # archive when size > 300 MB
CHECK_INTERVAL_SEC = 10

HDFS_NAMENODE_URL = "http://namenode:50070"
HDFS_USER = "hdfs"
HDFS_ARCHIVE_DIR = "/ecommerce_archive"

# ===============================
# CLIENTS
# ===============================

mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)
db = mongo_client[DB_NAME]
orders_live = db[COLLECTION_NAME]

# ===============================
# WAIT FOR HDFS
# ===============================

def wait_for_hdfs(host="namenode", port=50070, timeout=300):
    """Wait until WebHDFS is reachable"""
    print(f"Waiting for HDFS at {host}:{port} ...")
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=5):
                print("HDFS is ready!")
                return
        except OSError:
            if time.time() - start > timeout:
                raise TimeoutError(f"HDFS not reachable after {timeout}s")
            print("HDFS not ready yet, retrying in 5s...")
            time.sleep(5)

wait_for_hdfs()

# Now HDFS client can be safely created
hdfs_client = InsecureClient(HDFS_NAMENODE_URL, user=HDFS_USER)

# ===============================
# HELPERS
# ===============================

def get_collection_size_mb(collection):
    stats = db.command("collstats", collection.name)
    return stats["size"] / (1024 * 1024)

def archive_orders_to_hdfs():
    print("Archiver started. Monitoring MongoDB collection size...")
    while True:
        try:
            size_mb = get_collection_size_mb(orders_live)

            if size_mb <= SIZE_THRESHOLD_MB:
                print(f"Current size: {size_mb:.2f} MB. No archiving needed.")
                time.sleep(CHECK_INTERVAL_SEC)
                continue

            print(f"Size {size_mb:.2f} MB > {SIZE_THRESHOLD_MB} MB. Starting archive...")

            docs = list(orders_live.find({}, {"_id": 0}))

            if not docs:
                print("No documents found to archive.")
                time.sleep(CHECK_INTERVAL_SEC)
                continue

            archive_filename = (
                f"{HDFS_ARCHIVE_DIR}/archive_"
                f"{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.json"
            )

            with hdfs_client.write(
                archive_filename,
                encoding="utf-8",
                overwrite=True
            ) as writer:
                json.dump(docs, writer)

            print(f"Archived {len(docs)} documents to HDFS: {archive_filename}")

            # OPTIONAL: uncomment if you want delete-after-archive
            # orders_live.delete_many({})

        except Exception as e:
            print(f"Failed to write to HDFS: {e}. Retrying in 30s...")
            time.sleep(30)

# ===============================
# ENTRY POINT
# ===============================

if __name__ == "__main__":
    archive_orders_to_hdfs()
