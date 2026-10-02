"""Prepare the maintenance runtime while lightweight site requests remain usable."""
import logging


def prepare_prediction_runtime():
    try:
        # Importing sklearn, xgboost and SHAP dominates the first request on a small host.
        from backend.explain import get_explainer
        get_explainer()
        logging.getLogger(__name__).info('Maintenance models and SHAP explainer are ready')
    except Exception:
        # Keep site lookup/chat available; a prediction request can retry normal loading.
        logging.getLogger(__name__).exception('Maintenance runtime preparation failed')
