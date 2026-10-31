# FoodFlow — End-to-End Food Delivery Data Engineering and Analytics Platform

## Project objective

FoodFlow is a data engineering platform for a food-delivery ecosystem. It integrates independent customer, restaurant, order, payment, delivery, and review datasets into a consistent, analytics-ready view. The project focuses on data quality, multi-source integration, batch processing, realtime ingestion, storage, and cross-domain analytics rather than building another food-ordering application.

The delivery outcome model is one downstream analytical use case. It supports operational insight into cancelled, delayed, and on-time orders, but it is not the primary purpose of the platform.

## Run order

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/data/generate_data.py
python src/data/clean_data.py
python src/data/integrate_data.py
python src/ml/train_model.py
python src/data/validate_data_quality.py
```

The validation step checks source duplicates and missing values, foreign-key relationships, integrated order uniqueness, and the final outcome distribution. It writes `data/processed/data_quality_report.json` and exits with a failure code if a quality rule is violated.

Then open two terminals.

### Terminal 1: start the real-time pipeline

```powershell
python src/streaming/realtime_pipeline.py
```

### Terminal 2: start the live dashboard

```powershell
streamlit run src/dashboard/app.py
```

The dashboard normally opens at `http://localhost:8501` and refreshes every 3 seconds.

The dashboard Control Panel can change the refresh interval, pause or resume realtime ingestion, reset the live analysis, filter the stream, and export filtered records.

### Optional API

```powershell
python src/api/prediction_api.py
```

The API runs at `http://127.0.0.1:5000`.

## Grafana monitoring

FoodFlow includes a Prometheus exporter for the realtime SQLite pipeline. Install the updated requirements, then start the exporter:

```powershell
pip install -r requirements.txt
python src/monitoring/metrics_exporter.py
```

The exporter exposes metrics at `http://localhost:9100/metrics` and a health endpoint at `http://localhost:9100/health`. It reports database availability, pipeline pause state, order volume, order value, prediction counts, average model confidence, and the age of the latest order.

With Docker Desktop running, start Prometheus and Grafana from a second terminal:

```powershell
docker compose -f monitoring/docker-compose.yml up -d
```

Open Grafana at `http://localhost:3000` and sign in with `admin` / `foodflow-admin`. The `FoodFlow Realtime Monitoring` dashboard and Prometheus datasource are provisioned automatically. Keep the exporter and realtime pipeline running while viewing the dashboard.

## Architecture

Raw customer, restaurant, order, payment, delivery, and review data → cleaning and validation → integrated analytics dataset → Random Forest operational insight → realtime order simulation → SQLite → Streamlit dashboard.

The dashboard presents platform-level metrics such as integrated row counts, source coverage, revenue, customer and restaurant dimensions, data-quality checks, city and cuisine analysis, realtime ingestion, and optional ML insights.

This is a local real-time simulation using Python and SQLite. Kafka, Spark, Docker, PostgreSQL, and Power BI can be added later.

The data is synthetic and the model is for academic demonstration only. The project is designed to demonstrate an end-to-end data engineering workflow; it is not a production food-delivery application.
