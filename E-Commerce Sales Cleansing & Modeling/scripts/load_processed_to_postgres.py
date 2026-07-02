from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.load_raw import load_dataframe_to_table  # noqa: E402
from src.db.postgres import DatabaseConfig, execute_sql, execute_sql_files  # noqa: E402


def build_config(argv: list[str] | None = None) -> DatabaseConfig:
    parser = argparse.ArgumentParser(description="Load processed Online Retail CSV outputs into Postgres.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--database", default="retail")
    parser.add_argument("--user", default="retail")
    parser.add_argument("--password", default="retail")
    args, _ = parser.parse_known_args(argv)
    return DatabaseConfig(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    columns = pd.read_csv(path, nrows=0).columns
    date_columns = [column for column in ["invoice_date", "loaded_at"] if column in columns]
    return pd.read_csv(path, parse_dates=date_columns, low_memory=False)


def load_processed_outputs(
    config: DatabaseConfig,
    processed_dir: Path,
    ddl_dir: Path,
    reset: bool,
) -> dict[str, int]:
    execute_sql_files(config, sorted(ddl_dir.glob("*.sql")))

    if reset:
        execute_sql(
            config,
            """
            TRUNCATE
                raw_online_retail,
                cleansed_returns,
                rejected_online_retail,
                fact_sales
            RESTART IDENTITY CASCADE;
            """,
        )

    table_loads = {
        "raw_online_retail": _read_csv(processed_dir / "sales.csv").drop(columns=["total_amount"], errors="ignore"),
        "cleansed_returns": _read_csv(processed_dir / "returns.csv"),
        "rejected_online_retail": _read_csv(processed_dir / "rejected.csv"),
    }

    counts: dict[str, int] = {}
    for table_name, frame in table_loads.items():
        counts[table_name] = load_dataframe_to_table(config, frame, table_name)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Load processed Online Retail CSV outputs into Postgres.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--database", default="retail")
    parser.add_argument("--user", default="retail")
    parser.add_argument("--password", default="retail")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--ddl-dir", type=Path, default=Path("sql/ddl"))
    parser.add_argument("--append", action="store_true", help="Append instead of truncating target tables first.")
    args = parser.parse_args()

    config = DatabaseConfig(args.host, args.port, args.database, args.user, args.password)
    counts = load_processed_outputs(
        config=config,
        processed_dir=args.processed_dir,
        ddl_dir=args.ddl_dir,
        reset=not args.append,
    )

    for table_name, row_count in counts.items():
        print(f"{table_name}: {row_count:,} rows loaded")


if __name__ == "__main__":
    main()
