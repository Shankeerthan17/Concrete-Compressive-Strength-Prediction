"""Evaluate every saved frontend model on the same reproducible holdout split."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.app import MODEL_OPTIONS, FEATURE_COLUMNS, _load_trained_model

def evaluate_models():
    data_path = ROOT / "data/processed/concrete_data_cleaned.csv"
    df = pd.read_csv(data_path)
    X = df.loc[:, list(FEATURE_COLUMNS)]
    y = df["compressive_strength"]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    metrics = {}
    for key, (label, filename) in MODEL_OPTIONS.items():
        model = _load_trained_model(key)
        predictions = model.predict(X_test)
        metrics[key] = {"label": label, "MAE": float(mean_absolute_error(y_test, predictions)),
            "RMSE": float(np.sqrt(mean_squared_error(y_test, predictions))),
            "R2": float(r2_score(y_test, predictions)),
            "model_sha256": hashlib.sha256((ROOT / "models/trained" / filename).read_bytes()).hexdigest()}
    result = {"test_rows": len(y_test), "total_rows": len(df), "test_size": 0.2,
              "random_state": 42, "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
              "models": metrics}
    output = ROOT / "reports/evaluation/frontend_metrics.json"
    output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
if __name__ == "__main__": evaluate_models()
