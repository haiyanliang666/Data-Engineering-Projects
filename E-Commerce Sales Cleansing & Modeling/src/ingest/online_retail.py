from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

COLUMN_MAP = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}


def normalize_online_retail_columns(raw: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """Normalize Online Retail source columns into the raw staging contract."""
    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    normalized = raw.loc[:, REQUIRED_COLUMNS].rename(columns=COLUMN_MAP).copy()
    normalized["invoice_no"] = normalized["invoice_no"].astype(str)
    normalized["stock_code"] = normalized["stock_code"].astype(str)
    normalized["source_file"] = source_file
    normalized["loaded_at"] = pd.Timestamp.now(tz="UTC")
    return normalized


def load_online_retail_file(path: str | Path) -> pd.DataFrame:
    """Load a local Online Retail Excel workbook into the raw staging shape."""
    workbook = Path(path)
    if not workbook.exists():
        raise FileNotFoundError(workbook)

    raw = pd.read_excel(workbook)
    return normalize_online_retail_columns(raw, source_file=workbook.name)


def write_raw_csv(source_path: str | Path, output_path: str | Path) -> Path:
    """Convert the workbook into a normalized raw CSV file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    load_online_retail_file(source_path).to_csv(output, index=False)
    return output
