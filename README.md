# GeoXAI-Bore

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest%20%7C%20XGBoost-green)
![Explainable AI](https://img.shields.io/badge/Explainable%20AI-SHAP-orange)
![Status](https://img.shields.io/badge/Status-Under%20Development-yellow)
![Research](https://img.shields.io/badge/Research-Andhra%20Pradesh-blueviolet)

**GeoXAI-Bore** is an Explainable Ensemble Learning Framework for predicting individual borewell failure in the hard-rock aquifers of Andhra Pradesh using multi-source hydrogeological, climatic, and geospatial data.

The project integrates **Random Forest**, **XGBoost**, and **CatBoost** with **SHAP-based Explainable AI (XAI)** and a **Generative AI explanation module** to provide transparent, interpretable, and data-driven borewell failure risk assessment through an interactive analytics dashboard.

---

## Research Motivation

Groundwater is the primary source of irrigation and drinking water in many regions of Andhra Pradesh. In hard-rock aquifers, borewells frequently fail due to groundwater depletion, erratic rainfall, over-extraction, and complex geological conditions.

Existing research primarily focuses on:

- Groundwater level prediction
- Groundwater potential mapping
- Regional groundwater assessment

However, there is limited research on **predicting the failure risk of individual borewells** using multi-source hydrogeological data.

GeoXAI-Bore aims to address this research gap.

---

## Objectives

- Predict individual borewell failure risk.
- Integrate multiple government hydrogeological datasets.
- Compare multiple ensemble machine learning models.
- Explain predictions using SHAP.
- Generate natural-language explanations using Generative AI.
- Develop an interactive dashboard for decision support.

---

## Technology Stack

### Programming

- Python

### Machine Learning

- Random Forest
- XGBoost
- Scikit-learn

### Explainable AI

- SHAP

### Data Processing

- Pandas
- NumPy

### GIS & Spatial Analytics

- GeoPandas
- QGIS
- Rasterio

### Backend

- FastAPI

### Frontend

- Streamlit

### Database

- PostgreSQL

### Visualization

- Plotly
- Folium
- Matplotlib

### Generative AI

- OpenAI GPT / Gemini API

---

## Proposed Workflow

```
Government Data Sources
        │
        ▼
Data Collection
        │
        ▼
Preprocessing
        │
        ▼
Feature Engineering
        │
        ▼
Random Forest
XGBoost
        │
        ▼
Performance Evaluation
        │
        ▼
SHAP Explainability
        │
        ▼
Generative AI Explanation
        │
        ▼
Interactive Dashboard
```

---

## Data Sources

The project uses publicly available government datasets, including:

- Central Ground Water Board (CGWB)
- India-WRIS
- India Meteorological Department (IMD)
- ISRO / NRSC
- Andhra Pradesh groundwater and hydrogeological datasets (where available)

---

## Repository Structure

```
GeoXAI-Bore/
│
├── backend/
├── frontend/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── preprocessing/
│   ├── models/
│   ├── explainability/
│   └── genai/
├── reports/
├── paper/
├── presentation/
├── docs/
├── README.md
├── requirements.txt
└── LICENSE
```

---

## Current Status

- [x] Repository setup
- [x] Project architecture
- [x] Literature review
- [ ] Dataset collection
- [ ] Data preprocessing
- [ ] Feature engineering
- [ ] Model development
- [ ] SHAP explainability
- [ ] GenAI integration
- [ ] Dashboard development
- [ ] Research paper
- [ ] Deployment

---

## Team

- **Devika Janardhanan**
- **Veerapaneni Joshitha**
- **Kuriti Hema Latha**
- **Shaik Mohammed Ayaz**

---

## License

This project is developed for academic and research purposes.


