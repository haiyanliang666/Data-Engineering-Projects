from pathlib import Path

import pandas as pd
import pytest

from src.ingest.online_retail import (
    REQUIRED_COLUMNS,
    load_online_retail_file,
    normalize_online_retail_columns,
)


def test_normalize_online_retail_columns_adds_metadata_and_standard_names():
    raw = pd.DataFrame(
        {
            "InvoiceNo": ["536365"],
            "StockCode": ["85123A"],
            "Description": ["WHITE HANGING HEART T-LIGHT HOLDER"],
            "Quantity": [6],
            "InvoiceDate": ["12/1/2010 8:26"],
            "UnitPrice": [2.55],
            "CustomerID": [17850],
            "Country": ["United Kingdom"],
        }
    )

    result = normalize_online_retail_columns(raw, source_file="sample.xlsx")

    assert list(result.columns) == [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
        "source_file",
        "loaded_at",
    ]
    assert result.loc[0, "source_file"] == "sample.xlsx"
    assert pd.notna(result.loc[0, "loaded_at"])


def test_normalize_online_retail_columns_rejects_missing_required_columns():
    raw = pd.DataFrame({column: [] for column in REQUIRED_COLUMNS if column != "InvoiceNo"})

    with pytest.raises(ValueError, match="Missing required columns: InvoiceNo"):
        normalize_online_retail_columns(raw, source_file="bad.xlsx")


def test_load_online_retail_file_uses_excel_reader(mocker, tmp_path):
    workbook = tmp_path / "Online Retail.xlsx"
    workbook.touch()
    read_excel = mocker.patch(
        "src.ingest.online_retail.pd.read_excel",
        return_value=pd.DataFrame(
            {
                "InvoiceNo": ["536365"],
                "StockCode": ["85123A"],
                "Description": ["WHITE HANGING HEART T-LIGHT HOLDER"],
                "Quantity": [6],
                "InvoiceDate": ["12/1/2010 8:26"],
                "UnitPrice": [2.55],
                "CustomerID": [17850],
                "Country": ["United Kingdom"],
            }
        ),
    )

    result = load_online_retail_file(workbook)

    read_excel.assert_called_once_with(Path(workbook))
    assert result.loc[0, "invoice_no"] == "536365"


def test_load_online_retail_file_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_online_retail_file(tmp_path / "missing.xlsx")
