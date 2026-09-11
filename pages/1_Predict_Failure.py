import streamlit as st
import plotly.graph_objects as go

from utils.theme import inject_css, hero, risk_badge, RISK_COLORS, MUTED
from utils.data_helpers import predict_single

st.set_page_config(page_title="Predict Failure | GeoXAI-Bore", page_icon="🔍", layout="wide")
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
    "Single-site assessment",
    "Predict failure risk for a borewell",
    "Enter the borewell's physical, hydrological and equipment details below. "
    "The model returns a risk category, failure probability, and the factors driving the result.",
)

with st.form("predict_form"):
    st.markdown("##### Site & hydrology")
    c1, c2, c3 = st.columns(3)
    depth = c1.number_input("Borewell depth (ft)", 50, 1500, 450, step=10)
    water_table = c2.number_input("Water table depth (ft)", 10, 1000, 280, step=10)
    yield_lph = c3.number_input("Water yield (litres/hour)", 20, 5000, 1200, step=50)

    c4, c5, c6 = st.columns(3)
    soil = c4.selectbox("Soil type", ["Sandy", "Rocky", "Clayey", "Loamy", "Laterite"])
    region = c5.selectbox("Region type", ["Coastal", "Plateau", "Plains", "Hilly", "Semi-Arid"])
    rainfall = c6.number_input("Annual rainfall (mm)", 100, 4000, 900, step=50)

    st.markdown("##### Equipment & usage")
    c7, c8, c9 = st.columns(3)
    pump_age = c7.number_input("Pump age (years)", 0.0, 30.0, 4.0, step=0.5)
    casing_age = c8.number_input("Casing pipe age (years)", 0.0, 40.0, 6.0, step=0.5)
    usage = c9.number_input("Daily usage (hours)", 0.5, 24.0, 7.0, step=0.5)

    c10, c11, c12 = st.columns(3)
    motor_temp = c10.number_input("Motor temperature (°C)", 25, 130, 58, step=1)
    vibration = c11.number_input("Vibration level (mm/s)", 0.0, 20.0, 2.2, step=0.1)
    voltage_fluct = c12.number_input("Voltage fluctuation (%)", 0.0, 40.0, 8.0, step=0.5)

    maintenance = st.slider("Maintenance visits per year", 0, 6, 1)

    submitted = st.form_submit_button("Run prediction", use_container_width=True)

if submitted:
    features = {
        "Borewell_Depth_ft": depth,
        "Water_Table_Depth_ft": water_table,
        "Pump_Age_years": pump_age,
        "Daily_Usage_hours": usage,
        "Soil_Type": soil,
        "Region_Type": region,
        "Annual_Rainfall_mm": rainfall,
        "Maintenance_Frequency_per_year": maintenance,
        "Motor_Temperature_C": motor_temp,
        "Vibration_Level_mms": vibration,
        "Voltage_Fluctuation_pct": voltage_fluct,
        "Water_Yield_LPH": yield_lph,
        "Casing_Pipe_Age_years": casing_age,
    }
    result = predict_single(features)
    category = result["Predicted_Risk_Category"]
    prob = result["Failure_Probability_6mo"]
    color = RISK_COLORS[category]

    st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
    res_col, gauge_col = st.columns([1, 1.1])

    with res_col:
        st.markdown("##### Result")
        st.markdown(risk_badge(category), unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-family:Fraunces,serif; font-size:2.3rem; margin:0.5rem 0;'>"
            f"{prob}% <span style='font-size:1rem; color:{MUTED}; font-family:Inter;'>"
            f"chance of failure within 6 months</span></div>",
            unsafe_allow_html=True,
        )
        classes = ["Low", "Medium", "High"]
        for cls in classes:
            p = result.get(f"Prob_{cls}", 0)
            st.markdown(f"**{cls}**")
            st.progress(min(int(p), 100) / 100)

        st.markdown("<div class='bw-divider'></div>", unsafe_allow_html=True)
        st.markdown("##### Recommended action")
        if category == "High":
            st.error(
                "🔴 Schedule an on-site inspection within 2 weeks. Check pump bearings, "
                "motor cooling, and casing integrity. Consider increasing maintenance frequency."
            )
        elif category == "Medium":
            st.warning(
                "🟠 Add to the next maintenance cycle. Monitor motor temperature and vibration "
                "trends monthly."
            )
        else:
            st.success(
                "🟢 No immediate action required. Continue routine maintenance schedule."
            )

    with gauge_col:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prob,
                number={"suffix": "%", "font": {"size": 40}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color},
                    "steps": [
    {"range": [0, 35], "color": "rgba(42,157,143,0.18)"},
    {"range": [35, 65], "color": "rgba(233,180,76,0.18)"},
    {"range": [65, 100], "color": "rgba(230,57,70,0.18)"},
],
                    "threshold": {
                        "line": {"color": color, "width": 4},
                        "thickness": 0.85,
                        "value": prob,
                    },
                },
                title={"text": "Failure probability"},
            )
        )
        fig.update_layout(height=340, margin=dict(t=50, b=10, l=30, r=30), font_family="Inter")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### What's driving this result")
        drivers = []
        if motor_temp > 75:
            drivers.append("Elevated motor temperature")
        if vibration > 5:
            drivers.append("High vibration levels")
        if pump_age > 10:
            drivers.append("Aging pump unit")
        if casing_age > 15:
            drivers.append("Aging casing pipe")
        if maintenance < 1:
            drivers.append("Low maintenance frequency")
        if voltage_fluct > 15:
            drivers.append("Unstable voltage supply")
        if rainfall < 500:
            drivers.append("Low annual rainfall / aquifer stress")
        if not drivers:
            drivers.append("No dominant risk factor — profile is within normal ranges")
        for d in drivers:
            st.markdown(f"- {d}")
else:
    st.info("Fill in the borewell details above and click **Run prediction** to see the risk assessment.")
