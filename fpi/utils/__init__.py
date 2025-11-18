"""
Utility functions and constants for the FPI application.

This subpackage contains general-purpose helpers and shortcuts used across
the France Property Insight (FPI) project, including CLI commands, display
formatting, constant definitions, and data mappings.

## Features

- Command-line shortcuts for project management and development
- Standardized constants for data processing and machine learning
- Formatting functions for user-friendly variable display
- Utilities for mapping postal codes to town names and providing suggestions

### `aliases`
Provides shortcut functions for frequent CLI tasks:
- Running pre-commit hooks
- Launching the app in Docker
- Performing type checks, audits, and tests
- Generating API documentation with pdoc
- Simulating the CI pipeline

### `constants`
Holds all standard constants used across the project:
- File paths for processed and cleaned data
- Lists of variables to keep for cleaning and prediction
- Numeric and categorical input definitions for ML models
- Department names and ML pipeline configurations

### `display_case`
Functions for formatting variable names into user-friendly display strings.
- Converts `snake_case` or `camelCase` to readable capitalized text

## Functions definitions
"""

from .display_case import format_display_name

__all__: list[str] = [
    "format_display_name",
]
