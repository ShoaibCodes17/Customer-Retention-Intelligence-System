import pandas as pd
from pathlib import Path

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_DIR / "data" / "raw"
PROCESSED_PATH = BASE_DIR / "data" / "processed"
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def load_raw(filename: str = "online_retail_2.csv")
    path = RAW_PATH / filename
    if path.suffix == ".csv": 
        df = pd.read_csv(path, encoding="ISO-8859-1")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Standardizing column names — the dataset has slightly different headers
    rename_map = {
        "invoice": "invoice_no",
        "stockcode": "stock_code",
        "price": "unit_price",
        "invoicedate": "invoice_date",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Drop rows with no customer ID — can't tie a retention action to an unknown customer
    df = df.dropna(subset=["customer_id"])

    # Remove cancelled orders (invoice numbers starting with 'C') and bad rows
    df = df[~df["invoice_no"].astype(str).str.startswith("C")]
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]

    df["customer_id"] = df["customer_id"].astype(int).astype(str) # CONVERTING THIS INTO STRING BECAUSE IT'S A UNIQUE IDENTIFIER
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["line_total"] = df["quantity"] * df["unit_price"]

    df = df.drop_duplicates()
    return df


def run():
    df = load_raw()
    cleaned = clean(df)
    out_path = PROCESSED_PATH / "transactions_clean.csv"
    cleaned.to_csv(out_path, index=False)
    print(f"Cleaned {len(cleaned):,} rows -> {out_path}")


# run()
if __name__ == "__main__":
    run()
