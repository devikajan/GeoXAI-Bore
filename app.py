import streamlit as st
import plotly.express as px
import pandas as pd
from utils.theme import inject_css, hero, metric_card, risk_badge, RISK_COLORS, MUTED, BORDER, ACCENT, INK

from utils.data_helpers import load_dataset, load_metrics

st.set_page_config(
    page_title="GeoXAI-Bore | Borewell Failure Prediction",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
df = load_dataset()
metrics = load_metrics()

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
    st.markdown("---")
    st.caption("v1.0 · Demo dataset, synthetically generated for illustration")

hero(
    "Groundwater infrastructure analytics",
    "Predict borewell failure before it happens",
    "AquaGuard combines pump telemetry, hydrogeological data, and maintenance "
    "history to flag borewells at risk of failure — so field teams can act "
    "before water access is disrupted.",
)

c1, c2, c3, c4 = st.columns(4)
metric_card("Borewells monitored", f"{len(df):,}", c1)
high_risk_pct = (df["Failure_Risk_Category"] == "High").mean() * 100
metric_card("High-risk sites", f"{high_risk_pct:.1f}%", c2)
metric_card("Model accuracy", f"{metrics['binary']['accuracy']*100:.1f}%", c3)
metric_card("ROC-AUC score", f"{metrics['binary']['roc_auc']:.2f}", c4)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)

left, right = st.columns([1.3, 1])

with left:
    st.markdown("#### Risk distribution across monitored borewells")
    risk_counts = df["Failure_Risk_Category"].value_counts().reindex(["Low", "Medium", "High"])
    fig = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        color=risk_counts.index,
        color_discrete_map=RISK_COLORS,
        labels={"x": "Risk category", "y": "Number of borewells"},
        text=risk_counts.values,
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
        font_family="Inter",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### Risk by soil type")
    soil_risk = pd.crosstab(df["Soil_Type"], df["Failure_Risk_Category"], normalize="index") * 100
    soil_risk = soil_risk.reindex(columns=["Low", "Medium", "High"])
    fig2 = px.bar(
        soil_risk,
        orientation="h",
        color_discrete_map=RISK_COLORS,
        labels={"value": "Share of borewells (%)", "Soil_Type": ""},
    )
    fig2.update_layout(
        barmode="stack",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=340,
        legend_title_text="",
        font_family="Inter",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)

st.markdown("#### What you can do here")
g1, g2, g3, g4 = st.columns(4)
cards = [
    (g1, "🔍", "Predict Failure", "Enter a single borewell's specs and get an instant risk score with explanations."),
    (g2, "📊", "Analytics Dashboard", "Explore the full monitored fleet — filter by region, soil type, and risk level."),
    (g3, "🧠", "Model Insights", "See which factors drive failure risk and how the model performs."),
    (g4, "📁", "Batch Prediction", "Upload a CSV of multiple borewells and score them all at once."),
]
for col, icon, title, desc in cards:
    col.markdown(
    f"""
    <div class="bw-card" style="min-height:190px; display:flex; flex-direction:column;">
        <div style="width:42px; height:42px; border-radius:11px; background:{ACCENT}17;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.15rem; margin-bottom:0.85rem;">{icon}</div>
        <div style="font-weight:600; font-size:1.02rem; margin-bottom:0.4rem; color:{INK};">{title}</div>
        <div style="color:{MUTED}; font-size:0.87rem; line-height:1.55;">{desc}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
st.caption(
    "⚠️ This application uses a synthetically generated dataset for demonstration purposes. "
    "Replace with real sensor and maintenance records before using for operational decisions."
)
