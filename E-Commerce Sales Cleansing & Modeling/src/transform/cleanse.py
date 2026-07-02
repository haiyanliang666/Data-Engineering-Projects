from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleansedRetailData:
    sales: pd.DataFrame
    returns: pd.DataFrame
    rejected: pd.DataFrame


def _customer_id_to_string(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def cleanse_online_retail(raw: pd.DataFrame) -> CleansedRetailData:
    """Clean raw Online Retail records into sales, returns, and rejected datasets."""
    cleaned = raw.drop_duplicates().copy()
    cleaned["invoice_date"] = pd.to_datetime(cleaned["invoice_date"], errors="coerce", format="mixed")
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["customer_id"] = cleaned["customer_id"].map(_customer_id_to_string)
    cleaned["total_amount"] = cleaned["quantity"] * cleaned["unit_price"]

    returns_mask = cleaned["quantity"] < 0
    invalid_mask = (
        cleaned["invoice_no"].isna()
        | cleaned["stock_code"].isna()
        | cleaned["customer_id"].isna()
        | cleaned["invoice_date"].isna()
        | cleaned["quantity"].isna()
        | cleaned["unit_price"].isna()
        | (cleaned["unit_price"] <= 0)
    )
    sales_mask = (~invalid_mask) & (~returns_mask) & (cleaned["quantity"] > 0)
    rejected_mask = invalid_mask | ((cleaned["quantity"] <= 0) & (~returns_mask))

    sales = cleaned.loc[sales_mask].reset_index(drop=True)
    returns = cleaned.loc[returns_mask & (~invalid_mask)].reset_index(drop=True)
    rejected = cleaned.loc[rejected_mask].reset_index(drop=True)
    return CleansedRetailData(sales=sales, returns=returns, rejected=rejected)


def write_cleansed_outputs(raw: pd.DataFrame, output_dir: str) -> CleansedRetailData:
    """Write cleansed CSV outputs for inspection and downstream loading."""
    result = cleanse_online_retail(raw)
    result.sales.to_csv(f"{output_dir}/sales.csv", index=False)
    result.returns.to_csv(f"{output_dir}/returns.csv", index=False)
    result.rejected.to_csv(f"{output_dir}/rejected.csv", index=False)
    return result
