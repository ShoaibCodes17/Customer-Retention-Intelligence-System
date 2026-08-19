from flask import Blueprint, jsonify, request, Flask
import pandas as pd
from sqlalchemy import text
from src.api.db import engine
from src.models.predict import at_risk_customers
from src.agent.retention_agent import generate_retention_action
from src.models.explain import explain_customer

api = Blueprint("api", __name__)


@api.route("/health")
def health():
    return jsonify(status="ok")


@api.route("/customers/at-risk")
def get_at_risk():
    min_prob = float(request.args.get("min_probability", 0.5))
    df = at_risk_customers(min_prob)
    return jsonify(df.to_dict(orient="records"))

@api.route("/customers/<customer_id>/explain")
def explain(customer_id):
    result = explain_customer(customer_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@api.route("/customers/<customer_id>/generate-action", methods=["POST"])
def generate_action(customer_id):
    df = pd.read_sql(
        text("""SELECT customer_id, recency_days, frequency, monetary, estimated_clv, recency_ratio
           FROM rfm_features WHERE customer_id = :customer_id"""),
        engine,
        params={"customer_id": customer_id},
    )
    if df.empty:
        return jsonify(error="customer not found"), 404
    
    explanation = explain_customer(customer_id)
    reasons = explanation.get("top_reasons", [])

    action = generate_retention_action(df.iloc[0].to_dict())

    with engine.begin() as conn:
        conn.exec_driver_sql(
            """INSERT INTO retention_actions
               (customer_id, email_subject, email_body, suggested_offer)
               VALUES (%s, %s, %s, %s)""",
            (customer_id, action["subject"], action["body"], action["offer"]),
        )
    return jsonify(action)

@api.route("/customers/<customer_id>/approve", methods=["POST"])
def approve_action(customer_id):
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """UPDATE retention_actions SET status = 'approved'
               WHERE customer_id = %s
               ORDER BY generated_at DESC LIMIT 1""",
            (customer_id,),
        )
    return jsonify(status="approved")
