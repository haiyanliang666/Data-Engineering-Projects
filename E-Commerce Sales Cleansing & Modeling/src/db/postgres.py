from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import psycopg
except ImportError:  # pragma: no cover - exercised only when dependencies are absent
    psycopg = None


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str

    @property
    def dsn(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} " f"user={self.user} password={self.password}"


def execute_sql_files(config: DatabaseConfig, sql_files: list[Path]) -> None:
    """Execute SQL files in order inside one database connection."""
    if psycopg is None:
        raise RuntimeError("Failed to execute SQL files") from ImportError("psycopg is not installed")

    try:
        with psycopg.connect(config.dsn) as conn:
            with conn.cursor() as cursor:
                for sql_file in sql_files:
                    cursor.execute(sql_file.read_text(encoding="utf-8"))
            conn.commit()
    except Exception as exc:
        raise RuntimeError("Failed to execute SQL files") from exc


def execute_sql(config: DatabaseConfig, sql: str) -> None:
    """Execute a SQL statement inside one database transaction."""
    if psycopg is None:
        raise RuntimeError("Failed to execute SQL") from ImportError("psycopg is not installed")

    try:
        with psycopg.connect(config.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
    except Exception as exc:
        raise RuntimeError("Failed to execute SQL") from exc
