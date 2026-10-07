import math
import json
from pathlib import Path

import joblib
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

_F32_MAX = float(np.finfo(np.float32).max)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "trained" / "random_forest.pkl"

FEATURES = (
    {"name": "cement", "label": "Cement", "unit": "kg/m³"},
    {"name": "blast_furnace_slag", "label": "Blast furnace slag", "unit": "kg/m³"},
    {"name": "fly_ash", "label": "Fly ash", "unit": "kg/m³"},
    {"name": "water", "label": "Water", "unit": "kg/m³"},
    {"name": "superplasticizer", "label": "Superplasticizer", "unit": "kg/m³"},
    {"name": "coarse_aggregate", "label": "Coarse aggregate", "unit": "kg/m³"},
    {"name": "fine_aggregate", "label": "Fine aggregate", "unit": "kg/m³"},
    {"name": "age", "label": "Curing age", "unit": "days"},
)
FEATURE_COLUMNS = tuple(feature["name"] for feature in FEATURES)


MODEL_OPTIONS = {
    "random_forest": ("Random Forest", "random_forest.pkl"),
    "linear_regression": ("Linear Regression (PCA)", "linear_regression_pca_pipeline.joblib"),
    "decision_tree": ("Decision Tree", "decision_tree.joblib"),
    "gradient_boosting": ("Gradient Boosting", "gradient_boosting.joblib"),
    "xgboost": ("XGBoost", "xgboost.joblib"),
    "neural_network": ("Neural Network", "neural_network.joblib"),
}


def _load_trained_model(model_id="random_forest"):
    MODEL_PATH = PROJECT_ROOT / "models/trained" / MODEL_OPTIONS[model_id][1]
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)


def create_app(model=None):
    app = Flask(__name__)
    app.config["MODEL"] = model
    app.config["MODELS"] = {}
    metrics_path = PROJECT_ROOT / "reports/evaluation/frontend_metrics.json"
    try:
        app.config["EVALUATION"] = json.loads(metrics_path.read_text())
    except (OSError, ValueError):
        app.config["EVALUATION"] = {"models": {}}


    @app.route("/", methods=["GET", "POST"])
    def index():
        values = {}
        errors = {}
        prediction = None
        selected_model = request.form.get("model", "random_forest")
        if selected_model not in MODEL_OPTIONS:
            errors["model"] = "Choose a valid model."
            selected_model = "random_forest"

        if request.method == "POST":
            for feature in FEATURES:
                name = feature["name"]
                raw_value = request.form.get(name, "").strip()
                values[name] = raw_value

                try:
                    value = float(raw_value)
                except ValueError:
                    errors[name] = "Enter a valid number."
                    continue

                if not math.isfinite(value):
                    errors[name] = "Enter a finite number."
                elif value < 0:
                    errors[name] = "Value cannot be negative."
                elif name == "age" and value == 0:
                    errors[name] = "Curing age must be greater than zero."
                else:
                    if value > _F32_MAX:
                        errors[name] = "Value is too large."
                    else:
                        values[name] = value

            if not errors:
                model = app.config.get("MODEL")
                if model is None:
                    try:
                        model = app.config["MODELS"].get(selected_model)
                        if model is None:
                            model = _load_trained_model(selected_model)
                            app.config["MODELS"][selected_model] = model
                    except Exception as exc:
                        for name in FEATURE_COLUMNS:
                            errors[name] = f"Error loading model: {exc}"

                if model is not None:
                    inputs = pd.DataFrame(
                        [[values[name] for name in FEATURE_COLUMNS]],
                        columns=FEATURE_COLUMNS,
                    )
                    try:
                        prediction = float(model.predict(inputs)[0])
                        if not math.isfinite(prediction):
                            raise ValueError("The model returned a non-finite prediction.")
                    except (ValueError, OverflowError) as exc:
                        for name in FEATURE_COLUMNS:
                            errors[name] = str(exc)
                        prediction = None

        model_type = MODEL_OPTIONS[selected_model][0]

        return (
            render_template(
                "index.html",
                features=FEATURES,
                values=values,
                errors=errors,
                prediction=prediction,
                model_type=model_type,
                model_options=MODEL_OPTIONS,
                selected_model=selected_model,
                evaluation=app.config["EVALUATION"],
            ),
            400 if errors else 200,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
