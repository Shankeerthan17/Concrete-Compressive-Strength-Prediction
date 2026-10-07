"""Train missing frontend models; preserve the supplied Random Forest artifact."""
from pathlib import Path
import sys, json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
def train_models():
    df = pd.read_csv(ROOT / "data/processed/concrete_data_cleaned.csv")
    X = df.drop(columns="compressive_strength")
    y = df["compressive_strength"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    linear = Pipeline([("selection", VarianceThreshold(0.01)), ("scaler", StandardScaler()),
                       ("pca", PCA(n_components=0.95)), ("model", LinearRegression())])
    search = GridSearchCV(linear, {"model__fit_intercept": [True, False]},
                          cv=KFold(5, shuffle=True, random_state=42), scoring="neg_mean_squared_error")
    search.fit(X_train, y_train)
    models = {
        "linear_regression_pca_pipeline": search.best_estimator_,
        "decision_tree": DecisionTreeRegressor(random_state=42),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
        "xgboost": XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42, n_jobs=2),
        "neural_network": Pipeline([("scaler", StandardScaler()), ("model", MLPRegressor(
            hidden_layer_sizes=(100, 50), activation="relu", solver="adam", max_iter=3000, random_state=42))]),
    }
    versions = {}
    import sklearn, xgboost
    versions.update(sklearn=sklearn.__version__, xgboost=xgboost.__version__)
    metrics = {}
    for name, model in models.items():
        if name != "linear_regression_pca_pipeline": model.fit(X_train, y_train)
        joblib.dump(model, ROOT / "models/trained" / (name + ".joblib"), compress=3)
        pred = model.predict(X_test)
        metrics[name] = {"MAE": float(mean_absolute_error(y_test, pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_test, pred))), "R2": float(r2_score(y_test, pred))}
        print(name, metrics[name], flush=True)
    details = {"feature_columns": X.columns.tolist(), "train_rows": len(X_train), "test_rows": len(X_test),
               "linear_best_parameters": search.best_params_, "versions": versions, "test_metrics": metrics,
               "note": "Other models newly trained; original Random Forest preserved. Neural Network uses a fitted StandardScaler pipeline."}
    (ROOT / "models/metadata/frontend_models.json").write_text(json.dumps(details, indent=2))
if __name__ == "__main__": train_models()
