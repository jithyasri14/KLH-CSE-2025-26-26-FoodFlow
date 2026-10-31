from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

customers = pd.DataFrame({
    "customer_id": [f"C{i:04d}" for i in range(1, 501)],
    "customer_name": [f"Customer_{i}" for i in range(1, 501)],
    "customer_city": rng.choice(["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Delhi"], 500),
    "customer_age": rng.integers(18, 65, 500)
})
customers.to_csv(RAW / "customers.csv", index=False)

restaurants = pd.DataFrame({
    "restaurant_id": [f"R{i:03d}" for i in range(1, 51)],
    "restaurant_name": [f"Restaurant_{i}" for i in range(1, 51)],
    "restaurant_city": rng.choice(["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Delhi"], 50),
    "restaurant_rating": np.round(rng.uniform(2.5, 5.0, 50), 1),
    "cuisine": rng.choice(["Indian", "Chinese", "Italian", "Mexican", "Fast Food"], 50)
})
restaurants.to_csv(RAW / "restaurants.csv", index=False)

n = 5000
order_ids = [f"O{i:05d}" for i in range(1, n + 1)]
distances = np.round(rng.uniform(1, 18, n), 2)
prep = rng.integers(10, 46, n)
estimated = rng.integers(25, 70, n)

risk_score = 0.04 * distances + 0.035 * prep - 0.025 * estimated + rng.normal(0, 0.8, n)
cancelled = risk_score > np.percentile(risk_score, 86)

actual_delivery = np.maximum(
    10,
    estimated + distances * 1.3 + prep * 0.45 + rng.normal(0, 7, n)
)
actual_delivery = np.round(actual_delivery).astype(int)
order_status = np.where(cancelled, "Cancelled", "Completed")

# Keep a representative, learnable on-time segment so the platform can compare
# outcomes using the same operational features available to the model.
on_time_mask = (
    (~cancelled)
    & (distances <= np.percentile(distances, 45))
    & (prep <= np.percentile(prep, 55))
    & (estimated >= np.percentile(estimated, 45))
    & (rng.random(n) < 0.72)
)
on_time_delivery = estimated[on_time_mask] - rng.integers(
    0, 8, on_time_mask.sum()
)
actual_delivery[on_time_mask] = np.maximum(10, on_time_delivery)

orders = pd.DataFrame({
    "order_id": order_ids,
    "customer_id": rng.choice(customers["customer_id"], n),
    "restaurant_id": rng.choice(restaurants["restaurant_id"], n),
    "order_value": np.round(rng.uniform(100, 1200, n), 2),
    "delivery_distance_km": distances,
    "preparation_time_min": prep,
    "estimated_delivery_time_min": estimated,
    "payment_method": rng.choice(["UPI", "Card", "Cash", "Wallet"], n),
    "order_status": order_status,
    "order_date": pd.date_range("2026-01-01", periods=n, freq="30min")
})
orders.to_csv(RAW / "orders.csv", index=False)

payments = pd.DataFrame({
    "payment_id": [f"P{i:05d}" for i in range(1, n + 1)],
    "order_id": order_ids,
    "payment_method": orders["payment_method"],
    "payment_amount": orders["order_value"],
    "payment_status": np.where(order_status == "Cancelled", "Refunded", "Successful")
})
payments.to_csv(RAW / "payments.csv", index=False)

deliveries = pd.DataFrame({
    "delivery_id": [f"D{i:05d}" for i in range(1, n + 1)],
    "order_id": order_ids,
    "delivery_partner_id": [f"DP{int(x):04d}" for x in rng.integers(1, 301, n)],
    "actual_delivery_time_min": actual_delivery,
    "delivery_status": np.where(order_status == "Cancelled", "Not Delivered", "Delivered")
})
deliveries.to_csv(RAW / "deliveries.csv", index=False)

reviews = pd.DataFrame({
    "review_id": [f"RV{i:05d}" for i in range(1, 3001)],
    "order_id": rng.choice(order_ids, 3000),
    "customer_id": rng.choice(customers["customer_id"], 3000),
    "review_rating": rng.integers(1, 6, 3000),
    "review_text": rng.choice(
        ["Great service", "Late delivery", "Tasty food", "Average experience", "Excellent"],
        3000
    )
})
reviews.to_csv(RAW / "reviews.csv", index=False)

print("Raw datasets generated successfully.")
