"""
Home page subdivision of the interface subpackage.

### `home_page`
Provides the homepage layout with hero section, search, and feature cards.

- `get_home_page()`: Returns homepage Gradio components (dropdowns and buttons).
"""

from .home.home_page import get_home_page

__all__: list[str] = [
    "get_home_page",
]
