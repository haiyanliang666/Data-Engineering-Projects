import pandas as pd

from src.transform.cleanse import cleanse_online_retail


def test_cleanse_online_retail_excludes_invalid_sales_and_keeps_returns():
    raw = pd.DataFrame(
        [
            {
                "invoice_no": "1001",
                "stock_code": "A1",
                "description": "Widget",
                "quantity": 2,
                "invoice_date": "2024-01-05 10:30",
                "unit_price": 3.5,
                "customer_id": 42,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
            {
                "invoice_no": "1001",
                "stock_code": "A1",
                "description": "Widget",
                "quantity": 2,
                "invoice_date": "2024-01-05 10:30",
                "unit_price": 3.5,
                "customer_id": 42,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
            {
                "invoice_no": "1002",
                "stock_code": "A2",
                "description": "Return",
                "quantity": -1,
                "invoice_date": "2024-01-06",
                "unit_price": 4.0,
                "customer_id": 43,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
            {
                "invoice_no": "1003",
                "stock_code": "A3",
                "description": "Missing customer",
                "quantity": 1,
                "invoice_date": "2024-01-07",
                "unit_price": 5.0,
                "customer_id": None,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
            {
                "invoice_no": "1004",
                "stock_code": "A4",
                "description": "Free item",
                "quantity": 1,
                "invoice_date": "2024-01-08",
                "unit_price": 0,
                "customer_id": 44,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
            {
                "invoice_no": "1005",
                "stock_code": "A5",
                "description": "Bad date",
                "quantity": 1,
                "invoice_date": "not-a-date",
                "unit_price": 1.0,
                "customer_id": 45,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            },
        ]
    )

    result = cleanse_online_retail(raw)

    assert result.sales["invoice_no"].tolist() == ["1001"]
    assert result.sales.loc[0, "invoice_date"] == pd.Timestamp("2024-01-05 10:30")
    assert result.sales.loc[0, "total_amount"] == 7.0
    assert result.returns["invoice_no"].tolist() == ["1002"]
    assert set(result.rejected["invoice_no"]) == {"1003", "1004", "1005"}


def test_cleanse_online_retail_converts_customer_id_to_string_without_decimal():
    raw = pd.DataFrame(
        [
            {
                "invoice_no": "1001",
                "stock_code": "A1",
                "description": "Widget",
                "quantity": 2,
                "invoice_date": "2024-01-05",
                "unit_price": 3.5,
                "customer_id": 17850.0,
                "country": "United Kingdom",
                "source_file": "sample.xlsx",
                "loaded_at": "2024-02-01",
            }
        ]
    )

    result = cleanse_online_retail(raw)

    assert result.sales.loc[0, "customer_id"] == "17850"
