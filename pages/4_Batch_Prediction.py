import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import inject_css, hero, metric_card, RISK_COLORS
from utils.data_helpers import predict_batch, load_dataset

st.set_page_config(page_title="Batch Prediction | GeoXAI-Bore", page_icon="📁", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("### GeoXAI-Bore")
    st.caption("Borewell Failure Intelligence")
    st.markdown("---")
    st.page_link("app.py", label="Overview", icon="🏠")
    st.page_link("pages/1_Predict_Failure.py", label="Predict Failure", icon="🔍")
    st.page_link("pages/2_Analytics_Dashboard.py", label="Analytics Dashboard", icon="📊")
    st.page_link("pages/3_Model_Insights.py", label="Model Insights", icon="🧠")
    st.page_link("pages/4_Batch_Prediction.py", label="Batch Prediction", icon="📁")
    st.page_link("pages/5_About.py", label="About & Methodology", icon="ℹ️")

hero(
    "Score many sites at once",
    "Batch prediction from CSV",
    "Upload a CSV with one row per borewell to score the whole batch in one go. "
    "Need the right format? Download the template below.",
)

required_cols = [
    "Borewell_Depth_ft", "Water_Table_Depth_ft", "Pump_Age_years", "Daily_Usage_hours",
    "Soil_Type", "Region_Type", "Annual_Rainfall_mm", "Maintenance_Frequency_per_year",
    "Motor_Temperature_C", "Vibration_Level_mms", "Voltage_Fluctuation_pct",
    "Water_Yield_LPH", "Casing_Pipe_Age_years",
]

c1, c2 = st.columns([2, 1])
with c1:
    uploaded = st.file_uploader("Upload borewell CSV", type=["csv"])
with c2:
    st.write("")
    st.write("")
    template = load_dataset()[required_cols].head(5)
    st.download_button(
        "Download CSV template",
        template.to_csv(index=False).encode("utf-8"),
        file_name="borewell_template.csv",
        mime="text/csv",
        use_container_width=True,
    )

if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Couldn't read that file: {e}")
        st.stop()

    missing = [c for c in required_cols if c not in raw.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.stop()

    valid_soils = {"Sandy", "Rocky", "Clayey", "Loamy", "Laterite"}
    valid_regions = {"Coastal", "Plateau", "Plains", "Hilly", "Semi-Arid"}
    bad_soil = set(raw["Soil_Type"].unique()) - valid_soils
    bad_region = set(raw["Region_Type"].unique()) - valid_regions
    if bad_soil:
        st.error(f"Unrecognized Soil_Type values: {bad_soil}. Must be one of {valid_soils}.")
        st.stop()
    if bad_region:
        st.error(f"Unrecognized Region_Type values: {bad_region}. Must be one of {valid_regions}.")
        st.stop()

    with st.spinner("Scoring borewells..."):
        results = predict_batch(raw)

    st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    metric_card("Rows scored", f"{len(results):,}", m1)
    metric_card("High risk", f"{(results['Predicted_Risk_Category']=='High').sum():,}", m2)
    metric_card("Medium risk", f"{(results['Predicted_Risk_Category']=='Medium').sum():,}", m3)
    metric_card("Low risk", f"{(results['Predicted_Risk_Category']=='Low').sum():,}", m4)

    st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
    rc1, rc2 = st.columns([1, 1.4])
    with rc1:
        st.markdown("#### Risk breakdown")
        counts = results["Predicted_Risk_Category"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
        fig = px.pie(
            values=counts.values, names=counts.index, color=counts.index,
            color_discrete_map=RISK_COLORS, hole=0.5,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, font_family="Inter")
        st.plotly_chart(fig, use_container_width=True)

    with rc2:
        st.markdown("#### Scored results")
        st.dataframe(
            results.sort_values("Failure_Probability_6mo", ascending=False),
            use_container_width=True, height=320,
        )

    st.download_button(
        "Download scored results as CSV",
        results.to_csv(index=False).encode("utf-8"),
        file_name="borewell_predictions.csv",
        mime="text/csv",
    )
else:
    st.info("Upload a CSV file to get started, or download the template to see the expected format.")
    st.markdown("##### Required columns")
    st.code(", ".join(required_cols), language="text")
