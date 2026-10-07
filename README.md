# Concrete Compressive Strength Predictor

A machine learning project that predicts concrete compressive strength in **megapascals (MPa)** from mix composition and curing age. The project includes exploratory analysis, preprocessing, model training and evaluation, and a Flask web application for comparing six regression models.

Developed for the **IT2011 Artificial Intelligence and Machine Learning** group assignment.

## Features

- Explore feature distributions, correlations and outliers using Jupyter notebooks.
- Clean the dataset by removing missing records, duplicates and IQR outliers.
- Predict strength using six selectable regression models.
- Apply the complete fitted preprocessing pipeline during inference where required.
- Display MAE, RMSE and R² for the selected model.
- Compare all models using scores from the same test observations.
- Validate numeric inputs and reject negative values or non-positive curing age.
- Use a responsive interface with light and dark themes.

## Input Features

| Input | Unit |
| --- | --- |
| Cement | kg/m³ |
| Blast furnace slag | kg/m³ |
| Fly ash | kg/m³ |
| Water | kg/m³ |
| Superplasticizer | kg/m³ |
| Coarse aggregate | kg/m³ |
| Fine aggregate | kg/m³ |
| Curing age | days |

**Target:** Concrete compressive strength, in MPa. The target is not scaled in the Linear Regression pipeline.

## Models

| Model | Implementation |
| --- | --- |
| Linear Regression | VarianceThreshold → StandardScaler → PCA → LinearRegression |
| Decision Tree | DecisionTreeRegressor |
| Random Forest | Existing saved RandomForestRegressor |
| Gradient Boosting | GradientBoostingRegressor |
| XGBoost | XGBRegressor |
| Neural Network | StandardScaler → MLPRegressor |

The Linear Regression pipeline retains at least 95% of explained variance through PCA. Its `fit_intercept` parameter is selected with five-fold cross-validation using `GridSearchCV`.

The existing training notebook contains Random Forest tuning and comparison experiments. The training script reproduces the additional five frontend models and preserves the existing Random Forest artifact.

## Technology Stack

Python, Flask, pandas, NumPy, scikit-learn, XGBoost, joblib, Matplotlib, seaborn, Jupyter, pytest, HTML, CSS and JavaScript.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app.py` | Root entry point for the web application |
| `app/app.py` | Flask routes, model loading and input validation |
| `app/templates/` | Frontend HTML templates |
| `app/static/` | Styles and JavaScript |
| `data/raw/` | Original dataset |
| `data/processed/` | Cleaned and transformed datasets |
| `data/splited/` | Existing saved train/test split files |
| `notebooks/` | EDA, preprocessing, feature engineering and model experiments |
| `notebooks/05_linear_regression.ipynb` | Integrated Linear Regression notebook |
| `models/trained/` | Saved models and fitted pipelines |
| `models/metadata/` | Training metadata and version information |
| `scripts/train_model.py` | Train the additional frontend models |
| `scripts/evaluate_model.py` | Evaluate all saved frontend models |
| `reports/evaluation/frontend_metrics.json` | Common test-split scores used by the frontend |
| `reports/figures/` | Analysis plots |
| `tests/test_app.py` | Prediction, validation and evaluation checks |
| `requirements.txt` | Python dependencies |

Some other directories and scripts are scaffolding for future work; the commands below use the implemented entry points.

## Getting Started

Use **Python 3.11 or 3.12**. Clone or download this repository and open its root folder in VS Code. Run commands from the folder containing `app.py` and `requirements.txt`.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The server continues running until you press `Ctrl+C` in the terminal.

## Using the Application

1. Select a regression model from the dropdown.
2. Enter the seven mix quantities and the curing age.
3. Click **Estimate strength** to obtain a prediction in MPa.
4. Review the selected model's metrics and the comparison table.

Changing the model updates the evaluation metrics immediately. Click **Estimate strength** again to calculate a prediction with the newly selected model. The prediction badge identifies the model used for the displayed result.

## Model Evaluation

The cleaned dataset contains **911 records**. An 80/20 split with `random_state=42` produces **728 training records** and **183 test records**.

The following scores were calculated from the saved models on the same 183 test observations:

| Model | MAE (MPa) ↓ | RMSE (MPa) ↓ | R² ↑ |
| --- | ---: | ---: | ---: |
| Random Forest | 3.06 | 4.20 | 0.9325 |
| Linear Regression (PCA) | 6.01 | 7.73 | 0.7711 |
| Decision Tree | 4.64 | 6.70 | 0.8277 |
| Gradient Boosting | 3.54 | 4.78 | 0.9126 |
| XGBoost | 4.23 | 5.55 | 0.8821 |
| Neural Network | 3.21 | 4.72 | 0.9144 |

- **MAE:** Average absolute prediction error. Lower is better.
- **RMSE:** Error measure that gives larger errors more weight. Lower is better.
- **R²:** Measures how well predictions explain target variation. Higher is better; it is not percentage accuracy.

These metrics describe aggregate dataset performance, not the error of an individual frontend prediction. Earlier JSON reports may describe different training experiments; `frontend_metrics.json` is the source for the current frontend comparison.

### Evaluation Limitations

The existing workflow used this test split during model comparison. It also calculated IQR outlier thresholds across the dataset before splitting, including the target column. These results therefore describe the current cleaned-data experiment, rather than an independent assessment on untouched data. A stronger final evaluation would reserve a separate validation dataset and fit preprocessing decisions using training data only.

## Training and Reproducibility

The application needs the saved files in `models/trained/`. If they are already present, training is not required to launch the frontend.

To reproduce Linear Regression, Decision Tree, Gradient Boosting, XGBoost and Neural Network:

```bash
python scripts/train_model.py
```

The script preserves the existing Random Forest file. To reproduce Random Forest, use the training and export cells in `notebooks/04_model_training.ipynb`.

After retraining or replacing model files, refresh the metrics and restart the application:

```bash
python scripts/evaluate_model.py
python app.py
```

The evaluation JSON records model and dataset hashes to identify the artifacts evaluated.

## Running Tests

```bash
python -m pytest tests/test_app.py -q
```

Checks cover form rendering, feature order, input validation, saved-model predictions, model selection and evaluation values against the saved artifacts.

## Troubleshooting

**Missing Python package:** Install `requirements.txt` using the same Python environment that runs the app. In VS Code, select the corresponding interpreter and notebook kernel.

**Missing seaborn in a notebook:** Run `%pip install seaborn` in a notebook cell, restart the kernel and rerun the cells.

**Missing model file:** Run the training script for the additional models. Obtain or reproduce the Random Forest file separately using its training notebook.

**scikit-learn version warning:** The original Random Forest artifact was saved using scikit-learn 1.9.0, while the packaged requirements use 1.8.0. It produced predictions in the tested environment, but reproducible use should retrain and save that model with the installed version.

**Metrics do not reflect new models:** Run `python scripts/evaluate_model.py` and restart the application.

## Contributing

Create a branch for your changes, run the relevant checks and open a pull request for team review. Keep virtual environments and temporary files out of version control. Follow the team's agreed policy for storing trained model artifacts.

## License

This repository includes an MIT License. See [LICENSE](LICENSE) for the terms and existing attribution.
