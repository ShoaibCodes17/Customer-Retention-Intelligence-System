"""
SHAP-based explainability for the churn model.
Answers "why is THIS customer flagged" — not just that they are.
"""
import shap
import joblib
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from src.config import Config
from src.models.train import FEATURES

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
MODEL_PATH = Path("src/models/churn_model.pkl")

FEATURE_LABELS = {
    "frequency": "how often they order",
    "monetary": "their total historical spend",
    "avg_order_value": "their average order size",
    "estimated_clv": "their estimated lifetime value",
    "recency_ratio": "how overdue they are relative to their usual buying rhythm",
}

_model = None
_explainer = None


def get_explainer():
    global _model, _explainer
    if _explainer is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "churn_model.pkl not found — run 'python -m src.models.train' first"
            )
        _model = joblib.load(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)
    return _model, _explainer


def explain_customer(customer_id, top_n = 3):
    model, explainer = get_explainer()

    row = pd.read_sql(
        text(f"SELECT {', '.join(FEATURES)} FROM rfm_features WHERE customer_id = :cid"),
        engine, params={"cid": customer_id},
    )
    if row.empty:
        return {"error": "customer not found"}

    shap_values = explainer.shap_values(row)
    values = shap_values[0]  # single row in, single row of contributions out

    contributions = list(zip(FEATURES, values, row.iloc[0]))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    reasons = []
    for feature, shap_val, feature_val in contributions[:top_n]:
        reasons.append({
            "feature": feature,
            "label": FEATURE_LABELS.get(feature, feature),
            "value": round(float(feature_val), 2),
            "shap_value": round(float(shap_val), 4),
            "direction": "increases risk" if shap_val > 0 else "decreases risk",
        })

    return {"customer_id": customer_id, "top_reasons": reasons}
