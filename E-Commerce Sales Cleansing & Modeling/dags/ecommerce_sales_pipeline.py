from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from airflow.sdk import dag, task
except ImportError:  # pragma: no cover - Airflow 2 compatibility
    from airflow.decorators import dag, task

from src.db.load_raw import load_csv_to_raw_table
from src.db.postgres import DatabaseConfig, execute_sql, execute_sql_files
from src.ingest.online_retail import load_online_retail_file
from src.transform.cleanse import cleanse_online_retail

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"
RAW_OUTPUT = PROJECT_ROOT / "data" / "processed" / "raw_online_retail.csv"
SALES_OUTPUT = PROJECT_ROOT / "data" / "processed" / "sales.csv"
RETURNS_OUTPUT = PROJECT_ROOT / "data" / "processed" / "returns.csv"
REJECTED_OUTPUT = PROJECT_ROOT / "data" / "processed" / "rejected.csv"


@dag(
    dag_id="ecommerce_sales_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["ecommerce", "sales", "postgres"],
)
def ecommerce_sales_pipeline():
    @task
    def ingest_raw_data() -> str:
        raw = load_online_retail_file(SOURCE_FILE)
        RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        raw.to_csv(RAW_OUTPUT, index=False)
        return str(RAW_OUTPUT)

    @task
    def validate_raw_data(raw_path: str) -> str:
        if not Path(raw_path).exists():
            raise FileNotFoundError(raw_path)
        return raw_path

    @task
    def cleanse_data(raw_path: str) -> dict[str, str]:
        raw = load_online_retail_file(SOURCE_FILE)
        result = cleanse_online_retail(raw)
        result.sales.to_csv(SALES_OUTPUT, index=False)
        result.returns.to_csv(RETURNS_OUTPUT, index=False)
        result.rejected.to_csv(REJECTED_OUTPUT, index=False)
        return {
            "sales": str(SALES_OUTPUT),
            "returns": str(RETURNS_OUTPUT),
            "rejected": str(REJECTED_OUTPUT),
        }

    @task
    def load_raw_to_postgres(raw_path: str) -> int:
        config = DatabaseConfig("postgres", 5432, "retail", "retail", "retail")
        execute_sql_files(config, sorted((PROJECT_ROOT / "sql" / "ddl").glob("*.sql")))
        execute_sql(config, "TRUNCATE raw_online_retail;")
        return load_csv_to_raw_table(config, raw_path)

    @task
    def load_dimensions() -> None:
        config = DatabaseConfig("postgres", 5432, "retail", "retail", "retail")
        execute_sql_files(config, [PROJECT_ROOT / "sql" / "transformations" / "001_load_dimensions.sql"])

    @task
    def load_fact_sales() -> None:
        config = DatabaseConfig("postgres", 5432, "retail", "retail", "retail")
        execute_sql_files(config, [PROJECT_ROOT / "sql" / "transformations" / "002_load_fact_sales.sql"])

    @task
    def run_quality_checks() -> None:
        config = DatabaseConfig("postgres", 5432, "retail", "retail", "retail")
        execute_sql_files(config, [PROJECT_ROOT / "sql" / "transformations" / "003_quality_checks.sql"])

    raw_path = ingest_raw_data()
    validated = validate_raw_data(raw_path)
    loaded_count = load_raw_to_postgres(validated)
    cleanse_data(validated) >> loaded_count >> load_dimensions() >> load_fact_sales() >> run_quality_checks()


ecommerce_sales_pipeline()
