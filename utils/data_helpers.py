import json
import os
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_resource
def load_model():
    return joblib.load(os.path.join(BASE_DIR, "utils", "model.pkl"))


@st.cache_data
def load_dataset():
    return pd.read_csv(os.path.join(BASE_DIR, "data", "borewell_dataset.csv"))


@st.cache_data
def load_metrics():
    with open(os.path.join(BASE_DIR, "utils", "metrics.json")) as f:
        return json.load(f)


@st.cache_data
def load_feature_importance():
    return pd.read_csv(os.path.join(BASE_DIR, "utils", "feature_importance.csv"))


@st.cache_data
def load_roc_curve():
    return pd.read_csv(os.path.join(BASE_DIR, "utils", "roc_curve.csv"))


def predict_batch(input_df: pd.DataFrame) -> pd.DataFrame:
    """Takes a dataframe with raw feature columns and returns predictions appended."""
    bundle = load_model()
    clf = bundle["multiclass_model"]
    bin_clf = bundle["binary_model"]
    le_soil = bundle["soil_encoder"]
    le_region = bundle["region_encoder"]
    le_target = bundle["target_encoder"]
    feature_cols = bundle["feature_cols"]

    X = input_df[feature_cols].copy()
    X["Soil_Type"] = le_soil.transform(X["Soil_Type"])
    X["Region_Type"] = le_region.transform(X["Region_Type"])

    class_pred = clf.predict(X)
    class_proba = clf.predict_proba(X)
    bin_proba = bin_clf.predict_proba(X)[:, 1]

    out = input_df.copy()
    out["Predicted_Risk_Category"] = le_target.inverse_transform(class_pred)
    out["Failure_Probability_6mo"] = (bin_proba * 100).round(1)

    for i, cls in enumerate(le_target.classes_):
        out[f"Prob_{cls}"] = (class_proba[:, i] * 100).round(1)

    return out


def predict_single(feature_dict: dict) -> dict:
    df = pd.DataFrame([feature_dict])
    result = predict_batch(df)
    return result.iloc[0].to_dict()
