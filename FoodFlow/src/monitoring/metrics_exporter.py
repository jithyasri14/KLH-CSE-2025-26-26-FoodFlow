from datetime import datetime
from pathlib import Path
import sqlite3
import time

from flask import Flask, Response, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "data" / "processed" / "foodflow_realtime.db"

app = Flask(__name__)

DB_AVAILABLE = Gauge("foodflow_realtime_database_available", "Whether the realtime SQLite database is available")
PIPELINE_PAUSED = Gauge("foodflow_pipeline_paused", "Whether realtime ingestion is paused")
ORDERS_TOTAL = Gauge("foodflow_realtime_orders_total", "Total realtime orders currently stored")
ORDERS_BY_PREDICTION = Gauge(
    "foodflow_realtime_orders_by_prediction",
    "Realtime orders by model prediction",
    ["prediction"],
)
ORDER_VALUE_TOTAL = Gauge("foodflow_realtime_order_value_total", "Total value of stored realtime orders")
AVERAGE_CONFIDENCE = Gauge(
    "foodflow_model_average_confidence",
    "Average prediction probability by class",
    ["prediction"],
)
LAST_ORDER_AGE_SECONDS = Gauge(
    "foodflow_last_order_age_seconds",
    "Age in seconds of the newest realtime order",
)

PREDICTIONS = ("Cancelled", "Delayed", "On-Time")


def clear_metrics():
    DB_AVAILABLE.set(0)
    PIPELINE_PAUSED.set(0)
    ORDERS_TOTAL.set(0)
    ORDER_VALUE_TOTAL.set(0)
    LAST_ORDER_AGE_SECONDS.set(0)
    for prediction in PREDICTIONS:
        ORDERS_BY_PREDICTION.labels(prediction=prediction).set(0)
        AVERAGE_CONFIDENCE.labels(prediction=prediction).set(0)


def collect_database_metrics():
    clear_metrics()
    if not DATABASE.exists():
        return False

    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.row_factory = sqlite3.Row
            order_summary = connection.execute(
                """
                SELECT COUNT(*) AS total_orders,
                       COALESCE(SUM(order_value), 0) AS total_value,
                       MAX(order_timestamp) AS latest_order,
                       AVG(cancelled_probability) AS cancelled_confidence,
                       AVG(delayed_probability) AS delayed_confidence,
                       AVG(on_time_probability) AS on_time_confidence
                FROM realtime_orders
                """
            ).fetchone()
            prediction_rows = connection.execute(
                "SELECT prediction, COUNT(*) AS count FROM realtime_orders GROUP BY prediction"
            ).fetchall()
            paused = connection.execute(
                "SELECT paused FROM dashboard_control WHERE id = 1"
            ).fetchone()

        DB_AVAILABLE.set(1)
        PIPELINE_PAUSED.set(int(paused[0]) if paused else 0)
        ORDERS_TOTAL.set(order_summary["total_orders"] or 0)
        ORDER_VALUE_TOTAL.set(order_summary["total_value"] or 0)
        confidence_values = {
            "Cancelled": order_summary["cancelled_confidence"],
            "Delayed": order_summary["delayed_confidence"],
            "On-Time": order_summary["on_time_confidence"],
        }
        for prediction, count in prediction_rows:
            ORDERS_BY_PREDICTION.labels(prediction=prediction).set(count)
        for prediction, confidence in confidence_values.items():
            AVERAGE_CONFIDENCE.labels(prediction=prediction).set(confidence or 0)

        if order_summary["latest_order"]:
            latest = datetime.fromisoformat(order_summary["latest_order"])
            LAST_ORDER_AGE_SECONDS.set(max(0, time.time() - latest.timestamp()))
        return True
    except (OSError, sqlite3.Error, ValueError):
        clear_metrics()
        return False


@app.get("/metrics")
def metrics():
    collect_database_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    available = collect_database_metrics()
    return jsonify({"status": "ok" if available else "waiting", "database": str(DATABASE)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100, debug=False)
