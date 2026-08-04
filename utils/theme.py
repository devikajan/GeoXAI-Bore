"""Shared visual identity for the Borewell Failure Prediction app — water theme."""

import streamlit as st

# ---- Water-inspired palette ----
PRIMARY = "#0E4C6B"        # deep water blue
PRIMARY_LIGHT = "#1E88A8"  # mid-depth teal-blue
ACCENT = "#00B4D8"         # aqua / surface water
ACCENT_LIGHT = "#48CAE4"   # light aqua ripple
SUCCESS = "#2A9D8F"        # clear-water teal
WARNING = "#E9B44C"        # silty amber
DANGER = "#E63946"         # alert coral-red
BG = "#EAF6F8"             # misty pale blue background
SURFACE = "#FFFFFF"
INK = "#082032"            # deep ink navy
MUTED = "#5A7A8C"           # muted slate blue
BORDER = "#D3E9EF"

RISK_COLORS = {"Low": SUCCESS, "Medium": WARNING, "High": DANGER}


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        .stApp {{
            background: {BG};
            background-image:
                radial-gradient(circle at 15% 0%, {ACCENT_LIGHT}22 0%, transparent 40%),
                radial-gradient(circle at 90% 10%, {PRIMARY_LIGHT}1a 0%, transparent 35%);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {PRIMARY} 0%, #0A3A52 100%);
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] * {{
            color: #E7F6FA !important;
        }}
        section[data-testid="stSidebar"] .stRadio label:hover {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: rgba(231,246,250,0.18);
        }}

        h1, h2, h3, h4 {{
            font-family: 'Public Sans', sans-serif !important;
            color: {INK} !important;
            letter-spacing: -0.01em;
        }}

        .bw-eyebrow {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {ACCENT_LIGHT};
            font-weight: 500;
        }}

        .bw-hero {{
            padding: 2.3rem 2.4rem;
            background: linear-gradient(120deg, {PRIMARY} 0%, {PRIMARY_LIGHT} 55%, {ACCENT} 130%);
            border-radius: 20px;
            color: #F0FBFD;
            margin-bottom: 1.6rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 12px 32px -12px {PRIMARY}55;
        }}
        .bw-hero::after {{
            content: "";
            position: absolute;
            right: -60px;
            bottom: -80px;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            background: radial-gradient(circle, {ACCENT_LIGHT}33 0%, transparent 70%);
        }}
        .bw-hero h1 {{
            color: #FBFEFF !important;
            font-weight: 700;
            font-size: 2.15rem;
            margin: 0.25rem 0 0.5rem 0;
        }}
        .bw-hero p {{
            color: #D9F1F6;
            font-size: 1.01rem;
            max-width: 640px;
            margin: 0;
            position: relative;
        }}
        .bw-hero .bw-eyebrow {{ color: #A9E8F5; position: relative; }}

        .bw-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    line-height: 1.5;
    transition: box-shadow 0.15s, transform 0.15s;
}}
        .bw-card:hover {{
            box-shadow: 0 8px 24px -12px {PRIMARY}33;
            transform: translateY(-1px);
        }}

        .bw-metric {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-left: 4px solid {ACCENT};
            border-radius: 14px;
            padding: 1rem 1.2rem;
            box-shadow: 0 2px 10px -6px {PRIMARY}22;
        }}
        .bw-metric .val {{
            font-family: 'Public Sans', sans-serif;
            font-size: 1.9rem;
            color: {INK};
            font-weight: 700;
            line-height: 1.1;
        }}
        .bw-metric .lbl {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {MUTED};
            margin-bottom: 0.35rem;
        }}

        .bw-badge {{
            display: inline-block;
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.03em;
        }}

        .bw-divider {{
            height: 1px;
            background: linear-gradient(90deg, {BORDER}, transparent);
            margin: 1.4rem 0;
            border: none;
        }}

        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 0.8rem 1rem 0.5rem 1rem;
            box-shadow: 0 2px 10px -6px {PRIMARY}22;
        }}

        /* Inputs get a soft aqua focus ring */
        .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 2px {ACCENT}33 !important;
        }}

        .stButton > button {{
            background: linear-gradient(120deg, {ACCENT} 0%, {PRIMARY_LIGHT} 100%);
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            font-family: 'Public Sans', sans-serif;
            transition: 0.15s;
            box-shadow: 0 4px 14px -6px {ACCENT}66;
        }}
        .stButton > button:hover {{
            filter: brightness(1.06);
            box-shadow: 0 6px 18px -6px {ACCENT}88;
        }}

        /* Progress bars pick up the aqua accent */
        div[data-testid="stProgress"] > div > div {{
            background-image: linear-gradient(90deg, {ACCENT}, {PRIMARY_LIGHT});
        }}

        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(eyebrow: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="bw-hero">
            <div class="bw-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, col=None):
    target = col if col is not None else st
    target.markdown(
        f"""
        <div class="bw-metric">
            <div class="lbl"><</div>
            <div class="val">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def risk_badge(category: str) -> str:
    color = RISK_COLORS.get(category, MUTED)
    return f'<span class="bw-badge" style="background:{color}22;color:{color};border:1px solid {color}55;">{category} risk</span>'