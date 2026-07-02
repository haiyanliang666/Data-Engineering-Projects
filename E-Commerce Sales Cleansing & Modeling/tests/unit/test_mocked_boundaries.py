from pathlib import Path

import pytest

from src.db.postgres import DatabaseConfig, execute_sql_files
from src.ingest.downloader import download_dataset


def test_download_dataset_wraps_network_errors(mocker, tmp_path):
    mocker.patch(
        "src.ingest.downloader.urlopen",
        side_effect=TimeoutError("network timed out"),
    )

    with pytest.raises(RuntimeError, match="Failed to download dataset"):
        download_dataset("https://example.com/online-retail.xlsx", tmp_path / "raw.xlsx")


def test_execute_sql_files_wraps_database_errors(mocker, tmp_path):
    sql_file = tmp_path / "001.sql"
    sql_file.write_text("select 1;", encoding="utf-8")
    mocker.patch("src.db.postgres.psycopg.connect", side_effect=RuntimeError("db down"))

    config = DatabaseConfig(host="localhost", port=5432, database="retail", user="retail", password="retail")

    with pytest.raises(RuntimeError, match="Failed to execute SQL files"):
        execute_sql_files(config, [Path(sql_file)])
