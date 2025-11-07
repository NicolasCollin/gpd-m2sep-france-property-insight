"""
Constants used across the property prediction pipeline.
Includes variables to keep, numeric columns, and ML config.
"""

from pathlib import Path

PROCESSED_DATA: Path = Path("data/processed")
CLEANED_DATA: Path = Path("data/cleaned")

# Columns to keep in cleaned CSV / processed data
VARS_TO_KEEP: list[str] = [
    "transaction_date",
    "property_value",
    "postal_code",
    "town_name",
    "department_code",
    "town_code",
    "property_type_code",
    "property_type",
    "building_area",
    "main_rooms",
    "land_area",
]

# Numeric columns for preprocessing and modeling
NUMERIC_VARS: list[str] = [
    "property_value",
    "building_area",
    "main_rooms",
    "land_area",
]

DEPT_NAMES: dict[str, str] = {
    "75": "Paris",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d’Oise",
}

# ML pipeline constants
DEFAULT_TEST_SIZE: float = 0.3
RANDOM_STATE: int = 42
