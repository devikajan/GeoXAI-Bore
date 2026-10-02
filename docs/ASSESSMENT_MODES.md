# Two assessment options

The React website opens on **New drilling**, followed by **Maintenance**.

## New drilling

`POST /drilling/assess` accepts `planned_depth_ft` and `estimated_water_table_ft`.
It compares depths, displays the margin and a graph, and provides an explanation
with the same language options as maintenance. It does not use the maintenance
models. Passing the check only means the planned depth extends below the estimated
water table; it does not establish a productive aquifer or usable yield.

`success_probability` is deliberately null. The repository has no verified
drilling-success outcome labels. To enable success/failure prediction, define a
usable-yield outcome and collect representative site records with observed drilling
outcomes. Train and evaluate a separate model using only pre-drilling features;
exclude pump age, measured borewell yield and other post-drilling information.
Do not derive success labels from `Failure_Within_6Months`.

## Maintenance

`POST /predict` retains the existing 13-feature Random Forest/XGBoost model,
six-month failure score, SHAP graphs and multilingual explanations. It is a
research model trained on synthetic failure labels, not a field-validated forecast.

Switching options keeps results separate and clears the assistant conversation
so explanations do not carry over between tasks.
