from __future__ import annotations

from pathlib import Path

import pandas as pd


def money(value: float) -> str:
    return f"${value:,.2f}"


def main() -> None:
    processed_dir = Path("data/processed")
    sales_path = processed_dir / "sales.csv"
    returns_path = processed_dir / "returns.csv"
    rejected_path = processed_dir / "rejected.csv"

    sales = pd.read_csv(sales_path, parse_dates=["invoice_date"])
    returns = pd.read_csv(returns_path)
    rejected = pd.read_csv(rejected_path)

    daily = sales.groupby(sales["invoice_date"].dt.date)["total_amount"].sum().reset_index(name="revenue").tail(30)
    top_products = (
        sales.groupby(["stock_code", "description"], dropna=False)["total_amount"]
        .sum()
        .reset_index(name="revenue")
        .sort_values("revenue", ascending=False)
        .head(20)
    )
    monthly = (
        sales.assign(month=sales["invoice_date"].dt.to_period("M").astype(str))
        .groupby("month")["total_amount"]
        .sum()
        .reset_index(name="revenue")
    )

    summary = {
        "Sales rows": f"{len(sales):,}",
        "Returns rows": f"{len(returns):,}",
        "Rejected rows": f"{len(rejected):,}",
        "Revenue": money(float(sales["total_amount"].sum())),
        "Unique customers": f"{sales['customer_id'].nunique():,}",
        "Unique products": f"{sales['stock_code'].nunique():,}",
    }
    cards = "\n".join(
        f"<div class='card'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
        for label, value in summary.items()
    )

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>E-Commerce Sales Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #f7f7f4; color: #222; }}
    h1 {{ margin-bottom: 6px; }}
    .sub {{ color: #666; margin-bottom: 24px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 20px 0; }}
    .card {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px; }}
    .label {{ color: #666; font-size: 13px; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 8px; }}
    section {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 18px; margin: 18px 0; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #eee; padding: 8px; text-align: left; }}
    th {{ background: #fafafa; }}
  </style>
</head>
<body>
  <h1>E-Commerce Sales Cleansing & Modeling</h1>
  <div class="sub">Generated from <code>data/processed/sales.csv</code></div>
  <div class="cards">{cards}</div>
  <section><h2>Last 30 Daily Revenue Points</h2>{daily.to_html(index=False)}</section>
  <section><h2>Top 20 Products by Revenue</h2>{top_products.to_html(index=False)}</section>
  <section><h2>Monthly Revenue</h2>{monthly.to_html(index=False)}</section>
</body>
</html>
"""
    output_path = processed_dir / "report.html"
    output_path.write_text(html, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
