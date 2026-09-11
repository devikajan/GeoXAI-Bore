import shap
import pandas as pd

from backend.model import (
    random_forest,
    preprocessor
)


def explain_borewell(data):

    # Convert input into DataFrame
    input_data = pd.DataFrame([data])

    # Apply the same preprocessing used during training
    processed_data = preprocessor.transform(input_data)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(random_forest)

    # Calculate SHAP values
    shap_values = explainer.shap_values(processed_data)

    # Get feature names after preprocessing
    feature_names = preprocessor.get_feature_names_out()

    # SHAP values for failure class (class 1)
    values = shap_values[0][:, 1]

    explanations = []

    for feature, value in zip(feature_names, values):

        # Remove preprocessing prefixes
        clean_feature = feature.replace("numerical__", "")
        clean_feature = clean_feature.replace("categorical__", "")

        # Ignore one-hot category features
        # We will handle them using the original input values
        if clean_feature.startswith("Region_Type_"):
            continue

        if clean_feature.startswith("Soil_Type_"):
            continue

        # Convert feature names to readable names
        name_map = {
            "Borewell_Depth_ft": "Borewell Depth",
            "Water_Table_Depth_ft": "Water Table Depth",
            "Pump_Age_years": "Pump Age",
            "Daily_Usage_hours": "Daily Usage",
            "Annual_Rainfall_mm": "Annual Rainfall",
            "Maintenance_Frequency_per_year": "Maintenance Frequency",
            "Motor_Temperature_C": "Motor Temperature",
            "Vibration_Level_mms": "Vibration Level",
            "Voltage_Fluctuation_pct": "Voltage Fluctuation",
            "Water_Yield_LPH": "Water Yield",
            "Casing_Pipe_Age_years": "Casing Pipe Age"
        }

        clean_name = name_map.get(clean_feature, clean_feature)

        if value > 0:
            impact = "increases failure risk"
        elif value < 0:
            impact = "decreases failure risk"
        else:
            impact = "no significant impact"

        explanations.append({
            "feature": clean_name,
            "shap_value": round(float(value), 4),
            "impact": impact
        })

    # Sort by strongest influence
    explanations.sort(
        key=lambda x: abs(x["shap_value"]),
        reverse=True
    )

    return explanations