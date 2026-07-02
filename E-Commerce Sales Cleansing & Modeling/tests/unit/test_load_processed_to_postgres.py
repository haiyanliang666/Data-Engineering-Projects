from pathlib import Path

import pandas as pd

from scripts.load_processed_to_postgres import build_config, load_processed_outputs


def test_build_config_uses_docker_compose_defaults():
    config = build_config([])

    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "retail"
    assert config.user == "retail"
    assert config.password == "retail"


def test_load_processed_outputs_loads_expected_tables(mocker, tmp_path):
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    sales = pd.DataFrame({"invoice_no": ["1001"], "quantity": [2]})
    returns = pd.DataFrame({"invoice_no": ["1002"], "quantity": [-1]})
    rejected = pd.DataFrame({"invoice_no": ["1003"], "quantity": [1]})
    sales.to_csv(processed_dir / "sales.csv", index=False)
    returns.to_csv(processed_dir / "returns.csv", index=False)
    rejected.to_csv(processed_dir / "rejected.csv", index=False)

    execute_sql_files = mocker.patch("scripts.load_processed_to_postgres.execute_sql_files")
    execute_sql = mocker.patch("scripts.load_processed_to_postgres.execute_sql")
    load_frame = mocker.patch("scripts.load_processed_to_postgres.load_dataframe_to_table", return_value=1)

    result = load_processed_outputs(
        config=build_config([]),
        processed_dir=processed_dir,
        ddl_dir=Path("sql/ddl"),
        reset=True,
    )

    execute_sql_files.assert_called_once()
    execute_sql.assert_called_once()
    assert load_frame.call_args_list[0].args[2] == "raw_online_retail"
    assert load_frame.call_args_list[1].args[2] == "cleansed_returns"
    assert load_frame.call_args_list[2].args[2] == "rejected_online_retail"
    assert result == {
        "raw_online_retail": 1,
        "cleansed_returns": 1,
        "rejected_online_retail": 1,
    }
