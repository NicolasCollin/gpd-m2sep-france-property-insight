import pandas as pd
import pytest


@pytest.fixture
def df_dvf() -> pd.DataFrame:
    """
    Fixture providing a synthetic DVF-like dataset for testing visualizations.
    Can be used by multiple test classes across the test suite.

    Returns:
        pd.DataFrame: Sample cleaned DVF dataset
    """
    data: dict[str, list] = {
        "transaction_date": [
            "05/01/2024",
            "19/01/2024",
            "19/01/2024",
            "19/01/2024",
            "19/01/2024",
        ],
        "property_value": [
            "1350000,00",
            "2865000,00",
            "2865000,00",
            "2865000,00",
            "2865000,00",
        ],
        "postal_code": [75020.0, 75002.0, 75002.0, 75002.0, 75002.0],
        "town_name": ["PARIS 20", "PARIS 02", "PARIS 02", "PARIS 02", "PARIS 02"],
        "department_code": ["75", "75", "75", "75", "75"],
        "town_code": [120, 102, 102, 102, 102],
        "property_type_code": [4.0, 4.0, 2.0, 2.0, 2.0],
        "property_type": [
            "Local industriel. commercial ou assimilé",
            "Local industriel. commercial ou assimilé",
            "Appartement",
            "Appartement",
            "Appartement",
        ],
        "building_area": [135.0, 27.0, 43.0, 44.0, 107.0],
        "main_rooms": [0.0, 0.0, 2.0, 2.0, 5.0],
        "land_area": [124.0, 69.0, 69.0, 69.0, 69.0],
    }

    return pd.DataFrame(data)
