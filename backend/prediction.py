import pandas as pd

from backend.model import (
    random_forest,
    xgboost_model,
    preprocessor
)

from backend.explain import explain_borewell


def predict_borewell(data):

    # Convert input data into DataFrame
    input_data = pd.DataFrame([data])

    # Apply the same preprocessing used during training
    processed_data = preprocessor.transform(input_data)

    # Random Forest probability
    rf_probability = float(
        random_forest.predict_proba(processed_data)[0][1]
    )

    # XGBoost probability
    xgb_probability = float(
        xgboost_model.predict_proba(processed_data)[0][1]
    )

    # Ensemble probability
    ensemble_probability = float(
        0.5 * rf_probability +
        0.5 * xgb_probability
    )

    # Determine risk category
    if ensemble_probability < 0.33:
        risk_category = "Low"

    elif ensemble_probability < 0.66:
        risk_category = "Medium"

    else:
        risk_category = "High"

    # Get SHAP explanations
    explanations = explain_borewell(data)

    return {
        "random_forest_probability": round(rf_probability, 4),
        "xgboost_probability": round(xgb_probability, 4),
        "ensemble_probability": round(ensemble_probability, 4),
        "risk_category": risk_category,
        "top_features": explanations[:5]
    }