from __future__ import annotations

import pandas as pd


def run_fact_sales_quality_checks(fact_sales: pd.DataFrame) -> list[str]:
    """Validate core fact_sales invariants and raise when any check fails."""
    failures: list[str] = []
    required_not_null = ["invoice_no", "product_key", "customer_key", "date_key"]
    for column in required_not_null:
        if column in fact_sales.columns and fact_sales[column].isna().any():
            failures.append(f"{column} contains nulls")

    if "quantity" in fact_sales.columns and (fact_sales["quantity"] < 0).any():
        failures.append("quantity contains negative values")
    if "total_amount" in fact_sales.columns and (fact_sales["total_amount"] < 0).any():
        failures.append("total_amount contains negative values")
    if "total_amount" in fact_sales.columns and fact_sales["total_amount"].sum() == 0:
        failures.append("total revenue is zero")

    if failures:
        raise ValueError("; ".join(failures))
    return failures
