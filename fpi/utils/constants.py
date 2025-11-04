"""
Constants used across the property prediction pipeline.
Includes variables to keep, numeric columns, and ML config.
"""

from typing import List

# Columns to keep in cleaned CSV / processed data
VARS_TO_KEEP: List[str] = [
    "property_value",
    "postal_code",
    "department_code",
    "town_code",
    "property_type_code",
    "building_area",
    "main_rooms",
    "land_area",
]

# Numeric columns for preprocessing and modeling
NUMERIC_VARS: List[str] = [
    "property_value",
    "building_area",
    "main_rooms",
    "land_area",
]

# ML pipeline constants
DEFAULT_TEST_SIZE: float = 0.3
RANDOM_STATE: int = 42
