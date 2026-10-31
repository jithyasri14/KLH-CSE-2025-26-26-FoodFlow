from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
REPORT_FILE = PROCESSED / "data_quality_report.json"

SOURCE_KEYS = {
    "customers": "customer_id",
    "restaurants": "restaurant_id",
    "orders": "order_id",
    "payments": "payment_id",
    "deliveries": "delivery_id",
    "reviews": "review_id",
}


def check_source(name, key):
    frame = pd.read_csv(PROCESSED / f"{name}_cleaned.csv")
    duplicate_keys = int(frame[key].duplicated().sum())
    missing_values = int(frame.isna().sum().sum())
    return {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "duplicate_keys": duplicate_keys,
        "missing_values": missing_values,
        "passed": duplicate_keys == 0 and missing_values == 0,
    }


def main():
    report = {"sources": {}, "relationships": {}, "integrated": {}, "passed": True}

    for name, key in SOURCE_KEYS.items():
        report["sources"][name] = check_source(name, key)

    customers = pd.read_csv(PROCESSED / "customers_cleaned.csv")
    restaurants = pd.read_csv(PROCESSED / "restaurants_cleaned.csv")
    orders = pd.read_csv(PROCESSED / "orders_cleaned.csv")
    payments = pd.read_csv(PROCESSED / "payments_cleaned.csv")
    deliveries = pd.read_csv(PROCESSED / "deliveries_cleaned.csv")
    reviews = pd.read_csv(PROCESSED / "reviews_cleaned.csv")
    integrated = pd.read_csv(PROCESSED / "foodflow_integrated.csv")

    report["relationships"] = {
        "orders_missing_customers": int((~orders["customer_id"].isin(customers["customer_id"])).sum()),
        "orders_missing_restaurants": int((~orders["restaurant_id"].isin(restaurants["restaurant_id"])).sum()),
        "payments_missing_orders": int((~payments["order_id"].isin(orders["order_id"])).sum()),
        "deliveries_missing_orders": int((~deliveries["order_id"].isin(orders["order_id"])).sum()),
        "reviews_missing_orders": int((~reviews["order_id"].isin(orders["order_id"])).sum()),
    }

    outcome_counts = integrated["order_performance"].value_counts().to_dict()
    report["integrated"] = {
        "rows": int(len(integrated)),
        "unique_orders": int(integrated["order_id"].nunique()),
        "missing_values": int(integrated.isna().sum().sum()),
        "outcome_counts": {str(key): int(value) for key, value in outcome_counts.items()},
    }

    source_failed = any(not result["passed"] for result in report["sources"].values())
    relationship_failed = any(value != 0 for value in report["relationships"].values())
    integrated_failed = (
        report["integrated"]["rows"] != report["integrated"]["unique_orders"]
        or report["integrated"]["missing_values"] != 0
    )
    report["passed"] = not (source_failed or relationship_failed or integrated_failed)

    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Data quality report saved to: {REPORT_FILE}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
