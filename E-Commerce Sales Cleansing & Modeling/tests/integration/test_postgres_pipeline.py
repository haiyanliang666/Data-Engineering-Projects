from pathlib import Path

import psycopg
import pytest

from src.db.postgres import DatabaseConfig, execute_sql_files

pytestmark = pytest.mark.integration


def test_postgres_star_schema_pipeline_populates_fact_sales():
    config = DatabaseConfig("localhost", 5432, "retail", "retail", "retail")
    root = Path(__file__).resolve().parents[2]

    execute_sql_files(config, sorted((root / "sql" / "ddl").glob("*.sql")))

    with psycopg.connect(config.dsn) as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE raw_online_retail, fact_sales RESTART IDENTITY CASCADE;")
            cursor.execute("""
                INSERT INTO raw_online_retail (
                    invoice_no, stock_code, description, quantity, invoice_date,
                    unit_price, customer_id, country, source_file, loaded_at
                )
                VALUES
                    ('1001', 'A1', 'Widget', 2, '2024-01-05 10:30', 3.50, '42', 'United Kingdom', 'test', NOW()),
                    ('1002', 'A2', 'Return', -1, '2024-01-06 11:30', 4.00, '43', 'United Kingdom', 'test', NOW());
                """)
        conn.commit()

    execute_sql_files(config, [root / "sql" / "transformations" / "001_load_dimensions.sql"])
    execute_sql_files(config, [root / "sql" / "transformations" / "002_load_fact_sales.sql"])

    with psycopg.connect(config.dsn) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM fact_sales;")
            count, revenue = cursor.fetchone()

    assert count == 1
    assert revenue == 7
