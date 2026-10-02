# Two assessment options

The React website opens on **New drilling**, followed by **Maintenance**.

## New drilling: location evidence

`GET /drilling/sites` lists 26 reference stations in 20 Andhra Pradesh districts.
The user selects district and mandal/reference station and specifies a water
requirement in litres per hour. No guessed water-table input is required.

`POST /drilling/site-assess` accepts `site_id` and `desired_yield_lph`.
It returns recorded geology, static water level and station discharge; the graph
compares recorded discharge with the user's requirement. These readings apply
to the selected reference station, not to the proposed drilling plot.

The catalogue is transcribed from the repository's `data/raw/geology.csv` APT
section into `data/drilling_reference_sites.json`. Discharge converts from litres
per second to litres per hour by multiplying by 3600. Static water level is metres
below ground; the source header spells it `mgbl`. Dates are not supplied. The
catalogue is not live monitoring, and its provenance/recency needs independent
verification before operational use. Areas outside coverage cannot be assessed.

`success_probability` remains null. There are no verified drilling-success labels
in the repository. Define a usable-yield outcome and collect representative site
records with observed drilling outcomes. Train and evaluate a separate model using
only pre-drilling features. Do not use post-drilling pump telemetry or derive success
labels from `Failure_Within_6Months`.

The legacy `POST /drilling/assess` depth comparison remains for API compatibility.

## Maintenance

`POST /predict` retains the 13-feature Random Forest/XGBoost model, six-month
failure score, SHAP graphs and multilingual explanations. It is a research model
trained on synthetic labels, not a field-validated forecast.
English explanations are immediate and derived from the model output; only
translations invoke Gemini. Changing modes clears the assistant conversation.

## Connection recovery

Health probes validate the JSON status, bypass caches and share in-flight work.
The interface gives cold starts a three-minute recovery window and then continues
retrying even if unavailable. Reconnect and return-to-tab events trigger checks.
Assessments wait for API readiness before submitting; POST requests are not blindly
retried. The free Render instance can still sleep after inactivity. An always-on
hosting plan is needed to remove provider cold starts entirely.
