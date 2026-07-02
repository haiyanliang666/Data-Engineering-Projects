from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.db.postgres import DatabaseConfig


def load_dataframe_to_table(config: DatabaseConfig, frame: pd.DataFrame, table_name: str) -> int:
    """Load a normalized DataFrame into Postgres using pandas SQL support."""
    from sqlalchemy import create_engine

    url = f"postgresql+psycopg://{config.user}:{config.password}" f"@{config.host}:{config.port}/{config.database}"
    engine = create_engine(url)
    frame.to_sql(table_name, engine, if_exists="append", index=False)
    return len(frame)


def load_dataframe_to_raw_table(
    config: DatabaseConfig, frame: pd.DataFrame, table_name: str = "raw_online_retail"
) -> int:
    return load_dataframe_to_table(config, frame, table_name)


def load_csv_to_raw_table(config: DatabaseConfig, csv_path: str | Path) -> int:
    frame = pd.read_csv(csv_path)
    return load_dataframe_to_raw_table(config, frame)
