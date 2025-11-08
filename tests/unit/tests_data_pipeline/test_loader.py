from pathlib import Path

import pandas as pd
import pytest

from fpi.data_pipeline.loader import load_all_csv


@pytest.fixture
def tmp_csv_dir(tmp_path: Path) -> Path:
    """
    Creates a temporary folder with a few cleaned CSV files for testing load_all_csv.

    Returns:
        Path: Path to the temporary root folder containing the CSV files.
    """
    # CSV 1
    df1 = pd.DataFrame(
        {
            "transaction_date": ["01/01/2024", "02/01/2024"],
            "property_value": ["1000000,00", "2000000,00"],
            "postal_code": [75001, 75001],
            "department_code": ["75", "75"],
            "town_code": [101, 101],
            "property_type_code": [1, 1],
            "property_type": ["Appartement", "Appartement"],
            "building_area": [50, 70],
            "main_rooms": [2, 3],
            "land_area": [0, 0],
        }
    )
    csv1 = tmp_path / "cleaned2024" / "cleaned_XX_XXXX.csv"
    csv1.parent.mkdir(parents=True, exist_ok=True)
    df1.to_csv(csv1, index=False, decimal=",")

    # CSV 2
    df2 = pd.DataFrame(
        {
            "transaction_date": ["03/01/2024"],
            "property_value": ["1500000,00"],
            "postal_code": [75002],
            "department_code": ["75"],
            "town_code": [102],
            "property_type_code": [2],
            "property_type": ["Appartement"],
            "building_area": [60],
            "main_rooms": [2],
            "land_area": [0],
        }
    )
    csv2 = tmp_path / "cleaned2023" / "cleaned_YY_YYYY.csv"
    csv2.parent.mkdir(parents=True, exist_ok=True)  # <- Make sure directory exists
    df2.to_csv(csv2, index=False, decimal=",")

    return tmp_path


def test_load_all_csv(tmp_csv_dir: Path) -> None:
    """
    Test that load_all_csv correctly loads and concatenates multiple CSV files,
    converts numeric columns, and handles the French decimal format.
    """
    df = load_all_csv(data_root=str(tmp_csv_dir))

    # Basic checks
    assert not df.empty
    assert df.shape[0] == 3  # 2 rows + 1 row
    assert "property_value" in df.columns

    # Check conversion to numeric
    assert pd.api.types.is_float_dtype(df["property_value"])
    assert df["property_value"].iloc[0] == 1500000.0
    assert df["property_value"].iloc[1] == 1000000.0

    # Check department codes is parsed properly
    assert df["department_code"].iloc[0] == 75
