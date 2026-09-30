# Dataset alignment with the research paper

This note records which repository data matches the GeoXAI-Bore paper and which files currently drive model training.

## Paper dataset found

The paper describes a synthetic dataset with 2,000 borewell observations, 13 model inputs, and the binary target `Failure_Within_6Months`. The repository contains that dataset in two identical files:

- `data/borewell_dataset.csv`
- `data/synthetic/Synthetic_Borewell_Data.csv`

Both files contain 2,000 rows and 18 columns. Their SHA-256 hashes are identical. The columns include:

- `District` and `Borewell_ID`
- The 13 inputs used by the prediction form
- `Failure_Risk_Score`
- `Failure_Risk_Category`
- `Failure_Within_6Months`

The binary target contains 1,110 non-failure observations and 890 failure observations. The stored risk categories contain 394 Low, 998 Medium, and 608 High observations.

The source data used to construct the synthetic dataset is also present under `data/raw`, including groundwater, rainfall, drought, geology, soil, reservoir, and station-location files. The processed integration file is `data/processed/AP_Borewell_Synthetic_Dataset_CLEANED.csv` with 2,000 rows and 65 columns.

## Current training-file difference

`backend/train_model.py` currently reads `dataset/borewell_dataset.csv`. That file contains 4,000 rows and 16 columns, so it is not the same 2,000-row dataset described in the paper. Its target contains 2,862 non-failure and 1,138 failure observations.

The separate root training script also generates 4,000 synthetic rows and writes model metrics with a 3,200/800 train-test split. Those values correspond to the current `utils/metrics.json`, while the paper reports a 1,200/400/400 train-validation-test split from 2,000 observations.

Before reporting the website as a direct reproduction of the paper, choose one canonical dataset and retrain both Random Forest and XGBoost from the paper's documented split and validation procedure. Record the resulting metrics and model hashes so the deployed API can be traced to that experiment.

## Result visualization

The React assessment result now displays:

- A 0-100 six-month failure-risk score
- Low, Medium, and High score ranges
- Random Forest, XGBoost, and ensemble probability bars
- A signed SHAP graph showing which features reduce or increase predicted risk

These graphs visualize the live API response for one borewell. They do not change the model, score thresholds, or underlying prediction.
