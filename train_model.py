"""
Generates a realistic synthetic borewell dataset and trains a RandomForest
classifier to predict borewell failure risk. Run once to produce:
  - data/borewell_dataset.csv
  - utils/model.pkl
  - utils/feature_importance.csv
  - utils/metrics.json
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve
)
from sklearn.preprocessing import LabelEncoder
import joblib

np.random.seed(42)
N = 4000

soil_types = ["Sandy", "Rocky", "Clayey", "Loamy", "Laterite"]
regions = ["Coastal", "Plateau", "Plains", "Hilly", "Semi-Arid"]

df = pd.DataFrame({
    "Borewell_Depth_ft": np.random.normal(450, 150, N).clip(80, 1200),
    "Water_Table_Depth_ft": np.random.normal(280, 120, N).clip(20, 900),
    "Pump_Age_years": np.random.exponential(4, N).clip(0, 25),
    "Daily_Usage_hours": np.random.normal(7, 3, N).clip(0.5, 20),
    "Soil_Type": np.random.choice(soil_types, N, p=[0.28, 0.22, 0.18, 0.22, 0.10]),
    "Region_Type": np.random.choice(regions, N, p=[0.15, 0.2, 0.3, 0.15, 0.2]),
    "Annual_Rainfall_mm": np.random.normal(900, 350, N).clip(150, 3000),
    "Maintenance_Frequency_per_year": np.random.poisson(1.4, N).clip(0, 6),
    "Motor_Temperature_C": np.random.normal(58, 12, N).clip(30, 110),
    "Vibration_Level_mms": np.random.exponential(2.2, N).clip(0.1, 15),
    "Voltage_Fluctuation_pct": np.random.normal(8, 5, N).clip(0, 35),
    "Water_Yield_LPH": np.random.normal(1200, 500, N).clip(50, 4000),
    "Casing_Pipe_Age_years": np.random.exponential(6, N).clip(0, 30),
})

# Rock-hardness / soil corrosion factor
soil_risk = df["Soil_Type"].map({
    "Sandy": 0.35, "Rocky": 0.10, "Clayey": 0.25, "Loamy": 0.15, "Laterite": 0.30
})
region_risk = df["Region_Type"].map({
    "Coastal": 0.30, "Plateau": 0.10, "Plains": 0.15, "Hilly": 0.20, "Semi-Arid": 0.35
})

# Build a continuous latent risk score from domain-informed weighted rules + noise
risk_score = (
    0.0022 * df["Pump_Age_years"] ** 1.3
    + 0.0009 * df["Casing_Pipe_Age_years"] ** 1.2
    + 0.015 * (df["Daily_Usage_hours"] / 20)
    + 0.02 * np.clip((df["Motor_Temperature_C"] - 55) / 55, 0, None)
    + 0.03 * (df["Vibration_Level_mms"] / 15)
    + 0.02 * (df["Voltage_Fluctuation_pct"] / 35)
    + 0.02 * np.clip((3200 - df["Annual_Rainfall_mm"]) / 3200, 0, None)
    + 0.02 * np.clip((df["Water_Table_Depth_ft"] - 300) / 900, 0, None)
    + 0.015 * np.clip((1200 - df["Water_Yield_LPH"]) / 1200, 0, None)
    - 0.018 * (df["Maintenance_Frequency_per_year"] / 6)
    + 0.10 * soil_risk
    + 0.10 * region_risk
    + np.random.normal(0, 0.05, N)
)

risk_score = (risk_score - risk_score.min()) / (risk_score.max() - risk_score.min())
df["Failure_Risk_Score"] = risk_score

def bucket(s):
    if s < 0.35:
        return "Low"
    elif s < 0.65:
        return "Medium"
    else:
        return "High"

df["Failure_Risk_Category"] = df["Failure_Risk_Score"].apply(bucket)
df["Failure_Within_6Months"] = (df["Failure_Risk_Score"] > 0.55).astype(int)

df.to_csv("data/borewell_dataset.csv", index=False)

# ---------------- Model training ----------------
feature_cols = [
    "Borewell_Depth_ft", "Water_Table_Depth_ft", "Pump_Age_years",
    "Daily_Usage_hours", "Soil_Type", "Region_Type", "Annual_Rainfall_mm",
    "Maintenance_Frequency_per_year", "Motor_Temperature_C",
    "Vibration_Level_mms", "Voltage_Fluctuation_pct", "Water_Yield_LPH",
    "Casing_Pipe_Age_years"
]

X = df[feature_cols].copy()
y_class = df["Failure_Risk_Category"]
y_bin = df["Failure_Within_6Months"]

le_soil = LabelEncoder().fit(X["Soil_Type"])
le_region = LabelEncoder().fit(X["Region_Type"])
X["Soil_Type"] = le_soil.transform(X["Soil_Type"])
X["Region_Type"] = le_region.transform(X["Region_Type"])

le_target = LabelEncoder().fit(y_class)
y_enc = le_target.transform(y_class)

X_train, X_test, y_train, y_test, ybin_train, ybin_test = train_test_split(
    X, y_enc, y_bin, test_size=0.2, random_state=42, stratify=y_enc
)

clf = RandomForestClassifier(
    n_estimators=300, max_depth=12, min_samples_leaf=3,
    random_state=42, class_weight="balanced"
)
clf.fit(X_train, y_train)

bin_clf = RandomForestClassifier(
    n_estimators=300, max_depth=12, min_samples_leaf=3,
    random_state=42, class_weight="balanced"
)
bin_clf.fit(X_train, ybin_train)

y_pred = clf.predict(X_test)
ybin_pred = bin_clf.predict(X_test)
ybin_proba = bin_clf.predict_proba(X_test)[:, 1]

metrics = {
    "multiclass": {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision_macro": round(precision_score(y_test, y_pred, average="macro"), 4),
        "recall_macro": round(recall_score(y_test, y_pred, average="macro"), 4),
        "f1_macro": round(f1_score(y_test, y_pred, average="macro"), 4),
        "classes": list(le_target.classes_),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    },
    "binary": {
        "accuracy": round(accuracy_score(ybin_test, ybin_pred), 4),
        "precision": round(precision_score(ybin_test, ybin_pred), 4),
        "recall": round(recall_score(ybin_test, ybin_pred), 4),
        "f1": round(f1_score(ybin_test, ybin_pred), 4),
        "roc_auc": round(roc_auc_score(ybin_test, ybin_proba), 4),
    },
    "n_train": len(X_train),
    "n_test": len(X_test),
}

fpr, tpr, _ = roc_curve(ybin_test, ybin_proba)
roc_df = pd.DataFrame({"fpr": fpr, "tpr": tpr})
roc_df.to_csv("utils/roc_curve.csv", index=False)

with open("utils/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

fi = pd.DataFrame({
    "Feature": feature_cols,
    "Importance": clf.feature_importances_
}).sort_values("Importance", ascending=False)
fi.to_csv("utils/feature_importance.csv", index=False)

joblib.dump({
    "multiclass_model": clf,
    "binary_model": bin_clf,
    "soil_encoder": le_soil,
    "region_encoder": le_region,
    "target_encoder": le_target,
    "feature_cols": feature_cols,
}, "utils/model.pkl")

print("Training complete.")
print(json.dumps(metrics, indent=2))
