import re  
from typing import Any, List, Tuple

import gradio as gr

# ==============================================================================
# VALIDATE INPUTS
# ==============================================================================


def validate_inputs(
    postal: str,
    dept: str,
    town: str,
    prop_type: str,
    area: float,
    rooms: int,
    land: float
) -> str:
    """
    Performs basic security and validation checks on raw form inputs.

    Returns an error message string if validation fails, otherwise an empty string.
    """

    # Check for required fields (mandatory fields)
    required_fields: dict[str, Any] = {
        "Postal code": postal,
        "Department code": dept,
        "Town code": town,
        "Living area": area,
        "Number of rooms": rooms,
        "Land area": land,
    }

    for name, value in required_fields.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"Error : field '{name}' is required."

    # Basic numeric and range checks
    try:
        if area <= 0 or area > 1000:
            return "Error : Living area must be positive and realistic (max 1000 m²)."
        if rooms <= 0 or rooms > 50:
            return "Error : Number of rooms must be positive and realistic (max 50)."
        if land < 0 or land > 100000:
            return "Error : Land area must be positive and realistic (max 10 hectares)."
    except (ValueError, TypeError):
        return "Error : Please enter valid numbers for areas and rooms."

    # Format check for Postal code (simple 5 digits check)
    postal_clean: str = postal.strip()
    if not re.fullmatch(r"^\d{5}$", postal_clean):
        return "Error : postal code must be a 5-digit number."

    return ""  # Validation successful


# ==============================================================================
# FORM
# ==============================================================================


def form() -> Tuple[List[gr.components.Component], gr.Dropdown]:
    """
    Creates the Gradio input form structure for property estimation.

    Returns:
        A tuple containing:
        1. inputs_list: An ordered list of all input components (including prop_type).
        2. prop_type_input: The Dropdown component, returned separately for clarity.
    """

    # --- LOCATION ---
    with gr.Row():
        postal_input: gr.Textbox = gr.Textbox(
            label="Postal code", placeholder="Ex: 75001", lines=1, interactive=True
        )
        dept_code_input: gr.Textbox = gr.Textbox(
            label="Department code", placeholder="Ex: 75 ou 974", lines=1, interactive=True
        )
        town_code_input: gr.Textbox = gr.Textbox(
            label="Town code", placeholder="Ex: 75101", lines=1, interactive=True
        )

    # --- CHARACTERISTICS ---
    with gr.Row():
        prop_type_input: gr.Dropdown = gr.Dropdown(
            label="Property type", choices=["House", "Apartment"], value="House"
        )
        area_input: gr.Number = gr.Number(label="Living area (m²)", minimum=1, step=1)
        rooms_input: gr.Number = gr.Number(label="Number of rooms", minimum=1, step=1)
        land_input: gr.Number = gr.Number(label="Land area (m²)", minimum=0, step=1)

    inputs_list: List[gr.components.Component] = [
        postal_input,
        dept_code_input,
        town_code_input,
        prop_type_input,
        area_input,
        rooms_input,
        land_input,
    ]

    return inputs_list, prop_type_input


# ==============================================================================
# RESET FORM
# ==============================================================================


def reset_form() -> List[Any]:
    """
    Resets all input fields and the result output component in the prediction form.

    Returns:
        A list of None or default values corresponding to the inputs and the
        result output, used by Gradio's update mechanism to clear the components.
    """
    # Order: [postal, dept, town, prop_type, area, rooms, land, result_output]
    postal_default: None = None
    dept_default: None = None
    town_default: None = None
    prop_type_default: str = "House"
    area_default: None = None
    rooms_default: None = None
    land_default: None = None
    result_output_default: str = ""

    return [
        postal_default,
        dept_default,
        town_default,
        prop_type_default,
        area_default,
        rooms_default,
        land_default,
        result_output_default,
    ]
