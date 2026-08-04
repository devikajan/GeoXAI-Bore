import streamlit as st
from utils.theme import inject_css, hero

st.set_page_config(page_title="About | GeoXAI-Bore", page_icon="ℹ️", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("###  GeoXAI-Bore")
    st.caption("Borewell Failure Intelligence")
    st.markdown("---")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Predict_Failure.py", label="Predict Failure", icon="🔍")
    st.page_link("pages/2_Analytics_Dashboard.py", label="Analytics Dashboard", icon="📊")
    st.page_link("pages/3_Model_Insights.py", label="Model Insights", icon="🧠")
    st.page_link("pages/4_Batch_Prediction.py", label="Batch Prediction", icon="📁")
    st.page_link("pages/5_About.py", label="About & Methodology", icon="ℹ️")

hero(
    "Documentation",
    "About & methodology",
    "How GeoXAI-Bore works, what data it expects, and how to adapt it to real field data.",
)

st.markdown(
    """
#### Purpose

GeoXAI-Bore is a demonstration application for predicting borewell failure risk using
machine learning. It's built to be a starting point that teams managing rural or
agricultural water infrastructure can adapt with their own sensor and maintenance data.

#### Data

The dataset shipped with this app (**4,000 records**) is **synthetically generated** using
domain-informed rules that connect equipment age, usage intensity, soil and rainfall
conditions to a latent failure-risk score, plus random noise. It approximates real-world
patterns but is **not sourced from actual field records**. Before using this for operational
decisions, replace `data/borewell_dataset.csv` with real historical records of borewell
inspections and failures, then re-run `train_model.py`.

#### Features used by the model

| Feature | Description |
|---|---|
| Borewell depth | Total drilled depth in feet |
| Water table depth | Depth to the water table in feet |
| Pump age | Age of the installed pump, years |
| Casing pipe age | Age of the casing pipe, years |
| Daily usage | Average hours of daily operation |
| Soil type | Sandy / Rocky / Clayey / Loamy / Laterite |
| Region type | Coastal / Plateau / Plains / Hilly / Semi-Arid |
| Annual rainfall | Local annual rainfall, mm |
| Maintenance frequency | Service visits per year |
| Motor temperature | Operating motor temperature, °C |
| Vibration level | Pump vibration, mm/s |
| Voltage fluctuation | Power supply instability, % |
| Water yield | Output flow rate, litres per hour |

#### Models

Two Random Forest classifiers are trained on an 80/20 stratified split:
1. A **3-class model** predicting risk category (Low / Medium / High)
2. A **binary model** predicting probability of failure within 6 months, used for the
   probability gauge on the Predict Failure page

See the **Model Insights** page for performance metrics, feature importance, and the
confusion matrix.

#### Adapting this app

- Swap `data/borewell_dataset.csv` for real records with the same column names, or edit
  `train_model.py` to match your schema
- Re-run `python train_model.py` to regenerate `utils/model.pkl` and all metrics
- All pages read from the model bundle in `utils/model.pkl` — no other code changes needed
  if your column names stay the same

#### Tech stack

Streamlit · scikit-learn · pandas · Plotly · joblib
"""
)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
st.caption("Built as a demonstration project. Not for operational or safety-critical use without validation on real data.")
