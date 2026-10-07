from app.app import FEATURE_COLUMNS, create_app


class StubModel:
    def __init__(self):
        self.inputs = None

    def predict(self, inputs):
        self.inputs = inputs
        return [42.5]


def valid_form_data():
    return {
        "cement": "350",
        "blast_furnace_slag": "0",
        "fly_ash": "0",
        "water": "180",
        "superplasticizer": "8",
        "coarse_aggregate": "1000",
        "fine_aggregate": "750",
        "age": "28",
    }


def test_home_page_displays_all_model_inputs():
    client = create_app(model=StubModel()).test_client()

    response = client.get("/")

    assert response.status_code == 200
    for feature in FEATURE_COLUMNS:
        assert feature.encode() in response.data


def test_valid_form_predicts_using_model_feature_order():
    model = StubModel()
    client = create_app(model=model).test_client()

    response = client.post("/", data=valid_form_data())

    assert response.status_code == 200
    assert b"42.50 MPa" in response.data
    assert list(model.inputs.columns) == list(FEATURE_COLUMNS)
    assert model.inputs.iloc[0].tolist() == [350, 0, 0, 180, 8, 1000, 750, 28]


def test_invalid_values_are_reported_without_predicting():
    model = StubModel()
    client = create_app(model=model).test_client()
    form_data = valid_form_data()
    form_data["cement"] = "-1"
    form_data["age"] = "0"

    response = client.post("/", data=form_data)

    assert response.status_code == 400
    assert b"Value cannot be negative." in response.data
    assert b"Curing age must be greater than zero." in response.data
    assert model.inputs is None


def test_non_numeric_values_are_reported_without_predicting():
    model = StubModel()
    client = create_app(model=model).test_client()
    form_data = valid_form_data()
    form_data["water"] = "not a number"

    response = client.post("/", data=form_data)

    assert response.status_code == 400
    assert b"Enter a valid number." in response.data
    assert model.inputs is None


def test_default_app_loads_model_and_predicts():
    from app.app import app

    client = app.test_client()
    response = client.post("/", data=valid_form_data())

    assert response.status_code == 200
    assert b"MPa" in response.data



def test_every_saved_model_predicts_and_keeps_selection():
    from app.app import MODEL_OPTIONS
    client = create_app().test_client()
    for key, (label, _) in MODEL_OPTIONS.items():
        response = client.post('/', data={**valid_form_data(), 'model': key})
        assert response.status_code == 200, (key, response.data)
        assert label.encode() in response.data
        assert f'value="{key}" selected'.encode() in response.data
        assert b'prediction-exact-val' in response.data


def test_unknown_model_is_rejected():
    response = create_app().test_client().post('/', data={**valid_form_data(), 'model': '../bad'})
    assert response.status_code == 400
    assert b'Choose a valid model.' in response.data


def test_evaluation_metrics_match_saved_models_on_common_test_split():
    import json
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from app.app import PROJECT_ROOT, MODEL_OPTIONS, _load_trained_model
    evaluation = json.loads((PROJECT_ROOT / 'reports/evaluation/frontend_metrics.json').read_text())
    df = pd.read_csv(PROJECT_ROOT / 'data/processed/concrete_data_cleaned.csv')
    _, X_test, _, y_test = train_test_split(df[list(FEATURE_COLUMNS)], df['compressive_strength'], test_size=.2, random_state=42)
    assert evaluation['test_rows'] == len(y_test)
    client = create_app().test_client()
    for key in MODEL_OPTIONS:
        pred = _load_trained_model(key).predict(X_test)
        scores = evaluation['models'][key]
        assert np.isclose(scores['MAE'], mean_absolute_error(y_test, pred))
        assert np.isclose(scores['RMSE'], np.sqrt(mean_squared_error(y_test, pred)))
        assert np.isclose(scores['R2'], r2_score(y_test, pred))
        response = client.post('/', data={**valid_form_data(), 'model': key})
        assert response.status_code == 200
        assert f'id="metric-mae">{scores["MAE"]:.2f}'.encode() in response.data
        assert f'id="metric-r2">{scores["R2"]:.4f}'.encode() in response.data
    assert b'All models on the same test dataset' in client.get('/').data
