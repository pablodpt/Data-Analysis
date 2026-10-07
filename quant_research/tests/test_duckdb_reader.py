from __future__ import annotations

import duckdb

from quant_research.io import load_market_data, standardize_ohlcv


def test_duckdb_catalog_and_table_selection_are_read_only(tmp_path):
    db_path = tmp_path / "market.duckdb"
    connection = duckdb.connect(str(db_path))
    connection.execute("CREATE TABLE prices AS SELECT DATE '2020-01-02' AS Date, 100.0 AS Open, 101.0 AS High, 99.0 AS Low, 100.5 AS Close, 1234 AS Volume")
    connection.execute("CREATE TABLE metadata AS SELECT 'unit-test' AS description")
    connection.close()

    loaded = load_market_data(database_path=db_path)
    assert loaded.relation == "main.prices"
    assert set(loaded.tables["table"]) == {"prices", "metadata"}
    standardized, _, _ = standardize_ohlcv(loaded.frame)
    assert standardized.iloc[0]["close"] == 100.5

    # The loader must never alter or create tables in the source database.
    connection = duckdb.connect(str(db_path), read_only=True)
    names = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
    connection.close()
    assert names == {"prices", "metadata"}
