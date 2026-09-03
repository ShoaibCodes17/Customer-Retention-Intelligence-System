"""Loads the trained model and scores customers for churn probability."""
import joblib
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from src.config import Config
from src.models.train import FEATURES

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
MODEL_PATH = Path("src/models/churn_model.pkl")
_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def score_all_customers():
    model = get_model()
    df = pd.read_sql("SELECT * FROM rfm_features", engine)
    df["churn_probability"] = model.predict_proba(df[FEATURES])[:, 1]

    out = df[["customer_id", "churn_probability"]]
    out.to_sql(
        "churn_predictions", engine, if_exists="replace", index=False,
        method="multi", chunksize=1000,
    )
    return out


def at_risk_customers(min_probability = 0.5):
    query = """
        SELECT p.customer_id, p.churn_probability, r.estimated_clv,
               r.recency_days, r.frequency, r.monetary
        FROM churn_predictions p
        JOIN rfm_features r ON p.customer_id = r.customer_id
        WHERE p.churn_probability >= %(min_probability)s
        ORDER BY r.estimated_clv DESC
    """
    return pd.read_sql(query, engine, params={"min_probability": min_probability})


if __name__ == "__main__":
    scored = score_all_customers()
    print(f"Scored {len(scored):,} customers")
