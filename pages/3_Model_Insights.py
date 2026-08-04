import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.theme import inject_css, hero, metric_card, PRIMARY, ACCENT
from utils.data_helpers import load_metrics, load_feature_importance, load_roc_curve

st.set_page_config(page_title="Model Insights | GeoXAI-Bore", page_icon="🧠", layout="wide")
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
    "Under the hood",
    "Model insights & performance",
    "AquaGuard uses a Random Forest classifier trained on hydrogeological, equipment, and "
    "maintenance features. This page shows how the model performs and what drives its predictions.",
)

metrics = load_metrics()
fi = load_feature_importance()
roc = load_roc_curve()

st.markdown("#### Performance summary (binary failure-within-6-months model)")
c1, c2, c3, c4, c5 = st.columns(5)
metric_card("Accuracy", f"{metrics['binary']['accuracy']*100:.1f}%", c1)
metric_card("Precision", f"{metrics['binary']['precision']*100:.1f}%", c2)
metric_card("Recall", f"{metrics['binary']['recall']*100:.1f}%", c3)
metric_card("F1 score", f"{metrics['binary']['f1']*100:.1f}%", c4)
metric_card("ROC-AUC", f"{metrics['binary']['roc_auc']:.2f}", c5)

st.caption(f"Evaluated on {metrics['n_test']:,} held-out borewells (trained on {metrics['n_train']:,}).")

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown("#### Feature importance")
    fig = px.bar(
        fi.sort_values("Importance"), x="Importance", y="Feature", orientation="h",
        color_discrete_sequence=[PRIMARY],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10), height=420, font_family="Inter",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Shows how much each feature contributes to the Random Forest's split decisions — "
        "higher values mean the model relies on that feature more heavily."
    )

with col2:
    st.markdown("#### ROC curve")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=roc["fpr"], y=roc["tpr"], mode="lines", name="Model",
                               line=dict(color=ACCENT, width=3)))
    fig2.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random baseline",
                               line=dict(color="#999", dash="dash")))
    fig2.update_layout(
        xaxis_title="False positive rate", yaxis_title="True positive rate",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10), height=420, font_family="Inter",
        legend=dict(x=0.55, y=0.08),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Area under curve: **{metrics['binary']['roc_auc']:.2f}** — higher is better (1.0 = perfect).")

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)

st.markdown("#### Confusion matrix — risk category model (Low / Medium / High)")
cm = metrics["multiclass"]["confusion_matrix"]
classes = metrics["multiclass"]["classes"]
cm_df = pd.DataFrame(cm, index=[f"Actual {c}" for c in classes], columns=[f"Predicted {c}" for c in classes])
fig3 = px.imshow(
    cm_df, text_auto=True, color_continuous_scale=[[0, "#F6F4EE"], [1, PRIMARY]],
    aspect="auto",
)
fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380, font_family="Inter")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
st.markdown("#### Model configuration")
st.markdown(
    """
- **Algorithm:** Random Forest Classifier (300 trees, max depth 12, balanced class weights)
- **Two models:** a 3-class risk categorizer (Low / Medium / High) and a binary
  6-month failure predictor used for the probability gauge
- **Split:** 80% train / 20% test, stratified by risk category
- **Features:** borewell depth, water table depth, pump age, casing age, daily usage,
  soil type, region type, annual rainfall, maintenance frequency, motor temperature,
  vibration level, voltage fluctuation, water yield
"""
)
