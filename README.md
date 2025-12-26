Real-Time Ecommerce Big Data Analytics Pipeline
1. Project Overview

This project implements a fully dockerized real-time Big Data Analytics (BDA) pipeline for an ecommerce domain. The system continuously generates realistic streaming data, ingests it into a NoSQL database, performs real-time and near–real-time analytics, and automatically archives historical data once a size threshold is reached.

The solution is designed to support live dashboards, high data velocity, and scalable analytics, following modern big data architectural principles.

2. Business Domain & Problem Justification

Domain: Ecommerce (real-time order processing)

Business Problem:
Ecommerce managers require minute-level visibility into sales performance, customer behavior, and product demand. Traditional batch systems introduce delays and cannot support operational decision-making.

This project addresses the problem by enabling:

Continuous data ingestion

Near real-time analytics

Automatic data lifecycle management (hot vs archived data)

This makes the system suitable for real-time monitoring and decision support.

3. Real-Time Data Generation

In this project, streaming e-commerce data is generated continuously using a statistical, AI-inspired data generator, rather than simple random value generators. The generator is designed to mimic realistic behaviors observed in real-world online shopping environments. It produces skewed order distributions where some products or categories are more popular than others, time-dependent purchase patterns reflecting peak and off-peak shopping hours, and trends at the category level that replicate actual consumer preferences. Additionally, the generator incorporates correlations between customers and their locations, ensuring that regional buying patterns, city-level demand, and customer segmentation are preserved. By modeling these statistical relationships, the generator produces data that behaves like a true production system, providing a realistic foundation for analytical queries, KPI computation, and dashboard visualization.

4. Data Model & Schema Design

The core dataset is centered around orders, represented as a fact table containing key numerical measures and associated dimensions.

Numerical KPIs (Facts):
The fact table captures essential metrics for analytics, including order amount, quantity, discount, tax, and total price. These metrics form the foundation for operational and strategic decision-making, such as revenue calculations, average order value, and profitability analysis.

Dimensions:
To enable comprehensive analytical queries, the fact table is linked to multiple dimensions, including customer, product, category, city, country, payment method, order status, and timestamp. These dimensions allow the system to perform join-based queries using standard SQL operations like WHERE, GROUP BY, and HAVING. For example, one can analyze revenue trends by city, product category performance, or customer purchasing behavior over time.

The schema is designed to support both real-time analytics from hot storage (MongoDB) and historical analytics from cold storage (HDFS). It ensures that BI dashboards can query data efficiently and produce visualizations such as revenue trends, top-selling products, failed payment analysis, and order volume dynamics.

5. Data Dictionary

Attribute	Description

order_id	Unique identifier for each order
customer_id	Reference to the customer
product_id	Reference to the product
category	Product category
order_amount	Base price of the order
discount	Discount applied to the order
tax	Tax amount applied
total_price	Final payable amount
city	Customer’s city
country	Customer’s country
timestamp	Time when the order was placed
payment_method	Method used for payment
order_status	Current status of the order

This data dictionary ensures clarity for all stakeholders, providing both developers and business users with a consistent understanding of each attribute. It also supports join-based queries for dashboard generation and KPI computation, enabling the system to provide actionable insights into real-time sales performance and customer behavior.

6. Data Volume and Archiving Strategy

In this project, the system is designed to maintain at least 300 MB of e-commerce data at all times, ensuring that both real-time and historical data are available for analytics. Data is continuously generated using an AI-based streaming generator, which produces realistic orders, payments, and cancellations. The generator follows statistical patterns observed in real-world e-commerce systems, including skewed order distributions, time-dependent purchase trends, and correlations between customers, products, and locations. This ensures that the streaming data is suitable for analytical queries and dashboard visualization.

To handle high-velocity data and ensure timely insights, MongoDB serves as the hot storage layer. Freshly generated streaming data is stored in MongoDB, allowing the system to perform real-time aggregation and update key performance indicators (KPIs) such as total revenue, total orders, average order value, and other metrics. MongoDB supports efficient reads and writes, which is critical for maintaining the minute-level live dashboard updates required by managers for operational decision-making.

When the size of the MongoDB collection exceeds the 300 MB threshold, older records are automatically moved to Hadoop HDFS, which serves as the cold storage layer. HDFS is ideal for storing large, immutable datasets, providing durability, fault tolerance, and scalability. The archived data is stored in JSON format and partitioned by timestamp to enable efficient query processing over historical datasets. Alongside the archived data, metadata is stored in structured JSON, including information such as archive timestamp, the number of records archived, and the data range covered. This metadata allows the system to track the lifecycle of each dataset and facilitates efficient retrieval for batch analytics or OLAP queries.

This archiving strategy ensures that the system can continuously ingest streaming data while preventing MongoDB from growing beyond manageable limits. By integrating HDFS for cold storage, the architecture provides a long-term analytics layer, allowing Spark to process both fresh and historical data for KPI computation, trend analysis, and BI dashboards. This approach balances real-time responsiveness with historical analytical capabilities, making the system suitable for operational monitoring, strategic decision-making, and compliance purposes.

7. Architecture Description

The architecture follows a layered big data design:


<img width="733" height="593" alt="Screenshot 2025-12-26 at 9 53 11 PM" src="https://github.com/user-attachments/assets/e3582993-ebd1-4c23-a057-80207bcc8d0b" />

a) Ingestion Layer

The ingestion layer is responsible for capturing all e-commerce events as they occur in real-time. A data generator produces realistic order data, including information about customers, products, quantities, payments, and cancellations, simulating the behavior of a live e-commerce platform. These events are streamed into Kafka, a high-throughput distributed message broker that ensures reliable delivery of data to downstream consumers. Zookeeper manages Kafka’s metadata and cluster coordination, maintaining the integrity and availability of the streaming system. By decoupling data producers and consumers, this layer allows the system to handle high-velocity streams while providing a buffer for processing components downstream.

b) Hot Storage Layer

The hot storage layer is implemented using MongoDB, a NoSQL document database designed to store recent, high-velocity data. MongoDB holds fresh streaming events from Kafka and serves as the primary source for operational dashboards. This layer enables the system to compute real-time key performance indicators (KPIs), such as total revenue, total orders, and average order value, providing immediate insights for business managers. By keeping only the most recent data, MongoDB ensures fast read and write performance, which is essential for live analytics and operational decision-making.

c) Cold Storage Layer

Cold storage is built on Hadoop HDFS, which provides a scalable, fault-tolerant repository for large volumes of historical e-commerce data. Data from MongoDB or directly from the streaming pipeline can be written into HDFS in a structured and partitioned format, often organized by timestamp to optimize query performance. This layer allows the system to preserve historical records for long-term analysis, compliance, and auditing purposes. Cold storage is designed for immutability and high durability rather than low-latency access, making it ideal for batch processing and analytical computations that do not require real-time responses.

d) Processing & Analytics Layer

The processing and analytics layer is powered by Apache Spark, which enables both batch and streaming computations on data from hot and cold storage. Spark reads fresh events from MongoDB and historical datasets from HDFS, transforming and aggregating them into analytics-ready information. It performs computations such as revenue trends, average order values, and counts of failed or cancelled orders. Resource management is handled by YARN, which orchestrates Spark jobs, manages cluster resources, and ensures efficient execution across multiple worker nodes. This layer transforms raw, unstructured data into structured, queryable datasets for downstream consumption.

e) Analytics Serving Layer

The analytics serving layer uses HBase, a column-oriented NoSQL database, to store processed and aggregated data in a format optimized for fast, random-access queries. Spark writes results to HBase, where dashboards and BI tools can efficiently retrieve historical and aggregated metrics. This layer complements MongoDB, which provides live data, by enabling analytics over large historical datasets without impacting the performance of the hot operational storage. HBase allows the system to provide fast responses to analytical queries, even as data volumes grow.

f) Visualization Layer

The visualization layer is composed of dashboards built with frameworks such as Streamlit or Dash. These dashboards connect to both MongoDB and HBase to provide a unified view of real-time and historical analytics. Users can monitor live KPIs, view trends over time, and analyze operational metrics without having to query raw data manually. This layer translates the processed data into actionable insights, enabling e-commerce managers to make timely, data-driven decisions.


8. Dashboard and Live Updates

The system provides a fully interactive dashboard that continuously reflects the latest e-commerce activity. Analytical KPIs, such as total revenue, average order value, sales by city, and product category performance, are updated in real-time as new data is ingested and processed. Dashboards are configured to refresh every minute, ensuring that managers can monitor key metrics with minimal latency. This enables live tracking of revenue trends, order volume dynamics, and category-level sales performance, supporting operational decision-making and rapid responses to emerging trends or anomalies in customer behavior. By integrating both hot data from MongoDB and processed analytics from HBase, the dashboard delivers a comprehensive view that combines real-time and historical insights.

9. Key Outcomes

The project successfully implements an end-to-end real-time Big Data Analytics (BDA) pipeline for the e-commerce domain. The system includes automated data lifecycle management, moving data seamlessly between hot and cold storage while maintaining optimal performance. The architecture is scalable, modular, and fully containerized, allowing easy deployment and reproducibility using Docker. Analytical workflows are powered by Spark, which transforms streaming and historical data into analytics-ready formats stored in HBase and MongoDB. The data schema and storage design are optimized for OLAP-style queries, supporting KPI computation, join-based analytics, and BI dashboard generation. Overall, the pipeline demonstrates a robust, real-time analytics capability suitable for operational monitoring, strategic decision-making, and long-term trend analysis.
