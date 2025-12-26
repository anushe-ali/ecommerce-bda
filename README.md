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

Ingestion Layer
Real-time ecommerce events are generated and streamed into MongoDB.

Hot Storage Layer
MongoDB stores fresh, high-velocity data for fast access and live analytics.

Archival Layer
A dedicated archiver service monitors data size and moves older data into HDFS once thresholds are exceeded.

Processing & Analytics Layer
Apache Spark processes both:

Fresh data from MongoDB

Historical data from HDFS
Spark performs aggregations, OLAP-style queries, and KPI computation using SQL.

Serving Layer
Processed analytical results are exposed to a BI/dashboard layer for visualization.

Containerization & Management
All services are fully dockerized, ensuring reproducibility and isolation.

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
