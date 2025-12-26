Real-Time Ecommerce Big Data Analytics Pipeline
1. Project Overview

This project implements a fully dockerized real-time Big Data Analytics (BDA) pipeline for an ecommerce domain. The system continuously generates realistic streaming data, ingests it into a NoSQL database, performs real-time and near–real-time analytics, and automatically archives historical data once a size threshold is reached.

The solution is designed to support live dashboards, high data velocity, and scalable analytics, following modern big data architectural principles.

2. Business Domain & Problem Justification

Domain: Ecommerce (real-time order processing)

Business Problem:
Ecommerce managers require minute-level visibility into sales performance, customer behavior, and product demand. Traditional batch systems introduce delays and cannot support operational decision-making.

This project addresses the problem by enabling:

-Continuous data ingestion

-Near real-time analytics

-Automatic data lifecycle management (hot vs archived data)

This makes the system suitable for real-time monitoring and decision support.

3. Real-Time Data Generation

In this project, streaming e-commerce data is generated continuously using a statistical, AI data generator, rather than simple random value generators. The generator is designed to mimic realistic behaviors observed in real-world online shopping environments. It produces skewed order distributions where some products or categories are more popular than others, time-dependent purchase patterns reflecting peak and off-peak shopping hours, and trends at the category level that replicate actual consumer preferences. Additionally, the generator incorporates correlations between customers and their locations, ensuring that regional buying patterns, city-level demand, and customer segmentation are preserved. By modeling these statistical relationships, the generator produces data that behaves like a true production system, providing a realistic foundation for analytical queries, KPI computation, and dashboard visualization.

4. Data Model & Schema Design

The core dataset is centered around orders, represented as a fact table containing key numerical measures and associated dimensions.

Numerical KPIs (Facts):
The fact table captures essential metrics for analytics, including order amount, quantity, discount, tax, and total price. These metrics form the foundation for operational and strategic decision-making, such as revenue calculations, average order value, and profitability analysis.

Dimensions:
To enable comprehensive analytical queries, the fact table is linked to multiple dimensions, including customer, product, category, city, country, payment method, order status, and timestamp. These dimensions allow the system to perform join-based queries using standard SQL operations like WHERE, GROUP BY, and HAVING. For example, one can analyze revenue trends by city, product category performance, or customer purchasing behavior over time.

The schema is designed to support both real-time analytics from hot storage (MongoDB) and historical analytics from cold storage (HDFS). It ensures that BI dashboards can query data efficiently and produce visualizations such as revenue trends, top-selling products, failed payment analysis, and order volume dynamics.

5. Data Dictionary

<img width="685" height="558" alt="Screenshot 2025-12-26 at 10 24 44 PM" src="https://github.com/user-attachments/assets/e2e534ea-03ad-400e-9a3f-a53c0e2cac14" />


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

The ingestion layer captures all e-commerce events in real time. The AI-based data generator produces realistic order events with customer, product, quantity, payment, and cancellation information. These events are streamed into Kafka, a high-throughput distributed message broker, while Zookeeper manages cluster coordination and metadata. By decoupling producers from consumers, this layer can handle high-velocity data streams efficiently and provide a buffer for downstream processing.

b) Hot Storage Layer

MongoDB serves as the hot storage layer, storing the processed streaming data including fact tables, dimension tables, and derived KPIs computed by Spark. This design allows the real-time dashboard to query the latest data efficiently. Separating facts and dimensions supports join-based queries for BI dashboards, such as revenue trends by city, product category performance, or customer-level insights.

c) Cold Storage Layer

Once MongoDB exceeds the defined size threshold (~300 MB), older records are archived to Hadoop HDFS in JSON format, partitioned by timestamp. Metadata is stored in structured JSON, capturing archive time, record count, and data range. This layer allows Spark to process historical data for trend analysis or batch analytics without impacting the performance of hot storage.

d) Processing & Analytics Layer

Apache Spark Structured Streaming consumes the Kafka topic with generated orders. It performs ETL, cleaning, and transforming the data into fact and dimension tables suitable for analytics. Dimension tables include customers, products, time, location, and payments, while the fact table contains detailed order-level records. Spark also computes derived KPIs like revenue by city, average order value, failed payments, and cancelled orders. These datasets are written to MongoDB for real-time analytics. Spark’s micro-batch processing ensures updates every 10 seconds, allowing dashboards to reflect near real-time metrics.

e) Analytics Serving Layer

For large-scale historical analytics, HBase can be used as a column-oriented storage layer. Spark writes aggregated results to HBase to support fast, random-access queries over historical datasets. This layer is optional and complements MongoDB, enabling analytical queries on large historical datasets without impacting real-time performance.

f) Visualization Layer

The dashboard reads KPIs and analytical data from MongoDB, providing live updates every minute. Visualizations include total revenue, total orders, average order value, revenue by city, average order value by city, failed payments, and cancelled orders. This layer combines near real-time metrics from hot storage with processed insights from Spark, giving operational visibility to managers.


8. Dashboard and Live Updates

The system provides a fully interactive dashboard that continuously reflects live e-commerce activity. Key performance indicators, such as total revenue, total orders, average order value, and city-level metrics, are updated every minute from MongoDB. This allows managers to monitor operational trends and customer behavior in near real-time. By integrating Spark-computed KPIs, the dashboard combines raw event data with analytical insights for actionable decision-making. Historical analytics can optionally be retrieved from HDFS or HBase if integrated.

9. Key Outcomes

The project successfully implements an end-to-end real-time Big Data Analytics (BDA) pipeline for the e-commerce domain. The system includes automated data lifecycle management, moving data seamlessly between hot and cold storage while maintaining optimal performance. The architecture is scalable, modular, and fully containerized, allowing easy deployment and reproducibility using Docker. Analytical workflows are powered by Spark, which transforms streaming data into analytics-ready formats stored in MongoDB. The data schema and storage design are optimized for OLAP-style queries, supporting KPI computation, join-based analytics, and BI dashboard generation. Overall, the pipeline demonstrates a robust, real-time analytics capability suitable for operational monitoring, strategic decision-making, and long-term trend analysis.
