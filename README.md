# Real-Time E-Commerce Big Data Analytics Pipeline

---

## 1. Project Overview

This project implements a fully Dockerized **real-time Big Data Analytics (BDA) pipeline** for the e-commerce domain. The system continuously generates realistic streaming data, ingests it into a NoSQL database, performs real-time and near–real-time analytics, and automatically archives historical data once a size threshold is reached.

The solution is designed to support **live dashboards**, **high data velocity**, and **scalable analytics**, following modern big data architectural principles.

---

## 2. Business Domain & Problem Justification

**Domain:**
E-commerce (real-time order processing)

**Business Problem:**
E-commerce managers require minute-level visibility into sales performance, customer behavior, and product demand. Traditional batch processing systems introduce delays and are unsuitable for operational decision-making.

This project addresses the problem by enabling:

* Continuous data ingestion
* Near real-time analytics
* Automatic data lifecycle management (hot vs cold storage)

This makes the system suitable for **real-time monitoring and decision support**.

---

## 3. Real-Time Data Generation

Streaming e-commerce data is generated continuously using a **statistical, AI-based data generator**, rather than simple random value generators. The generator mimics real-world online shopping behavior by modeling:

* Skewed order distributions where certain products or categories are more popular
* Time-dependent purchase patterns (peak vs off-peak hours)
* Category-level trends reflecting real consumer preferences
* Correlations between customers and locations, preserving regional demand patterns

By modeling these statistical relationships, the generator produces data that behaves like a real production system. This provides a realistic foundation for analytical queries, KPI computation, and dashboard visualization.

---

## 4. Data Model & Schema Design

The core dataset is centered around **orders**, represented as a **fact table** with associated **dimensions**.

### Numerical KPIs (Facts)

The fact table captures essential numerical metrics, including:

* Order amount
* Quantity
* Discount
* Tax
* Total price

These metrics support revenue analysis, average order value calculations, and profitability insights.

### Dimensions

The fact table is linked to multiple dimensions, including:

* Customer
* Product
* Category
* City
* Country
* Payment method
* Order status
* Timestamp

This design enables join-based analytical queries using standard SQL operations such as `WHERE`, `GROUP BY`, and `HAVING`. Analysts can evaluate revenue by city, category performance, or customer purchasing behavior over time.

The schema supports both:

* **Real-time analytics** from hot storage (MongoDB)
* **Historical analytics** from cold storage (HDFS)

---

## 5. Data Dictionary

![Data Dictionary](https://github.com/user-attachments/assets/e2e534ea-03ad-400e-9a3f-a53c0e2cac14)

The data dictionary ensures clarity for all stakeholders by providing a consistent understanding of each attribute. It supports join-based queries for dashboard generation and KPI computation, enabling actionable insights into real-time sales performance and customer behavior.

---

## 6. Data Volume and Archiving Strategy

The system maintains **at least 300 MB of e-commerce data** at all times, supporting both real-time and historical analytics. Data is continuously generated using an AI-based streaming generator that produces realistic orders, payments, and cancellations.

### Hot Storage: MongoDB

MongoDB serves as the hot storage layer, storing the most recent streaming data. It supports:

* Efficient reads and writes
* Real-time aggregation
* Minute-level KPI updates

Key KPIs include total revenue, total orders, average order value, and city-level metrics.

### Cold Storage: Hadoop HDFS

When MongoDB exceeds the **300 MB threshold**, older records are automatically archived to Hadoop HDFS. Archived data is:

* Stored in JSON format
* Partitioned by timestamp
* Accompanied by structured metadata (archive timestamp, record count, data range)

This strategy prevents unbounded growth of MongoDB while enabling long-term analytics. Spark can process both fresh and archived data for trend analysis, KPI recomputation, and BI reporting.

---

## 7. Architecture Description

The system follows a **layered big data architecture**:

![Architecture Diagram](https://github.com/user-attachments/assets/e3582993-ebd1-4c23-a057-80207bcc8d0b)

### a) Ingestion Layer

* AI-based data generator produces realistic e-commerce events
* Kafka ingests high-velocity streaming data
* Zookeeper manages cluster coordination and metadata
* Producer–consumer decoupling ensures scalability and reliability

### b) Hot Storage Layer

* MongoDB stores fact tables, dimension tables, and derived KPIs
* Optimized for real-time dashboard queries
* Schema separation enables efficient join-based analytics

### c) Cold Storage Layer

* Hadoop HDFS stores archived data beyond the MongoDB threshold
* Data is partitioned by timestamp with structured metadata
* Enables historical analytics without impacting hot storage performance

### d) Processing & Analytics Layer

* Spark Structured Streaming consumes Kafka topics
* Performs ETL, cleaning, and transformation
* Computes derived KPIs such as:

  * Revenue by city
  * Average order value
  * Failed payments
  * Cancelled orders
* Micro-batch processing updates data every ~10 seconds

### e) Analytics Serving Layer

* Optional HBase integration for large-scale historical analytics
* Stores aggregated metrics for fast random-access queries
* Complements MongoDB without impacting real-time workloads

### f) Visualization Layer

* Dash + Plotly dashboards read from MongoDB
* Live updates every minute
* Visualizations include revenue trends, order counts, AOV, and failure analysis

---

## 8. Dashboard and Live Updates

The system provides an interactive dashboard that reflects live e-commerce activity. Key performance indicators such as total revenue, total orders, average order value, and city-level metrics update every minute.

By combining raw event data with Spark-computed KPIs, the dashboard enables near real-time operational monitoring and data-driven decision-making. Historical insights can optionally be retrieved from HDFS or HBase.

---

## 9. Key Outcomes

* End-to-end real-time Big Data Analytics pipeline for e-commerce
* Automated data lifecycle management across hot and cold storage
* Scalable, modular, and fully containerized architecture using Docker
* Near real-time KPI dashboards for operational decision-making
* Analytics-ready schema optimized for OLAP-style queries
* Historical analytics support for long-term trend analysis

---


# Real-Time E-Commerce Setup

Follow the steps below to run the real-time e-commerce dashboard with optional data archiving.

---

## Step 1: Build and Start Containers

From the project root directory, build and start all required services:

```bash
docker compose build
docker compose up -d
```

* The `-d` flag runs containers in detached mode.
* This starts MongoDB, Kafka, Spark, Hadoop, and the dashboard service.

---

## Step 2: Start Spark Streaming

### 2.1 Enter the Spark Master Container

```bash
docker exec -it spark-master-bda bash
```

### 2.2 Copy Spark Streaming Script into the Container

From another terminal on the host machine:

```bash
docker cp scripts/spark_transform.py spark-master-bda:/spark_transform.py
```

### 2.3 Submit the Spark Streaming Job

Inside the Spark master container, run:

```bash
/spark/bin/spark-submit \
  --master spark://spark-master-bda:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.2 \
  /spark_transform.py
```

This job:

* Consumes real-time data from Kafka
* Performs ETL and KPI computation using Spark Structured Streaming
* Writes processed data and derived KPIs to MongoDB

---

## Step 3: Access the Dashboard

Open your browser and navigate to:

```
http://localhost:8050
```

* The dashboard displays live KPIs and analytical charts.
* Data refreshes automatically every minute.

---

## Step 4: Enable Data Archiving

To archive older MongoDB data into HDFS when storage exceeds the threshold:

### 4.1 Navigate to the Scripts Directory

```bash
cd scripts
```

### 4.2 Build the Archiver Docker Image

```bash
docker build -t ecommerce-bda-archiver -f Dockerfile.archiver .
```

### 4.3 Run the Archiver Container

```bash
docker run -it --rm \
  --name ecommerce-archiver \
  --network bda_network \
  ecommerce-bda-archiver \
  python3 archive_orders.py
```

* Older MongoDB records are moved to HDFS according to the archiving policy.
* Metadata such as archive timestamp and record counts is preserved.
* The `bda_network` allows communication between MongoDB and HDFS.

---

## Step 4: Airflow Setup and Configuration

Follow these steps to build, start, and configure Apache Airflow for workflow orchestration.

---

### 4.1 Build the Airflow Service

From the project root directory, build the Airflow image using the standalone Docker Compose file:

```bash
docker compose -f docker-compose-standalone.yml build airflow
```

---

### 4.2 Start the Airflow Container

Start the Airflow service in detached mode:

```bash
docker compose -f docker-compose-standalone.yml up -d airflow
```

This initializes:

* Airflow webserver
* Airflow scheduler
* Metadata database

---

### 4.3 Access the Airflow Container

Enter the running Airflow container:

```bash
docker exec -it airflow bash
```

---

### 4.4 Install Required Python Dependencies

Inside the Airflow container, install the required packages:

```bash
pip install pymongo hdfs kafka-python
```

These libraries enable:

* MongoDB integration
* HDFS interaction
* Kafka-based ingestion and monitoring

---

### 4.5 Create an Airflow Admin User

Create an admin user for accessing the Airflow web UI:

```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@airflow.com
```

---

### 4.6 Access the Airflow Web UI

Open your browser and navigate to:

```
http://localhost:8080
```

---

### 4.7 Log In to Airflow

Log in using the following credentials:

* **Username:** `admin`
* **Password:** (the password you set during user creation)

Once logged in, you can:

* Enable and trigger DAGs
* Monitor task execution
* Manage schedules and dependencies
