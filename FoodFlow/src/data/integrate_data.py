from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data" / "processed"

customers = pd.read_csv(P / "customers_cleaned.csv")
restaurants = pd.read_csv(P / "restaurants_cleaned.csv")
orders = pd.read_csv(P / "orders_cleaned.csv")
payments = pd.read_csv(P / "payments_cleaned.csv")
deliveries = pd.read_csv(P / "deliveries_cleaned.csv")
reviews = pd.read_csv(P / "reviews_cleaned.csv")

df = orders.merge(customers, on="customer_id", how="left")
df = df.merge(restaurants, on="restaurant_id", how="left")
df = df.merge(
    payments[["order_id", "payment_id", "payment_status", "payment_amount"]],
    on="order_id",
    how="left",
)
df = df.merge(deliveries, on="order_id", how="left")

review_summary = reviews.groupby("order_id", as_index=False).agg(
    review_count=("review_id", "count"),
    average_review_rating=("review_rating", "mean"),
)
df = df.merge(review_summary, on="order_id", how="left")
df["review_count"] = df["review_count"].fillna(0).astype(int)
df["average_review_rating"] = df["average_review_rating"].fillna(0).round(2)

df["order_date"] = pd.to_datetime(df["order_date"])
df["order_hour"] = df["order_date"].dt.hour
df["order_day"] = df["order_date"].dt.day_name()

def classify(row):
    if row["order_status"] == "Cancelled":
        return "Cancelled"
    if row["actual_delivery_time_min"] <= row["estimated_delivery_time_min"]:
        return "On-Time"
    return "Delayed"

df["order_performance"] = df.apply(classify, axis=1)
df.to_csv(P / "foodflow_integrated.csv", index=False)

print("Integrated dataset saved successfully.")
print(df["order_performance"].value_counts())
