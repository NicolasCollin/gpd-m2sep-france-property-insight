"""
Interface subpackage of the FPI application.

This subpackage contains all modules related to the Gradio-based user interface.

## Submodules

### `dashboard_page`
Provides functions to render the dashboard page with tables and visualizations.

- `get_dashboard_page()`: Returns a complete Gradio Blocks layout for the dashboard.

### `home_page`
Provides the homepage layout with hero section, search, and feature cards.

- `get_home_page()`: Returns homepage Gradio components (dropdowns and buttons).

### `form`
Input form utilities and validation for property price estimation.

- `get_form()`: Returns form components for property estimation.
- `reset_form()`: Returns default values to reset the form.
- `validate_inputs()`: Validates form input values.

### `prediction_page`
Prediction page layout and callbacks for the price estimation model.

- `get_prediction_page()`: Returns Gradio layout for the prediction page.
- `run_prediction()`: Function to perform a property price prediction.

### `menu`
Main navigation and full app layout.

- `app_menu()`: Returns the complete Gradio interface with header, pages, and navigation logic.
- `show_page(page_id)`: Utility to switch visible pages.

"""

# Import submodules
from .dashboard.dashboard_page import get_dashboard_page
from .home.home_page import get_home_page
from .menu import app_menu, show_page
from .prediction.form import get_form, reset_form, validate_inputs
from .prediction.prediction_page import get_prediction_page, run_prediction

# Define __all__ for clean imports
__all__: list[str] = [
    # Menu / app layout
    "app_menu",
    "show_page",
    # Dashboard
    "get_dashboard_table",
    "display_dashboard",
    "get_dashboard_page",
    # Home
    "get_home_page",
    # Prediction
    "get_prediction_page",
    "run_prediction",
    # Form utilities
    "get_form",
    "reset_form",
    "validate_inputs",
]
