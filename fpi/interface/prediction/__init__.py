"""
## Prediction subdivision of the interface subpackage.

### `form`
Input form utilities and validation for property price estimation.

- `get_form()`: Returns form components for property estimation.
- `reset_form()`: Returns default values to reset the form.
- `validate_inputs()`: Validates form input values.

### `prediction_page`
Prediction page layout and callbacks for the price estimation model.

- `get_prediction_page()`: Returns Gradio layout for the prediction page.
- `run_prediction()`: Function to perform a property price prediction.


"""

from .form import get_form, reset_form, validate_inputs
from .prediction_page import get_prediction_page, run_prediction

__all__: list[str] = [
    # Prediction
    "get_prediction_page",
    "run_prediction",
    # Form utilities
    "get_form",
    "reset_form",
    "validate_inputs",
]
