from pathlib import Path
import joblib
import pandas as pd
from flask import Flask, request, jsonify

ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = ROOT / "models" / "foodflow_random_forest.pkl"
bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
FEATURES = bundle["features"]

app = Flask(__name__)

@app.get("/")
def home():
    return jsonify({"message": "FoodFlow Prediction API is running"})

@app.post("/predict")
def predict():
    try:
        payload = request.get_json(force=True)
        missing = [f for f in FEATURES if f not in payload]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        input_df = pd.DataFrame([{f: payload[f] for f in FEATURES}])
        prediction = model.predict(input_df)[0]
        probabilities = model.predict_proba(input_df)[0]

        return jsonify({
            "prediction": str(prediction),
            "probabilities": {
                str(category): round(float(probability), 4)
                for category, probability in zip(model.classes_, probabilities)
            }
        })
    except Exception as error:
        return jsonify({"error": str(error)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
