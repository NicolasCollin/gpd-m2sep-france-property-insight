from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator


class PropertyData(BaseModel):
    """
    Data model representing a single validated property transaction row.

    Each attribute corresponds to a column in the cleaned CSV dataset and
    includes constraints to ensure data validity and consistency.

    Attributes:
        - property_value (float): Property sale price, must be positive.
        - postal_code (int): 5-digit French postal code.
        - department_code (int): Department numeric code (1 to 976).
        - town_code (int): Municipality code, positive integer.
        - property_type_code (int): Type of property (1 to 4).
        - building_area (float): Built area in m², non-negative.
        - main_rooms (float): Number of main rooms, non-negative.
        - land_area (float): Land area in m², non-negative.
    """

    property_value: float = Field(..., gt=0)
    postal_code: int = Field(..., ge=1000, le=99999)
    department_code: int = Field(..., ge=1, le=976)
    town_code: int = Field(..., gt=0)
    property_type_code: int = Field(..., ge=1, le=4)
    building_area: float = Field(..., ge=0)
    main_rooms: float = Field(..., ge=0)
    land_area: float = Field(..., ge=0)

    @field_validator("property_value", mode="before")
    def convert_european_number(cls, v: Any) -> float:
        """
        Convert strings like '200000,00' to a float using European decimal commas.
        """
        if isinstance(v, str):
            v = v.replace(",", ".")
        try:
            return float(v)
        except Exception:
            raise ValueError(f"Invalid property_value: {v}")

    @field_validator("postal_code", mode="before")
    def normalize_postal_code(cls, v: Any) -> int:
        """
        Convert postal code to integer if it was parsed as float.
        """
        if isinstance(v, float):
            return int(v)
        return v


def validate_csv(csv_path: str | Path, save_invalid: bool = True) -> List[PropertyData]:
    """
    Validate all rows of a cleaned CSV file using the PropertyData model.

    Each row is checked for correct data types, value ranges, and format consistency.
    Invalid rows are displayed in detail (row index, column names, and values)
    and optionally exported to a separate CSV file for further inspection.

    Args:
        - csv_path (str | Path):
            Path to the input CSV file containing property data.
        - save_invalid (bool):
            Whether to save invalid rows in a separate file (`invalid_rows.csv`).
            Defaults to True.

    Returns:
        - List[PropertyData]:
            A list of validated PropertyData instances (one per valid row).

    Output:
        - Prints detailed validation errors to console.
        - Optionally creates an `invalid_rows.csv` in the same folder.
        - Displays validation summary with the number of valid rows.
    """
    csv_path_obj: Path = Path(csv_path)
    print(f"\nValidating file: {csv_path_obj.resolve()}")

    df: pd.DataFrame = pd.read_csv(csv_path_obj, sep=",", low_memory=False)
    valid_rows: List[PropertyData] = []
    invalid_entries: List[Dict[str, Any]] = []

    for i, row in df.iterrows():
        # i: int = row index
        # row: pd.Series = row data
        row_dict: Dict[str, Any] = row.to_dict()
        try:
            record: PropertyData = PropertyData(**row_dict)
            valid_rows.append(record)
        except ValidationError as e:
            error_info: Dict[str, Any] = {
                "row_index": i,
                "errors": [err["loc"][0] for err in e.errors()],
                "values": {field: row[field] for field in e.errors()[0]["loc"] if field in row},
            }
            invalid_entries.append({**row_dict, "error_columns": error_info["errors"]})
            print(f"\nRow {i} invalid ({', '.join(error_info['errors'])})\n" f"\tValues: {error_info['values']}")

    total_rows: int = len(df)
    valid_count: int = len(valid_rows)
    print(f"\n{valid_count}/{total_rows} rows successfully validated.")

    if save_invalid and invalid_entries:
        invalid_df: pd.DataFrame = pd.DataFrame(invalid_entries)
        out_path: Path = csv_path_obj.parent / "invalid_rows.csv"
        invalid_df.to_csv(out_path, index=False)
        print(f"Invalid rows saved to: {out_path.resolve()}")

    return valid_rows


if __name__ == "__main__":
    validated_data: List[PropertyData] = validate_csv("data/cleaned/cleaned2024/cleaned_75_2024.csv")
