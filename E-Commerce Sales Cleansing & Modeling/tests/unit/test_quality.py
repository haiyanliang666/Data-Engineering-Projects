import pandas as pd
import pytest

from src.transform.quality import run_fact_sales_quality_checks


def test_run_fact_sales_quality_checks_accepts_valid_sales():
    fact_sales = pd.DataFrame(
        {
            "invoice_no": ["1001"],
            "product_key": [1],
            "customer_key": [1],
            "date_key": [20240105],
            "quantity": [2],
            "total_amount": [7.0],
        }
    )

    assert run_fact_sales_quality_checks(fact_sales) == []


def test_run_fact_sales_quality_checks_reports_invalid_sales():
    fact_sales = pd.DataFrame(
        {
            "invoice_no": [None],
            "product_key": [None],
            "customer_key": [1],
            "date_key": [20240105],
            "quantity": [-1],
            "total_amount": [-7.0],
        }
    )

    with pytest.raises(ValueError) as exc_info:
        run_fact_sales_quality_checks(fact_sales)

    message = str(exc_info.value)
    assert "invoice_no contains nulls" in message
    assert "quantity contains negative values" in message
    assert "total_amount contains negative values" in message
    assert "product_key contains nulls" in message
