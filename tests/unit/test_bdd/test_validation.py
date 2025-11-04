import pandas as pd
from pathlib import Path
from fpi.data_pipeline.validation import PropertyData, validate_csv

def test_propertydata_valid(tmp_path):
    """Ensure valid row passes validation."""
    data = {
        "property_value": 250000,
        "postal_code": 75001,
        "department_code": 75,
        "town_code": 101,
        "property_type_code": 2,
        "building_area": 80,
        "main_rooms": 3,
        "land_area": 0,
    }
    model = PropertyData(**data)
    assert model.property_value == 250000.0
    assert model.department_code == 75


def test_propertydata_invalid_value():
    """Invalid property_type_code should raise ValidationError."""
    from pydantic import ValidationError
    bad_data = {
        "property_value": 100000,
        "postal_code": 75001,
        "department_code": 75,
        "town_code": 101,
        "property_type_code": 99,  # <- invalid
        "building_area": 50,
        "main_rooms": 2,
        "land_area": 20,
    }
    import pytest
    with pytest.raises(ValidationError):
        PropertyData(**bad_data)


def test_validate_csv(tmp_path):
    """Run validation on a small CSV and verify outputs."""
    csv_path = tmp_path / "sample.csv"
    df = pd.DataFrame([
        # One valid line
        {"property_value": 300000, "postal_code": 75001, "department_code": 75,
         "town_code": 101, "property_type_code": 2, "building_area": 70, "main_rooms": 3, "land_area": 0},
        # One invalid line (negative area)
        {"property_value": 200000, "postal_code": 75002, "department_code": 75,
         "town_code": 102, "property_type_code": 1, "building_area": -10, "main_rooms": 2, "land_area": 0},
    ])
    df.to_csv(csv_path, index=False)

    valid_rows, total_rows, error_count = validate_csv(csv_path)
    assert total_rows == 2
    assert len(valid_rows) == 1
    assert error_count == 1

    # Check files created
    processed_dir = Path("data/processed")
    valid_file = next(processed_dir.rglob("*.valid.csv"))
    invalid_file = next(processed_dir.rglob("*.invalid.csv"))
    assert valid_file.exists()
    assert invalid_file.exists()