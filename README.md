# 💧 AquaGuard — Borewell Failure Prediction

A professional, multi-page Streamlit application for predicting borewell
(bore-well pump) failure risk from hydrogeological, equipment, and
maintenance data.

## Pages

- **Overview** — fleet-wide KPIs and risk snapshot
- **Predict Failure** — single-site form with risk gauge and driver explanation
- **Analytics Dashboard** — filterable charts across the monitored fleet
- **Model Insights** — feature importance, ROC curve, confusion matrix, metrics
- **Batch Prediction** — upload a CSV and score many borewells at once
- **About & Methodology** — data, model, and adaptation notes

## Setup

```bash
pip install -r requirements.txt
python train_model.py     # generates data + trains the model (already done once)
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Project structure

```
app.py                          # Home page
pages/
  1_Predict_Failure.py
  2_Analytics_Dashboard.py
  3_Model_Insights.py
  4_Batch_Prediction.py
  5_About.py
utils/
  theme.py                      # shared CSS / design tokens
  data_helpers.py                # model + data loading, prediction functions
  model.pkl                      # trained model bundle
  metrics.json                   # evaluation metrics
  feature_importance.csv
  roc_curve.csv
data/
  borewell_dataset.csv           # synthetic training dataset (4,000 rows)
train_model.py                   # regenerate data + retrain model
.streamlit/config.toml           # theme configuration
```

## Using your own data

Replace `data/borewell_dataset.csv` with real records using the same column
names (see the About page in-app for the full schema), then run
`python train_model.py` again to retrain and refresh all metrics.

## Note

The bundled dataset is **synthetically generated** for demonstration. Validate
against real historical failure records before using this for operational
decisions.
