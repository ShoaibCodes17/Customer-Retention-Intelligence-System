import pandas as pd
from sqlalchemy import create_engine
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

def business_impact_report(threshold: float = 0.5, win_back_rate: float = 0.15):
    df = pd.read_sql(f"""
        SELECT p.customer_id, p.churn_probability, r.estimated_clv
        FROM churn_predictions p JOIN rfm_features r ON p.customer_id = r.customer_id
        WHERE p.churn_probability >= {threshold}
    """, engine)

    flagged_clv = df["estimated_clv"].sum()
    projected_value_protected = flagged_clv * win_back_rate

    print(f"Customers flagged at-risk: {len(df):,}")
    print(f"Total CLV flagged at-risk: ${flagged_clv:,.2f}")
    print(f"Projected value protected (assumes {win_back_rate:.0%} win-back rate): ${projected_value_protected:,.2f}")

if __name__ == "__main__":
    business_impact_report()