import streamlit as st
import plotly.express as px

from utils.theme import inject_css, hero, metric_card, RISK_COLORS
from utils.data_helpers import load_dataset

st.set_page_config(page_title="Analytics Dashboard | GeoXAI-Bore", page_icon="📊", layout="wide")
inject_css()
df = load_dataset()

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
    st.markdown("##### Filters")
    regions = st.multiselect("Region type", sorted(df["Region_Type"].unique()), default=list(df["Region_Type"].unique()))
    soils = st.multiselect("Soil type", sorted(df["Soil_Type"].unique()), default=list(df["Soil_Type"].unique()))
    risk_levels = st.multiselect("Risk category", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])

fdf = df[
    df["Region_Type"].isin(regions)
    & df["Soil_Type"].isin(soils)
    & df["Failure_Risk_Category"].isin(risk_levels)
]

hero(
    "Fleet-wide monitoring",
    "Analytics dashboard",
    "Explore the monitored borewell fleet. Use the filters in the sidebar to narrow down by "
    "region, soil type, or risk category.",
)

c1, c2, c3, c4 = st.columns(4)
metric_card("Filtered borewells", f"{len(fdf):,}", c1)
metric_card("Avg. pump age", f"{fdf['Pump_Age_years'].mean():.1f} yrs" if len(fdf) else "—", c2)
metric_card("Avg. water yield", f"{fdf['Water_Yield_LPH'].mean():,.0f} LPH" if len(fdf) else "—", c3)
metric_card("High-risk share", f"{(fdf['Failure_Risk_Category']=='High').mean()*100:.1f}%" if len(fdf) else "—", c4)

st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)

if fdf.empty:
    st.warning("No borewells match the current filters. Adjust the sidebar filters.")
else:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("#### Risk by region")
        crosstab = fdf.groupby(["Region_Type", "Failure_Risk_Category"]).size().reset_index(name="count")
        fig = px.bar(
            crosstab, x="Region_Type", y="count", color="Failure_Risk_Category",
            color_discrete_map=RISK_COLORS, labels={"Region_Type": "Region", "count": "Borewells"},
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10, b=10, l=10, r=10), height=340, legend_title_text="", font_family="Inter")
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.markdown("#### Pump age vs. failure probability")
        fig2 = px.scatter(
            fdf, x="Pump_Age_years", y="Failure_Risk_Score", color="Failure_Risk_Category",
            color_discrete_map=RISK_COLORS, opacity=0.6,
            labels={"Pump_Age_years": "Pump age (years)", "Failure_Risk_Score": "Failure risk score"},
        )
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=10, l=10, r=10), height=340, legend_title_text="", font_family="Inter")
        st.plotly_chart(fig2, use_container_width=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("#### Motor temperature distribution")
        fig3 = px.histogram(
            fdf, x="Motor_Temperature_C", color="Failure_Risk_Category",
            color_discrete_map=RISK_COLORS, nbins=30, barmode="overlay", opacity=0.7,
            labels={"Motor_Temperature_C": "Motor temperature (°C)"},
        )
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=10, l=10, r=10), height=320, legend_title_text="", font_family="Inter")
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        st.markdown("#### Rainfall vs. water yield")
        fig4 = px.scatter(
            fdf, x="Annual_Rainfall_mm", y="Water_Yield_LPH", color="Failure_Risk_Category",
            color_discrete_map=RISK_COLORS, opacity=0.6,
            labels={"Annual_Rainfall_mm": "Annual rainfall (mm)", "Water_Yield_LPH": "Water yield (LPH)"},
        )
        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=10, l=10, r=10), height=320, legend_title_text="", font_family="Inter")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
    st.markdown("#### Raw data")
    st.dataframe(fdf, use_container_width=True, height=320)
    st.download_button(
        "Download filtered data as CSV",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="filtered_borewells.csv",
        mime="text/csv",
    )
