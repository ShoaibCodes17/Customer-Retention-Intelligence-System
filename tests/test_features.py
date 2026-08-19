"""
Basic tests for RFM logic. Run with: pytest tests/
Extend these as you build — e.g. test churn labeling edge cases,
CLV calculation on known inputs, and RFM aggregation correctness.
"""
import pandas as pd


def test_line_total_calculation():
    df = pd.DataFrame({"quantity": [2, 3], "unit_price": [10.0, 5.0]})
    df["line_total"] = df["quantity"] * df["unit_price"]
    assert df["line_total"].tolist() == [20.0, 15.0]


def test_churn_label_threshold():
    inactivity_days = 90
    recency = pd.Series([30, 120, 91, 89])
    is_churned = (recency > inactivity_days).astype(int)
    assert is_churned.tolist() == [0, 1, 1, 0]
