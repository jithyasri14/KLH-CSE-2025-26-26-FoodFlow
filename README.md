# FOODFLOW : End-to-End Food Delivery Data Engineering & Analytics Platform

FoodFlow is an end-to-end data engineering and analytics platform designed to transform raw food-delivery data into meaningful insights. The system integrates multiple datasets, performs data cleaning and validation, builds an analytics-ready dataset, and applies Machine Learning to predict food-delivery order performance.

The platform also demonstrates simulated real-time order processing through a Flask API, SQLite database, and interactive Streamlit dashboard.

---

##  1. Problem Statement

Food delivery platforms generate large volumes of data from different sources, including customers, restaurants, orders, payments, deliveries, and reviews.

Managing these datasets independently creates challenges in data integration, data quality, operational analysis, and delivery performance monitoring.

FoodFlow addresses these challenges by developing a unified data engineering workflow that ingests, cleans, validates, and integrates multiple food-delivery datasets.

The processed data is used to predict whether an order will be **On-Time, Delayed, or Cancelled**, while an interactive dashboard provides operational insights and simulated real-time monitoring.

---

##  2. Project Objectives

- Ingest multiple food-delivery datasets.
- Perform data cleaning and preprocessing.
- Validate data quality and handle missing or invalid records.
- Integrate multiple datasets using common identifiers.
- Generate an analytics-ready unified dataset.
- Apply Random Forest for order performance prediction.
- Develop a Flask-based prediction API.
- Implement simulated real-time order processing.
- Store incoming orders and prediction results in SQLite.
- Develop an interactive Streamlit dashboard.
- Provide historical and simulated live operational insights.

---

##  3. System Architecture

### 3.1 Historical Data Processing

```text
+--------------------------------------------------+
|             FOOD DELIVERY DATA SOURCES           |
|                                                  |
| Customers | Restaurants | Orders | Payments      |
| Deliveries | Reviews                             |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|                 DATA INGESTION                   |
|                 Python + Pandas                  |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|                  DATA CLEANING                   |
|                                                  |
| Duplicate Removal | Missing Values               |
| Invalid Record Handling                          |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|             DATA QUALITY VALIDATION              |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|                 DATA INTEGRATION                 |
|                                                  |
| Customer ID | Restaurant ID | Order ID            |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|             FEATURE ENGINEERING                 |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|              RANDOM FOREST MODEL                 |
|                                                  |
|       On-Time | Delayed | Cancelled               |
+--------------------------------------------------+
```

### 3.2 Simulated Real-Time Processing

```text
+-------------------------+
|      NEW ORDER          |
+------------+------------+
             |
             v
+-------------------------+
|   PYTHON ORDER          |
|     SIMULATOR           |
+------------+------------+
             |
             v
+-------------------------+
|      FLASK API          |
+------------+------------+
             |
             v
+-------------------------+
|   RANDOM FOREST MODEL   |
+------------+------------+
             |
             v
+-------------------------+
|    ORDER PREDICTION     |
|                        |
| On-Time / Delayed /     |
| Cancelled               |
+------------+------------+
             |
             v
+-------------------------+
|     SQLITE DATABASE     |
+------------+------------+
             |
             v
+-------------------------+
|   STREAMLIT DASHBOARD   |
+-------------------------+
```

---

##  4. Technology Stack

| Category | Technology | Purpose |
|:---|:---|:---|
| Programming Language | Python | Core application development |
| Data Processing | Pandas | Data cleaning and integration |
| Machine Learning | Scikit-learn | Model development and evaluation |
| ML Algorithm | Random Forest | Order performance classification |
| Backend Framework | Flask | Prediction API |
| Database | SQLite | Store order prediction records |
| Dashboard | Streamlit | Interactive visualization |
| Version Control | Git | Source code management |
| Repository | GitHub | Project collaboration |

---

##  5. Dataset Description

FoodFlow works with six food-delivery datasets.

| Dataset | Description |
|:---|:---|
| Customers | Customer-related information |
| Restaurants | Restaurant details and ratings |
| Orders | Order details, values, and status |
| Payments | Payment-related information |
| Deliveries | Delivery distance and delivery-time information |
| Reviews | Customer feedback and ratings |

The datasets are integrated using common identifiers:

- `customer_id`
- `restaurant_id`
- `order_id`

**Dataset Source:** Kaggle

Dataset URL: [Add the exact Kaggle dataset link]

---

##  6. Data Engineering Workflow

### 6.1 Data Ingestion

Python and Pandas are used to read the six source CSV datasets into DataFrames.

### 6.2 Data Cleaning

The cleaning process includes:

- Removing duplicate records.
- Handling missing values.
- Replacing missing numerical values using median values.
- Handling missing categorical values.
- Validating restaurant ratings.
- Removing invalid order records.

### 6.3 Data Quality Validation

The validation stage checks whether the processed datasets satisfy the configured data-quality conditions before further processing.

### 6.4 Data Integration

The cleaned datasets are combined using common identifiers such as customer ID, restaurant ID, and order ID.

This produces a unified food-delivery dataset.

### 6.5 Feature Engineering

Additional features are derived from the integrated dataset, including:

- `order_hour`
- `order_day`
- `order_performance`

The target variable `order_performance` contains three categories:

1. Cancelled
2. Delayed
3. On-Time

The current implementation determines order performance using cancellation status and the comparison between actual and estimated delivery time.

---

##  7. Machine Learning Methodology

FoodFlow uses a **Random Forest Classifier** to predict food-delivery order performance.

### Input Features

- Order value
- Delivery distance
- Preparation time
- Estimated delivery time
- Restaurant rating
- Customer age

### Output Classes

| Class | Description |
|:---|:---|
| On-Time | Predicted delivery within estimated time |
| Delayed | Predicted delivery exceeding estimated time |
| Cancelled | Order classified as cancelled |

### Model Configuration

| Parameter | Value |
|:---|:---|
| Algorithm | Random Forest Classifier |
| Number of Estimators | 150 |
| Training Data | 80% |
| Testing Data | 20% |
| Random State | 42 |
| Class Weight | Balanced |

### Model Performance

The previously recorded model-training run produced the following results:

| Evaluation Metric | Result |
|:---|---:|
| Accuracy | 81.1% |
| Weighted Precision | 78% |
| Weighted Recall | 81% |
| Weighted F1-Score | 78% |

These values represent a previous training run. Results may vary if the dataset or implementation changes.

---

##  8. Simulated Real-Time Processing

FoodFlow demonstrates real-time-style order processing using a Python-based order simulator and Flask API.

### Processing Workflow

1. The order simulator generates incoming order records.
2. The generated order information is sent to the Flask API.
3. The API loads the trained Random Forest model.
4. The model predicts the order performance.
5. The prediction and associated information are stored in SQLite.
6. The Streamlit dashboard displays the incoming order records and prediction results.

**Note:** The current implementation uses simulated real-time processing. It does not use Kafka-based streaming in the running prototype.

---

##  9. Prediction API

The Flask API acts as an interface between incoming orders and the trained Machine Learning model.

**Responsibilities:**

- Receive new order information.
- Process the input features.
- Load the trained Random Forest model.
- Generate order performance predictions.
- Return the predicted class and probability values.

The local API runs on:

`http://127.0.0.1:5000`

---

##  10. Data Storage

SQLite is used to store simulated real-time order information and prediction results.

**Database File:**

`data/processed/foodflow_realtime.db`

The database supports dashboard monitoring and retrieval of stored prediction records.

---

##  11. Interactive Dashboard

FoodFlow provides an interactive dashboard developed using Streamlit.

### Dashboard Modules

**1. Platform Overview**

- Total live events
- Cancelled orders
- Delayed orders
- On-Time orders
- Live order value

**2. Realtime Stream**

- Incoming simulated orders
- Order details
- Predicted order performance
- Live prediction records
- Downloadable records

**3. Operational ML**

- Model confidence monitoring
- Prediction probabilities
- Most likely prediction class
- Model performance insights

The displayed confidence represents the highest class probability returned by the Random Forest model. It is not a guarantee that the prediction is correct.

---

##  12. Novelty and Key Contributions

FoodFlow brings together multiple components into one integrated food-delivery data engineering prototype.

### Key Contributions

**1. Multi-Source Data Integration**

Combines six food-delivery data domains into a unified analytics-ready dataset.

**2. End-to-End Data Engineering Workflow**

Connects data ingestion, cleaning, validation, integration, feature engineering, and storage.

**3. Three-Class Order Performance Prediction**

Uses Random Forest to classify food-delivery orders into On-Time, Delayed, and Cancelled categories.

**4. API-Based Machine Learning Integration**

Exposes the trained prediction model through a Flask API, separating prediction logic from the dashboard.

**5. Simulated Real-Time Prediction**

Demonstrates the processing of incoming orders, prediction generation, and database storage.

**6. Unified Analytics Dashboard**

Combines operational monitoring and machine learning prediction insights in a single interactive interface.

---

##  13. Project Outcomes

The implemented FoodFlow prototype provides:

- A multi-source food-delivery data processing workflow.
- Cleaned and validated datasets.
- An integrated analytics-ready dataset.
- A trained Random Forest classification model.
- Order performance predictions.
- A Flask-based prediction service.
- A simulated real-time order processing pipeline.
- SQLite-based prediction storage.
- An interactive Streamlit dashboard.

---

##  14. Limitations

- Incoming real-time orders are simulated rather than collected from a live food-delivery platform.
- The current prototype does not use Kafka or Spark in its running pipeline.
- SQLite is used for local prototype storage.
- Model performance depends on data quality, feature selection, and target-label generation.
- Predictions are estimates and cannot guarantee actual delivery outcomes.

---

##  15. Future Scope

- Integrate Apache Kafka for event streaming.
- Use Apache Spark for distributed data processing.
- Introduce Apache Airflow for workflow orchestration.
- Migrate to PostgreSQL for larger-scale data storage.
- Implement advanced machine learning models.
- Improve prediction performance for minority classes.
- Add pipeline monitoring and alerting.
- Deploy the platform to a cloud environment.
- Integrate authorized live food-delivery data sources.

---

##  16. Team Members

| S. No. | Name | Roll Number | 
|:---:|:---|:---|
| 1 | Pagadala Goda Sahasra | 2420090128 | 
| 2 | Jithyasri Sammeta | 2420030586 |
| 3 | TAMMANA KAMESWARI AMULYA | 2420030434 | 


---
## 17. Faculty Guidance

**Under the Guidance of**

**Dr. N. Shirisha**  
Associate Professor  
Department of Computer Science and Engineering 
KL University






---

##  Project Information

| Detail | Information |
|:---|:---|
| Project Name | FoodFlow |
| Domain | Data Engineering, Analytics and Machine Learning |
| Prediction Task | Food Delivery Order Performance Classification |
| Data Sources | Six Food-Delivery Datasets |
| ML Algorithm | Random Forest |
| Current Execution | Historical Batch Processing + Simulated Real-Time Prediction |
