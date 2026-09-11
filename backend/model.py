import joblib
import os

# Get the folder where this file is located
BASE_DIR = os.path.dirname(__file__)

# Model paths
RF_PATH = os.path.join(BASE_DIR, "models", "random_forest.pkl")
XGB_PATH = os.path.join(BASE_DIR, "models", "xgboost.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")

# Load models
random_forest = joblib.load(RF_PATH)
xgboost_model = joblib.load(XGB_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

print("Random Forest loaded!")
print("XGBoost loaded!")
print("Preprocessor loaded!")