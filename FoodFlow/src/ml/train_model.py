from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "processed" / "foodflow_integrated.csv"
MODEL_FILE = ROOT / "models" / "foodflow_random_forest.pkl"
MODEL_FILE.parent.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE)

FEATURES = [
    "order_value",
    "delivery_distance_km",
    "preparation_time_min",
    "estimated_delivery_time_min",
    "restaurant_rating",
    "customer_age"
]

X = df[FEATURES]
y = df["order_performance"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print(classification_report(y_test, predictions))
print("Confusion matrix:")
print(confusion_matrix(y_test, predictions))

joblib.dump({"model": model, "features": FEATURES}, MODEL_FILE)
print("Model saved to:", MODEL_FILE)
