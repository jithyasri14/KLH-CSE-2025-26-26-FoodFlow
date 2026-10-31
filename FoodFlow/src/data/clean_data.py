from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

for name in ["customers", "restaurants", "orders", "payments", "deliveries", "reviews"]:
    df = pd.read_csv(RAW / f"{name}.csv")
    before = len(df)
    df = df.drop_duplicates().copy()
    # Removes duplicate values

    for column in df.select_dtypes(include="number").columns:
        df[column] = df[column].fillna(df[column].median())

    for column in df.select_dtypes(exclude="number").columns:
        df[column] = df[column].fillna("Unknown")

    if name == "restaurants":
        df = df[df["restaurant_rating"].between(1, 5)]

    if name == "orders":
        df = df[(df["order_value"] > 0) & (df["delivery_distance_km"] > 0)]

    df.to_csv(PROCESSED / f"{name}_cleaned.csv", index=False)
    print(f"{name}: {before} -> {len(df)} rows")

print("Cleaning completed successfully.")
