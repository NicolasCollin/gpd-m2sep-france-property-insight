"""
Data processing utilities for the FPI application.

This subpackage contains the full pipeline used to transform the DVF dataset
from raw text files into analysis-ready tables and machine-learning inputs.

## Features

- Data loading
- Data cleaning, normalization, processing
- Data validation schemas with Pydantic
- Data conversion: from csv to SQLite .db files

### `clean_data`
Tools for transforming raw DVF CSV files into standardized, consistent,
machine-readable files.
Includes:
- converting column names to lowercase
- extracting relevant fields
- removing duplicates and missing values
- normalizing decimal formats
- saving year-organized cleaned datasets

### `loader`
Utilities for loading all cleaned CSV files into a single DataFrame, ensuring
numeric columns are parsed correctly and corrupted rows are handled gracefully.

### `process_data`
Transforms cleaned data into an analysis-ready structure. Operations include:
- extracting the transaction year
- filtering only "Vente" rows
- dropping unused identifiers
- saving processed files into year-based folders

### `schemas`
Pydantic models defining strict, validated structures for both:
- user inputs from the prediction form
- individual cleaned DVF rows used for prediction

### `txt_to_sqlite`
A utility for converting text-based DVF extracts into SQLite databases with
automatic chunked loading and name sanitization.


## Functions definition
"""

from .clean_data import clean_data
from .loader import load_all_csv
from .process_data import process_data
from .schemas import PredictionFormSchema, PropertyData
from .txt_to_sqlite import txt_to_sqlite

__all__: list[str] = [
    "clean_data",
    "load_all_csv",
    "process_data",
    "PredictionFormSchema",
    "PropertyData",
    "txt_to_sqlite",
]
