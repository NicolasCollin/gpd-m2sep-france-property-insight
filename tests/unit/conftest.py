from unittest.mock import MagicMock, patch

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
        "street_number": ["10", "25", "5", "7", "12"],
        "street_type": ["rue", "avenue", "boulevard", "rue", "place"],
        "street_name": ["de Paris", "des Champs-Élysées", "Saint-Germain", "de Paris", "des Champs-Élysées"],
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


@pytest.fixture
def example_input() -> dict[str, float]:
    """Standard example input dictionary for property prediction."""
    return {
        "building_area": 13.0,
        "main_rooms": 1,
        "land_area": 20.0,
        "postal_code": 75020,
        "property_type_code": 2,
        "town_code": 120,
        "department_code": 75,
    }


@pytest.fixture
def example_input_int() -> dict[str, int]:
    """Same input but with integer values instead of floats."""
    return {
        "building_area": 13,
        "main_rooms": 1,
        "land_area": 20,
        "postal_code": 75020,
        "property_type_code": 2,
        "town_code": 120,
        "department_code": 75,
    }


@pytest.fixture
def incomplete_input() -> dict[str, float]:
    """Input with one required feature missing."""
    return {
        "building_area": 13.0,
        "land_area": 20.0,
        "postal_code": 75020,
        "property_type_code": 2,
        "town_code": 120,
        "department_code": 75,
    }


@pytest.fixture
def mock_model() -> MagicMock:
    """Reusable MagicMock model."""
    return MagicMock()


@pytest.fixture
def patched_model(mock_model: MagicMock):
    """Patches joblib.load to return the mock model for the duration of the test."""
    with patch("fpi.models.predict.joblib.load", return_value=mock_model):
        yield mock_model
