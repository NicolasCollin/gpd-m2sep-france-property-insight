import pandas as pd


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the core cleaning logic from `clean_data` on a DataFrame.

    Steps:
    1. Normalize column names (lowercase, strip).
    2. Rename columns to English equivalents.
    3. Keep only relevant columns.
    4. Drop rows with NA and duplicates.

    Args:
        df (pd.DataFrame): Raw DataFrame to clean.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    rename_dict: dict[str, str] = {
        "date_mutation": "transaction_date",
        "valeur_fonciere": "property_value",
        "code_postal": "postal_code",
        "commune": "town_name",
        "code_departement": "department_code",
        "code_commune": "town_code",
        "code_type_local": "property_type_code",
        "type_local": "property_type",
        "surface_reelle_bati": "building_area",
        "nombre_pieces_principales": "main_rooms",
        "surface_terrain": "land_area",
    }

    df.columns = df.columns.str.lower().str.strip()
    df = df.rename(columns=rename_dict)

    cols_to_keep: list[str] = [v for v in rename_dict.values() if v in df.columns]
    df = df[cols_to_keep]

    df = df.dropna().drop_duplicates()
    return df


class TestCleanData:
    """
    Unit tests for the `_clean_df` function.

    Checks:
    1. Columns are renamed according to the mapping and extra columns are removed.
    2. Rows containing NA values are dropped.
    3. Duplicate rows are removed.
    """

    def test_column_rename_and_filter(self) -> None:
        """
        Scenario: Columns should be renamed according to the mapping and extra columns removed.
        """
        df: pd.DataFrame = pd.DataFrame({"DATE_MUTATION": ["01/01/2024"], "valeur_fonciere": [1000000], "extra_col": ["to_remove"]})
        cleaned: pd.DataFrame = _clean_df(df)

        # Check renaming
        assert "transaction_date" in cleaned.columns
        assert "property_value" in cleaned.columns
        # Check extra column removed
        assert "extra_col" not in cleaned.columns

    def test_drop_na(self) -> None:
        """
        Scenario: Rows containing NA values should be dropped.
        """
        df: pd.DataFrame = pd.DataFrame({"date_mutation": ["01/01/2024", None], "valeur_fonciere": [1000000, 2000000]})
        cleaned: pd.DataFrame = _clean_df(df)

        # Rows with NA should be removed
        n_rows: int = cleaned.shape[0]
        assert n_rows == 1
        assert cleaned["transaction_date"].iloc[0] == "01/01/2024"

    def test_drop_duplicates(self) -> None:
        """
        Scenario: Duplicate rows should be removed.
        """
        df: pd.DataFrame = pd.DataFrame({"date_mutation": ["01/01/2024", "01/01/2024"], "valeur_fonciere": [1000000, 1000000]})
        cleaned: pd.DataFrame = _clean_df(df)

        # Duplicate row removed
        n_rows: int = cleaned.shape[0]
        assert n_rows == 1
