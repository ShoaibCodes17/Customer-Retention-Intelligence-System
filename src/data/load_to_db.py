"""Loads cleaned transactions into MySQL (customers + transactions tables)."""
import pandas as pd
from sqlalchemy import create_engine
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


def run():
    df = pd.read_csv(r"../data/processed/transactions_clean.csv", parse_dates=["invoice_date"])

    customers = (
        df.groupby("customer_id")
        .agg(
            country=("country", "first"),
            first_purchase=("invoice_date", "min"),
            last_purchase=("invoice_date", "max"),
        )
        .reset_index()
    )
     
    customers.to_sql("customers", engine, if_exists="append", index=False,
        method= 'multi', chunksize=1000,
    )

    df['line_total'] = df['quantity'] * df['unit_price']
    
    txns = df[[
        "invoice_no", "stock_code", "description", "quantity",
        "invoice_date", "unit_price", "customer_id", "country", 'line_total'
    ]]

    
    txns.to_sql(
            "transactions", engine, if_exists="append", index=False,
            method= "multi", chunksize=1000,
    )
    print(f"Loaded {len(customers):,} customers and {len(txns):,} transactions")


if __name__ == "__main__":
    run()
