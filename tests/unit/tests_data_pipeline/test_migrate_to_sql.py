from pathlib import Path

import pandas as pd
import pytest

from fpi.data_pipeline.migrate_to_sql import get_engine, migrate_all_cleaned


class TestMigrateToSql:
    """
    Unit tests for the SQL migration process defined in `migrate_to_sql`.

    These tests ensure that:
        1. Cleaned CSV files are correctly migrated into SQL tables.
        2. French decimal format is properly converted to numeric values.
        3. Basic migration behavior works as expected with simple datasets.
    """

    @pytest.fixture
    def tmp_csv_dir(self, tmp_path: Path) -> Path:
        """
        Create a temporary directory containing two small CSV files used for testing.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.

        Returns
        -------
        Path
            Path to the root directory where the temporary CSV files are stored.
        """
        df1 = pd.DataFrame(
            {
                "value": ["10,00", "20,00"],
                "code": [1, 2],
            }
        )
        file1 = tmp_path / "year2024" / "file_one.csv"
        file1.parent.mkdir(parents=True, exist_ok=True)
        df1.to_csv(file1, index=False, decimal=",")

        df2 = pd.DataFrame(
            {
                "value": ["30,00"],
                "code": [3],
            }
        )
        file2 = tmp_path / "year2023" / "file_two.csv"
        file2.parent.mkdir(parents=True, exist_ok=True)
        df2.to_csv(file2, index=False, decimal=",")

        return tmp_path

    def test_csv_files_migrated(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Two cleaned CSV files located under the temporary directory are
        migrated into separate SQL tables.

        The test verifies that:
            * Both output tables exist.
            * Both tables contain rows after migration.
        """
        engine = get_engine(db_path="data/sql/app.db")
        migrate_all_cleaned(engine=engine, cleaned_root=str(tmp_csv_dir))

        df_one = pd.read_sql_table("file_one", con=engine)
        df_two = pd.read_sql_table("file_two", con=engine)

        assert not df_one.empty
        assert not df_two.empty

        # Cleanup unwanted tables created during migration
        with engine.connect() as conn:
            conn.exec_driver_sql("DROP TABLE IF EXISTS file_one")
            conn.exec_driver_sql("DROP TABLE IF EXISTS file_two")

    def test_decimal_values_converted(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: The migration correctly handles French decimal format.

        The test verifies that:
            * The 'value' column is stored as a numeric dtype.
            * The numeric values are correctly parsed as floats.
        """
        engine = get_engine(db_path="data/sql/app.db")
        migrate_all_cleaned(engine=engine, cleaned_root=str(tmp_csv_dir))

        df = pd.read_sql_table("file_one", con=engine)

        assert pd.api.types.is_numeric_dtype(df["value"])
        assert set(df["value"].tolist()) == {10.0, 20.0}

        # Cleanup unwanted tables created during migration
        with engine.connect() as conn:
            conn.exec_driver_sql("DROP TABLE IF EXISTS file_one")
            conn.exec_driver_sql("DROP TABLE IF EXISTS file_two")
