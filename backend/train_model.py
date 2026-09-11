import pandas as pd

# Load dataset
df = pd.read_csv("dataset/borewell_dataset.csv")

# Input features
X = df[
    [
        "Borewell_Depth_ft",
        "Water_Table_Depth_ft",
        "Pump_Age_years",
        "Daily_Usage_hours",
        "Soil_Type",
        "Region_Type",
        "Annual_Rainfall_mm",
        "Maintenance_Frequency_per_year",
        "Motor_Temperature_C",
        "Vibration_Level_mms",
        "Voltage_Fluctuation_pct",
        "Water_Yield_LPH",
        "Casing_Pipe_Age_years"
    ]
]

# Target
y = df["Failure_Within_6Months"]

print("Dataset loaded successfully!")
print("Input shape:", X.shape)
print("Target shape:", y.shape)


# -----------------------------------
# PREPROCESSING
# -----------------------------------

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

# Categorical columns
categorical_columns = [
    "Soil_Type",
    "Region_Type"
]

# Numerical columns
numerical_columns = [
    "Borewell_Depth_ft",
    "Water_Table_Depth_ft",
    "Pump_Age_years",
    "Daily_Usage_hours",
    "Annual_Rainfall_mm",
    "Maintenance_Frequency_per_year",
    "Motor_Temperature_C",
    "Vibration_Level_mms",
    "Voltage_Fluctuation_pct",
    "Water_Yield_LPH",
    "Casing_Pipe_Age_years"
]

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("numerical", "passthrough", numerical_columns)
    ]
)

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)

# Apply preprocessing
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print("Preprocessing completed!")
print("Processed training shape:", X_train_processed.shape)
print("Processed testing shape:", X_test_processed.shape)
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train_processed, y_train)

print("Random Forest training completed!")
from sklearn.metrics import accuracy_score

y_pred = model.predict(X_test_processed)

accuracy = accuracy_score(y_test, y_pred)

print("Random Forest Accuracy:", accuracy)
from xgboost import XGBClassifier

xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)

xgb_model.fit(X_train_processed, y_train)

print("XGBoost training completed!")
y_pred_xgb = xgb_model.predict(X_test_processed)

xgb_accuracy = accuracy_score(y_test, y_pred_xgb)

print("XGBoost Accuracy:", xgb_accuracy)
rf_probability = model.predict_proba(X_test_processed)[:, 1]

xgb_probability = xgb_model.predict_proba(X_test_processed)[:, 1]

ensemble_probability = (
    0.5 * rf_probability +
    0.5 * xgb_probability
)

print("Ensemble prediction completed!")
print("First 5 ensemble probabilities:")
print(ensemble_probability[:5])
def get_risk_category(probability):
    if probability < 0.33:
        return "Low"
    elif probability < 0.66:
        return "Medium"
    else:
        return "High"


print("\nFirst 5 risk predictions:")

for probability in ensemble_probability[:5]:
    risk = get_risk_category(probability)

    print(
        f"Probability: {probability:.2f} "
        f"-> Risk: {risk}"
    )
    from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# Convert ensemble probability into binary prediction
ensemble_pred = (ensemble_probability >= 0.5).astype(int)

accuracy = accuracy_score(y_test, ensemble_pred)
precision = precision_score(y_test, ensemble_pred)
recall = recall_score(y_test, ensemble_pred)
f1 = f1_score(y_test, ensemble_pred)
roc_auc = roc_auc_score(y_test, ensemble_probability)

print("\nEnsemble Model Evaluation")
print("--------------------------")
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)
print("ROC-AUC  :", roc_auc)
import joblib
import os

models_folder = os.path.join(
    os.path.dirname(__file__),
    "models"
)

os.makedirs(models_folder, exist_ok=True)

model_path = os.path.join(
    models_folder,
    "random_forest.pkl"
)

print("Saving Random Forest model...")

joblib.dump(model, model_path)

print("Random Forest model saved!")
print("Location:", model_path)
import joblib

print("Saving model now...")

joblib.dump(model, "backend/models/random_forest.pkl")

print("MODEL SAVED SUCCESSFULLY!")
joblib.dump(xgb_model, "backend/models/xgboost.pkl")

print("XGBoost model saved!")
joblib.dump(xgb_model, "backend/models/xgboost.pkl")

print("XGBoost model saved!")
joblib.dump(model, "backend/models/random_forest.pkl")

print("Random Forest model saved!")

joblib.dump(xgb_model, "backend/models/xgboost.pkl")

print("XGBoost model saved!")
joblib.dump(preprocessor, "backend/models/preprocessor.pkl")

print("Preprocessor saved!")
