# E-Commerce Sales Cleansing & Modeling

This project ingests the UCI/Kaggle-style Online Retail dataset, cleans unreliable sales records, models the result in Postgres, orchestrates the workflow with Airflow, and exposes dashboard-ready analytics views.

## Business Goal

Enable an e-commerce store to track revenue, top products, and monthly growth accurately. Clean and reliable data helps marketing understand product performance and helps finance monitor revenue trends.

## Dataset

Default local source:

```text
Online Retail.xlsx
```

Reference sources:

- UCI Online Retail Data: https://archive.ics.uci.edu/ml/datasets/online+retail
- Kaggle E-Commerce datasets: https://www.kaggle.com/datasets?search=ecommerce

Expected columns:

```text
InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
```

## Project Layout

```text
data/raw/                raw downloaded files
data/processed/          normalized and cleansed outputs
src/ingest/              file download and ingestion code
src/transform/           cleansing and data quality code
src/db/                  Postgres execution and load helpers
sql/ddl/                 warehouse table and view definitions
sql/transformations/     dimension, fact, and quality SQL
dags/                    Airflow DAGs
dashboard/               Streamlit dashboard
tests/unit/              fast Python tests
tests/integration/       Postgres-backed tests
```

## Local Setup

Install dependencies:

```bash
pip install -e '.[dev]'
```

Run code quality checks:

```bash
black --check .
ruff check .
pytest tests/unit
```

Format and lint locally:

```bash
black .
ruff check . --fix
pre-commit run --all-files
```

Install the automatic Git pre-commit hook from the repository root:

```bash
cd "/Users/.../..."
pre-commit install --config "E-Commerce Sales Cleansing & Modeling/.pre-commit-config.yaml"
```

`pip install -e '.[dev]'` installs tools such as `pytest`, `black`, `ruff`, and `pre-commit`.
`pre-commit install` connects those checks to Git so they run automatically before each `git commit`.

## Docker Compose

Start Postgres:

```bash
docker compose up -d postgres
```

Run integration tests:

```bash
pytest tests/integration
```

Tear down services:

```bash
docker compose down
```

## Ingestion

Normalize the local workbook from Python:

```python
from src.ingest.online_retail import write_raw_csv

write_raw_csv("Online Retail.xlsx", "data/processed/raw_online_retail.csv")
```

The raw staging contract is:

```text
invoice_no, stock_code, description, quantity, invoice_date,
unit_price, customer_id, country, source_file, loaded_at
```

## Cleansing Rules

The main sales dataset:

- removes exact duplicate rows
- standardizes `invoice_date` to a timestamp
- excludes missing `customer_id`
- excludes invalid dates
- excludes zero or negative `unit_price`
- excludes returns from `fact_sales`
- calculates `total_amount = quantity * unit_price`

Negative `quantity` rows are preserved separately as returns for auditability.

## Postgres Model

Warehouse tables:

- `raw_online_retail`
- `cleansed_returns`
- `rejected_online_retail`
- `dim_product`
- `dim_customer`
- `dim_date`
- `fact_sales`

Dashboard views:

- `vw_daily_revenue`
- `vw_weekly_revenue`
- `vw_top_products`
- `vw_monthly_growth`

## Airflow

Start Airflow services:

```bash
docker compose up airflow-webserver airflow-scheduler
```

Pipeline stages:

```text
ingest_raw_data
validate_raw_data
cleanse_data
load_dimensions
load_fact_sales
run_quality_checks
```

The DAG is defined in `dags/ecommerce_sales_pipeline.py`.

## Dashboard

Run the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard reads from Postgres views and shows:

- daily revenue
- weekly revenue
- top products by revenue
- monthly growth

## CI/CD

GitHub Actions runs:

```text
install dependencies
black --check .
ruff check .
pytest tests/unit
pytest tests/integration
Airflow DAG import check
```

Deployment should only happen after all checks pass.

## Development Container

Open the project in VS Code and choose "Reopen in Container". The dev container uses the Docker Compose services and installs the project with development dependencies.

## Data Quality Assumptions

- `fact_sales` excludes returns and invalid revenue rows.
- Returns are preserved outside the main fact table for auditability.
- Rows missing `CustomerID` are excluded from customer-level analytics.
- Dashboard users query views instead of raw warehouse tables.
- Postgres is the source of truth for modeled analytics.
