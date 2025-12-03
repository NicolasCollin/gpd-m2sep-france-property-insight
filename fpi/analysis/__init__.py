"""
Analysis subpackage of the FPI application.

This subpackage contains all analytical tools used across the project.

## Features

- Statistical summaries
- Descriptive statistics
- Visualizations for dashboards
- Historical trend plots
- Price computation utilities
- A full exploratory data analysis pipeline

## Submodules

### `plots`
Low-level plotting utilities based on Matplotlib and Seaborn.

- `display_trend`: saves price evolution plots (region and department)
- Helper functions for cleaning and formatting values

### `dashboard`
Plot-building utilities designed for the Gradio dashboard interface.

- `plot_sales_count_by_department`
- `plot_price_evolution_by_department`

### `stats`
Statistical helpers for inspecting and understanding datasets.

- `summary`: quick printed overview
- `compute_descriptive_statistics`: formatted statistics and CSV exports
- `get_summary_data`: metadata extractor for tests

### `price`
Price-related computation utilities.

- `compute_price_per_sqm`

## Functions definitions
"""

# import shortcuts
from .dashboard import (
    plot_price_evolution_by_department,
    plot_sales_count_by_department,
)
from .market_analysis import (
    calculate_financing_simulation,
    calculate_market_metrics,
    create_sales_by_property_type_plot,
    filter_data_by_location,
    get_location_choices,
    get_sales_by_type_data,
)
from .plots import display_trend
from .price import compute_price_per_sqm
from .stats import (
    compute_descriptive_statistics,
    get_summary_data,
    summary,
)

__all__: list[str] = [
    # Dashboard plotting
    "plot_sales_count_by_department",
    "plot_price_evolution_by_department",
    # Market analysis
    "get_location_choices",
    "filter_data_by_location",
    "calculate_market_metrics",
    "create_sales_by_property_type_plot",
    "get_sales_by_type_data",
    "calculate_financing_simulation",
    # Trend plots
    "display_trend",
    # Statistics
    "summary",
    "compute_descriptive_statistics",
    "get_summary_data",
    # Price computation
    "compute_price_per_sqm",
]
