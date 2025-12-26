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

Streaming ecommerce data is generated continuously using a statistical, AI-inspired data generator rather than purely random values.
The generator preserves realistic properties such as:

Skewed order distributions

Time-based purchase patterns

Category-level trends

Customer and location correlations

This ensures the data behaves like a real production system and remains suitable for analytical queries.

4. Data Model & Schema Design
Fact Table (Orders)

The core dataset represents ecommerce orders.

Numerical KPIs (Facts):

Order amount

Quantity

Discount

Tax

Total price

Dimensions:

Customer

Product

Category

City

Country

Payment method

Order status

Timestamp

The schema supports join-based analytical queries, including WHERE, GROUP BY, and HAVING, which are required for BI dashboards.

5. Data Dictionary (Summary)
Attribute	Description
order_id	Unique order identifier
customer_id	Customer reference
product_id	Product reference
category	Product category
order_amount	Base order price
discount	Discount applied
tax	Tax amount
total_price	Final payable amount
city	Customer city
country	Customer country
timestamp	Order time
6. Data Volume & Archiving Strategy
Data Size Requirement

The system maintains at least 300 MB of data at all times

Data is continuously generated in real time

Archiving Policy

MongoDB acts as hot storage for fresh streaming data

When the size threshold is exceeded:

Older records are archived

MongoDB is cleaned to maintain performance

Archival Storage

Hadoop HDFS

Data stored in JSON format

Partitioned by timestamp

Metadata

Archive metadata is stored in structured JSON

Includes archive time, record count, and data range

Justification:
HDFS is optimized for large, immutable historical datasets and is ideal for long-term analytics and compliance storage.

7. Architecture Description (Textual)
The architecture follows a layered big data design:


<img width="733" height="593" alt="Screenshot 2025-12-26 at 9 53 11 PM" src="https://github.com/user-attachments/assets/e3582993-ebd1-4c23-a057-80207bcc8d0b" />



1. Ingestion Layer

The ingestion layer is responsible for capturing all e-commerce events as they occur in real-time. A data generator produces realistic order data, including information about customers, products, quantities, payments, and cancellations, simulating the behavior of a live e-commerce platform. These events are streamed into Kafka, a high-throughput distributed message broker that ensures reliable delivery of data to downstream consumers. Zookeeper manages Kafka’s metadata and cluster coordination, maintaining the integrity and availability of the streaming system. By decoupling data producers and consumers, this layer allows the system to handle high-velocity streams while providing a buffer for processing components downstream.

2. Hot Storage Layer

The hot storage layer is implemented using MongoDB, a NoSQL document database designed to store recent, high-velocity data. MongoDB holds fresh streaming events from Kafka and serves as the primary source for operational dashboards. This layer enables the system to compute real-time key performance indicators (KPIs), such as total revenue, total orders, and average order value, providing immediate insights for business managers. By keeping only the most recent data, MongoDB ensures fast read and write performance, which is essential for live analytics and operational decision-making.

3. Cold Storage Layer

Cold storage is built on Hadoop HDFS, which provides a scalable, fault-tolerant repository for large volumes of historical e-commerce data. Data from MongoDB or directly from the streaming pipeline can be written into HDFS in a structured and partitioned format, often organized by timestamp to optimize query performance. This layer allows the system to preserve historical records for long-term analysis, compliance, and auditing purposes. Cold storage is designed for immutability and high durability rather than low-latency access, making it ideal for batch processing and analytical computations that do not require real-time responses.

4. Processing & Analytics Layer

The processing and analytics layer is powered by Apache Spark, which enables both batch and streaming computations on data from hot and cold storage. Spark reads fresh events from MongoDB and historical datasets from HDFS, transforming and aggregating them into analytics-ready information. It performs computations such as revenue trends, average order values, and counts of failed or cancelled orders. Resource management is handled by YARN, which orchestrates Spark jobs, manages cluster resources, and ensures efficient execution across multiple worker nodes. This layer transforms raw, unstructured data into structured, queryable datasets for downstream consumption.

5. Analytics Serving Layer

The analytics serving layer uses HBase, a column-oriented NoSQL database, to store processed and aggregated data in a format optimized for fast, random-access queries. Spark writes results to HBase, where dashboards and BI tools can efficiently retrieve historical and aggregated metrics. This layer complements MongoDB, which provides live data, by enabling analytics over large historical datasets without impacting the performance of the hot operational storage. HBase allows the system to provide fast responses to analytical queries, even as data volumes grow.

6. Visualization Layer

The visualization layer is composed of dashboards built with frameworks such as Streamlit or Dash. These dashboards connect to both MongoDB and HBase to provide a unified view of real-time and historical analytics. Users can monitor live KPIs, view trends over time, and analyze operational metrics without having to query raw data manually. This layer translates the processed data into actionable insights, enabling e-commerce managers to make timely, data-driven decisions.

(A visual architecture diagram will be added separately.)

8. Technologies Used
Component	Technology
Data Generator	Python
Streaming Storage	MongoDB
Archive Storage	Hadoop HDFS
Processing & Analytics	Apache Spark
Orchestration-ready Setup	Docker Compose
Dashboard	BI-ready API / Streamlit
Containerization	Docker
9. Dashboard & Live Updates

Analytical KPIs are updated continuously

Dashboards refresh every minute

Supports live monitoring of:

Revenue trends

Sales by location

Category performance

Order volume dynamics

10. Key Outcomes

End-to-end real-time big data pipeline

Automated data lifecycle management

Scalable and modular architecture

Fully dockerized deployment

Analytics-ready schema and storage design
