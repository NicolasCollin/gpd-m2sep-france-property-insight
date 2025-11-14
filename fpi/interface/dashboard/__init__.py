"""
Dashboard subdivision of the interface subpackage.

### `dashboard_page`
Provides functions to render the dashboard page with tables and visualizations.

- `get_dashboard_page()`: Returns a complete Gradio Blocks layout for the dashboard.
"""

# Import submodules
from .dashboard.dashboard_page import get_dashboard_page

__all__: list[str] = [
    "get_dashboard_page",
]
