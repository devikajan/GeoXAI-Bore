import streamlit as st
import plotly.express as px
import pandas as pd

from utils.theme import (
    inject_css,
    hero,
    metric_card,
    RISK_COLORS,
    MUTED,
    BORDER,
    ACCENT,
    INK,
)

from utils.data_helpers import load_dataset, load_metrics


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GeoXAI-Bore | Borewell Failure Prediction",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# LOAD EXISTING PROJECT STYLES
# =========================================================

inject_css()


# =========================================================
# ADDITIONAL PROFESSIONAL DASHBOARD STYLES
# =========================================================

st.markdown(
    """
    <style>

    /* Main content spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(120, 130, 145, 0.15);
    }

    /* Sidebar title */
    .sidebar-brand {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }

    .sidebar-subtitle {
        font-size: 0.78rem;
        color: #6B7280;
        margin-bottom: 1.2rem;
    }

    /* Section headings */
    .section-heading {
        font-size: 1.05rem;
        font-weight: 650;
        letter-spacing: -0.01em;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }

    /* Professional feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(120, 130, 145, 0.18);
        border-radius: 14px;
        padding: 1.25rem;
        min-height: 175px;
        transition: all 0.2s ease;
    }

    .feature-card:hover {
        border-color: rgba(0, 180, 216, 0.45);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }

    .feature-number {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #6B7280;
        margin-bottom: 0.9rem;
    }

    .feature-title {
        font-size: 1rem;
        font-weight: 650;
        color: #172033;
        margin-bottom: 0.55rem;
    }

    .feature-description {
        font-size: 0.84rem;
        line-height: 1.55;
        color: #687386;
    }

    /* Dashboard information strip */
    .info-strip {
        background: rgba(0, 180, 216, 0.06);
        border: 1px solid rgba(0, 180, 216, 0.14);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .info-title {
        font-size: 0.82rem;
        font-weight: 650;
        color: #172033;
        margin-bottom: 0.15rem;
    }

    .info-text {
        font-size: 0.78rem;
        color: #687386;
    }

    /* Chart containers */
    .chart-heading {
        font-size: 0.95rem;
        font-weight: 650;
        color: #172033;
        margin-bottom: 0.2rem;
    }

    /* Footer */
    .dashboard-footer {
        text-align: center;
        color: #7A8494;
        font-size: 0.75rem;
        padding-top: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD PROJECT DATA SAFELY
# =========================================================

try:
    df = load_dataset()
    metrics = load_metrics()

except FileNotFoundError:
    st.error("Required project data files could not be found.")
    st.info(
        "Please make sure the required dataset and model "
        "metrics files are available in the project."
    )
    st.stop()

except Exception as error:
    st.error("An error occurred while loading the project data.")
    st.caption(f"Details: {error}")
    st.stop()


# =========================================================
# DATA VALIDATION
# =========================================================

if not isinstance(df, pd.DataFrame):
    st.error("The project dataset could not be loaded correctly.")
    st.stop()

if df.empty:
    st.warning("The project dataset is empty.")
    st.stop()


required_columns = [
    "Failure_Risk_Category",
    "Soil_Type",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.page_link("pages/6_AI_Assistant.py", label="AI Assistant")


    st.markdown(
        '<div class="sidebar-brand">GeoXAI-Bore</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Borewell Failure Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.page_link(
        "app.py",
        label="Overview",
    )

    st.page_link(
        "pages/1_Predict_Failure.py",
        label="Predict Failure",
    )

    st.page_link(
        "pages/2_Analytics_Dashboard.py",
        label="Analytics Dashboard",
    )

    st.page_link(
        "pages/3_Model_Insights.py",
        label="Model Insights",
    )

    st.page_link(
        "pages/4_Batch_Prediction.py",
        label="Batch Prediction",
    )

    st.page_link(
        "pages/5_About.py",
        label="About & Methodology",
    )

    st.markdown("---")

    st.caption(
        "GeoXAI-Bore · Research Prototype"
    )


# =========================================================
# HERO SECTION
# =========================================================

hero(
    "Groundwater infrastructure analytics",
    "Borewell failure prediction and risk intelligence",
    "GeoXAI-Bore combines borewell characteristics, pump "
    "telemetry, hydrogeological variables and maintenance "
    "information to identify sites associated with elevated "
    "failure risk.",
)


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.markdown(
    """
    <div class="info-strip">
        <div class="info-title">
            Groundwater Risk Intelligence
        </div>
        <div class="info-text">
            Use the dashboard to examine the monitored borewell
            population, understand risk patterns and explore
            model-based failure predictions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# KEY METRICS
# =========================================================

c1, c2, c3, c4 = st.columns(4)


# Borewell count
metric_card(
    "Borewells monitored",
    f"{len(df):,}",
    c1,
)


# Risk categories
risk_categories = (
    df["Failure_Risk_Category"]
    .astype(str)
    .str.strip()
)


high_risk_pct = (
    risk_categories.eq("High").mean() * 100
)


metric_card(
    "High-risk sites",
    f"{high_risk_pct:.1f}%",
    c2,
)


# Model accuracy
try:
    accuracy = float(
        metrics["binary"]["accuracy"]
    )
except (KeyError, TypeError, ValueError):
    accuracy = 0.0


metric_card(
    "Model accuracy",
    f"{accuracy * 100:.1f}%",
    c3,
)


# ROC-AUC
try:
    roc_auc = float(
        metrics["binary"]["roc_auc"]
    )
except (KeyError, TypeError, ValueError):
    roc_auc = 0.0


metric_card(
    "ROC-AUC",
    f"{roc_auc:.2f}",
    c4,
)


# =========================================================
# DIVIDER
# =========================================================

st.markdown(
    "<div class='bw-divider'></div>",
    unsafe_allow_html=True,
)


# =========================================================
# ANALYTICS SECTION
# =========================================================

st.markdown(
    '<div class="section-heading">Risk analytics</div>',
    unsafe_allow_html=True,
)


left, right = st.columns([1.3, 1])


# =========================================================
# RISK DISTRIBUTION
# =========================================================

with left:

    st.markdown(
        '<div class="chart-heading">'
        'Risk distribution across monitored borewells'
        '</div>',
        unsafe_allow_html=True,
    )

    risk_counts = (
        risk_categories
        .value_counts()
        .reindex(
            ["Low", "Medium", "High"],
            fill_value=0,
        )
    )

    fig = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        color=risk_counts.index,
        color_discrete_map=RISK_COLORS,
        labels={
            "x": "Risk category",
            "y": "Number of borewells",
        },
        text=risk_counts.values,
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
    )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            t=20,
            b=10,
            l=10,
            r=10,
        ),
        height=340,
        font_family="Inter",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# =========================================================
# RISK BY SOIL TYPE
# =========================================================

with right:

    st.markdown(
        '<div class="chart-heading">'
        'Risk distribution by soil type'
        '</div>',
        unsafe_allow_html=True,
    )

    soil_risk = (
        pd.crosstab(
            df["Soil_Type"],
            risk_categories,
            normalize="index",
        )
        * 100
    )

    soil_risk = soil_risk.reindex(
        columns=["Low", "Medium", "High"],
        fill_value=0,
    )

    fig2 = px.bar(
        soil_risk,
        orientation="h",
        color_discrete_map=RISK_COLORS,
        labels={
            "value": "Share of borewells (%)",
            "Soil_Type": "",
        },
    )

    fig2.update_layout(
        barmode="stack",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            t=20,
            b=10,
            l=10,
            r=10,
        ),
        height=340,
        legend_title_text="",
        font_family="Inter",
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
    )


# =========================================================
# PLATFORM FEATURES
# =========================================================

st.markdown(
    "<div class='bw-divider'></div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">Platform modules</div>',
    unsafe_allow_html=True,
)


g1, g2, g3, g4 = st.columns(4)


cards = [
    (
        g1,
        "01",
        "Predict Failure",
        "Evaluate an individual borewell and obtain a "
        "model-based failure risk assessment.",
    ),
    (
        g2,
        "02",
        "Analytics Dashboard",
        "Explore borewell patterns across regions, "
        "soil types and risk categories.",
    ),
    (
        g3,
        "03",
        "Model Insights",
        "Examine model performance and the factors "
        "associated with failure risk.",
    ),
    (
        g4,
        "04",
        "Batch Prediction",
        "Process multiple borewells from a CSV file "
        "and generate predictions in one workflow.",
    ),
]


for col, number, title, description in cards:

    card_html = f"""
<div class="feature-card">
    <div class="feature-number">{number}</div>
    <div class="feature-title">{title}</div>
    <div class="feature-description">{description}</div>
</div>
"""

    col.markdown(
        card_html,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    "<div class='bw-divider'></div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-footer">
        GeoXAI-Bore · Explainable borewell failure prediction
        and groundwater risk intelligence
        <br>
        Research prototype using a synthetic demonstration dataset
    </div>
    """,
    unsafe_allow_html=True,
)