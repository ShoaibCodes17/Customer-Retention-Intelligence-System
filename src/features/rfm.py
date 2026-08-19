"""
Computing RFM (Recency, Frequency, Monetary) features, an estimated CLV,
and a churn label for every customer.
"""
import pandas as pd
from sqlalchemy import create_engine
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


def compute_rfm() -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM transactions", engine, parse_dates=["invoice_date"])
    observation_date = df["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("customer_id")
        .agg(
            recency_days=("invoice_date", lambda x: (observation_date - x.max()).days),
            frequency=("invoice_no", "nunique"),
            monetary=("line_total", "sum"),
        ).round(4)
        .reset_index() 
    )
    # avg_days_between_orders: mean gap between a customer's consecutive orders
    order_dates = (
        df.sort_values("invoice_date")
          .groupby("customer_id")["invoice_date"]
          .apply(lambda x: x.drop_duplicates())  # one date per invoice, not per line item
    )

    gaps = order_dates.groupby("customer_id").apply(lambda x: x.diff().dt.days.dropna())
    avg_gap = gaps.groupby("customer_id").mean().rename("avg_days_between_orders")

    rfm = rfm.merge(avg_gap, on="customer_id", how="left")

    # one-time buyers have no gap to compute — fall back to their single recency value
    rfm["avg_days_between_orders"] = (rfm["avg_days_between_orders"].fillna(rfm["recency_days"])).round(4)

    # Simple CLV estimate: average order value x frequency x an assumed loyalty multiplier.
    # Swap this for a proper BG/NBD or Gamma-Gamma model later if you want to go deeper.
    rfm["avg_order_value"] = (rfm["monetary"] / rfm["frequency"]).round(2)
    rfm["estimated_clv"] = (rfm["avg_order_value"] * rfm["frequency"] * 1.5).round(2) # taking 1.5 here as an arbitary value by imagining that customer will give us 50% revenue if we retain him

    # recency_ratio replaces raw recency_days as a feature (from your bias question)
    rfm["recency_ratio"] = (rfm["recency_days"] / rfm["avg_days_between_orders"].replace(0, 1)).round(4)

    # Label churn: no purchase inside the inactivity window used for training
    rfm["is_churned"] = (rfm["recency_days"] > Config.CHURN_INACTIVITY_DAYS).astype(int)

    return rfm


def run():
    rfm = compute_rfm()
    rfm.to_sql(
        "rfm_features", engine, if_exists="replace", index=False,
        method="multi", chunksize=1000,
    )
    print(
        f"Computed RFM features for {len(rfm):,} customers "
        f"({rfm['is_churned'].mean():.1%} labeled churned)"
    )


if __name__ == "__main__":
    run()
