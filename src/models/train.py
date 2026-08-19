"""Trains a churn classifier on the RFM feature table and saves it."""
import joblib
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
MODEL_PATH = Path("src/models/churn_model.pkl")

FEATURES = ["frequency", "monetary", "avg_order_value", "estimated_clv", "recency_ratio"]


def run():
    df = pd.read_sql("SELECT * FROM rfm_features", engine)
    X, y = df[FEATURES], df["is_churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, preds))
    print(f"ROC-AUC: {roc_auc_score(y_test, probs):.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")


if __name__ == "__main__":
    run()
