import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set the random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Number of rows in the dataset to get closer to 1GB
num_rows = 10000000  # Adjusted to meet approximately 1GB dataset size

# Define possible values for categorical columns
categories = ['Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Toys']
payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Cash on Delivery']
statuses = ['Shipped', 'Delivered', 'Pending', 'Canceled']
currencies = ['USD', 'EUR', 'GBP', 'INR']
prime_values = [True, False]

# Generate synthetic data
data = {
    'order_id': [f'ORD{str(i).zfill(8)}' for i in range(1, num_rows+1)],
    'customer_id': [random.randint(1, 100000) for _ in range(num_rows)],
    'product_id': [random.randint(1, 10000) for _ in range(num_rows)],
    'category': [random.choice(categories) for _ in range(num_rows)],
    'price': [round(random.uniform(5.0, 500.0), 2) for _ in range(num_rows)],
    'quantity': [random.randint(1, 5) for _ in range(num_rows)],
    'timestamp': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(num_rows)],
    'location': [f'Location_{random.randint(1, 50)}' for _ in range(num_rows)],
    'payment_method': [random.choice(payment_methods) for _ in range(num_rows)],
    'status': [random.choice(statuses) for _ in range(num_rows)],
    'discount': [round(random.uniform(0.0, 50.0), 2) for _ in range(num_rows)],
    'delivery_time': [random.randint(1, 10) for _ in range(num_rows)],  # in days
    'user_rating': [random.randint(1, 5) for _ in range(num_rows)],
    'is_prime': [random.choice(prime_values) for _ in range(num_rows)],
    'currency': [random.choice(currencies) for _ in range(num_rows)],
    'seller_id': [random.randint(1, 1000) for _ in range(num_rows)],
}

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Save the dataset to a CSV file
df.to_csv('D:/ecommerce_data_1GB.csv', index=False)

# Check the size of the dataset
print(f"Dataset size: {df.memory_usage(deep=True).sum() / (1024 * 1024)} MB")

# Verify the first few rows of the dataset
print(df.head())
