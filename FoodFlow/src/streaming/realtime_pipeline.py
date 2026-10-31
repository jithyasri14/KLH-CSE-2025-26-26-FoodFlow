from pathlib import Path
from datetime import datetime
import random
import sqlite3
import time
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = ROOT / "models" / "foodflow_random_forest.pkl"
DATABASE = ROOT / "data" / "processed" / "foodflow_realtime.db"

bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
FEATURES = bundle["features"]

def create_database():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS realtime_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_timestamp TEXT NOT NULL,
                order_value REAL,
                delivery_distance_km REAL,
                preparation_time_min INTEGER,
                estimated_delivery_time_min INTEGER,
                restaurant_rating REAL,
                customer_age INTEGER,
                prediction TEXT,
                cancelled_probability REAL,
                delayed_probability REAL,
                on_time_probability REAL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_control (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                paused INTEGER NOT NULL DEFAULT 0
            )
        """)
        connection.execute(
            "INSERT OR IGNORE INTO dashboard_control (id, paused) VALUES (1, 0)"
        )

def generate_order():
    return {
        "order_value": round(random.uniform(100, 1200), 2),
        "delivery_distance_km": round(random.uniform(1, 18), 2),
        "preparation_time_min": random.randint(10, 45),
        "estimated_delivery_time_min": random.randint(25, 70),
        "restaurant_rating": round(random.uniform(2.5, 5.0), 1),
        "customer_age": random.randint(18, 65)
    }

def predict_order(order):
    input_df = pd.DataFrame([order], columns=FEATURES)
    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    return {
        "prediction": str(prediction),
        "probabilities": {
            str(category): float(probability)
            for category, probability in zip(model.classes_, probabilities)
        }
    }

def save_order(order, result):
    probabilities = result["probabilities"]
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            INSERT INTO realtime_orders (
                order_timestamp, order_value, delivery_distance_km,
                preparation_time_min, estimated_delivery_time_min,
                restaurant_rating, customer_age, prediction,
                cancelled_probability, delayed_probability, on_time_probability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            order["order_value"],
            order["delivery_distance_km"],
            order["preparation_time_min"],
            order["estimated_delivery_time_min"],
            order["restaurant_rating"],
            order["customer_age"],
            result["prediction"],
            probabilities.get("Cancelled", 0.0),
            probabilities.get("Delayed", 0.0),
            probabilities.get("On-Time", 0.0)
        ))

def main():
    create_database()
    print("FoodFlow real-time pipeline started...")
    print("Predictions are stored in SQLite.")
    print("Press CTRL+C to stop.\n")

    try:
        while True:
            with sqlite3.connect(DATABASE) as connection:
                paused = connection.execute(
                    "SELECT paused FROM dashboard_control WHERE id = 1"
                ).fetchone()[0]
            if paused:
                time.sleep(1)
                continue

            order = generate_order()
            result = predict_order(order)
            save_order(order, result)

            print("New order processed")
            print("Order:", order)
            print("Prediction:", result["prediction"])
            print("Probabilities:", {
                key: f"{value:.2%}"
                for key, value in result["probabilities"].items()
            })
            print("Saved to:", DATABASE)
            print("-" * 70)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nFoodFlow real-time pipeline stopped.")

if __name__ == "__main__":
    main()
