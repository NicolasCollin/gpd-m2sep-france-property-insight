import re

import gradio as gr


def validate_inputs(
    postal: str,
    dept: str,
    town: str,
    prop_type: str,
    area: float,
    rooms: int,
    land: float,
) -> str:
    """
    Perform basic validation on raw property form inputs.

    This function checks that all required fields are filled, numerical values
    are realistic, and the postal code format is valid.

    Args:
        - postal (str): Postal code (5-digit string).
        - dept (str): Department code.
        - town (str): Town code.
        - prop_type (str): Type of property ("House" or "Apartment").
        - area (float): Living area in square meters.
        - rooms (int): Number of main rooms.
        - land (float): Land area in square meters.

    Returns:
        - str: Empty string if all inputs are valid, or an error message
          starting with "Error :" otherwise.
    """

    required_fields: dict[str, str | float | int | None] = {
        "Postal code": postal,
        "Department code": dept,
        "Town code": town,
        "Living area": area,
        "Number of rooms": rooms,
        "Land area": land,
    }

    # Check for missing fields
    for name, value in required_fields.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"Error : field '{name}' is required."

    # Validate numeric fields
    try:
        if area <= 0 or area > 1000:
            return "Error : Living area must be positive and realistic (max 1000 m²)."
        if rooms <= 0 or rooms > 50:
            return "Error : Number of rooms must be positive and realistic (max 50)."
        if land < 0 or land > 100000:
            return "Error : Land area must be positive and realistic (max 10 hectares)."
    except (ValueError, TypeError):
        return "Error : Please enter valid numbers for areas and rooms."

    # Validate postal code format
    if not re.fullmatch(r"^\d{5}$", postal.strip()):
        return "Error : postal code must be a 5-digit number."

    return ""


def get_form() -> tuple[list[gr.components.FormComponent], gr.Dropdown]:
    """
    Build and return the Gradio input form for property price estimation.

    The form is composed of multiple text, dropdown, and number inputs arranged
    in two rows, and is intended for integration into a Gradio `Interface` or `Blocks`.

    Returns:
        - tuple[list[gr.components.FormComponent], gr.Dropdown]:
            A tuple containing:
            1. A list of all Gradio form components in order.
            2. The property type dropdown (for convenience, often needed separately).
    """

    # Row 1: location identifiers
    with gr.Row():
        postal_input: gr.Textbox = gr.Textbox(
            label="Postal code",
            placeholder="Ex: 75001",
            lines=1,
            interactive=True,
        )
        dept_code_input: gr.Textbox = gr.Textbox(
            label="Department code",
            placeholder="Ex: 75 ou 974",
            lines=1,
            interactive=True,
        )
        town_code_input: gr.Textbox = gr.Textbox(
            label="Town code",
            placeholder="Ex: 75101",
            lines=1,
            interactive=True,
        )

    # Row 2: property characteristics
    with gr.Row():
        prop_type_input: gr.Dropdown = gr.Dropdown(
            label="Property type",
            choices=["House", "Apartment"],
            value="House",
        )
        area_input: gr.Number = gr.Number(
            label="Living area (m²)",
            minimum=1,
            step=1,
        )
        rooms_input: gr.Number = gr.Number(
            label="Number of rooms",
            minimum=1,
            step=1,
        )
        land_input: gr.Number = gr.Number(
            label="Land area (m²)",
            minimum=0,
            step=1,
        )

    inputs_list: list[gr.components.FormComponent] = [
        postal_input,
        dept_code_input,
        town_code_input,
        prop_type_input,
        area_input,
        rooms_input,
        land_input,
    ]

    return inputs_list, prop_type_input


def reset_form() -> tuple[str, str, str, str, float, int, float, str]:
    """
    Return default values for all form components and the initial output message.

    This function is typically used to reset the form state when the user
    clicks a "Reset" or "Clear" button.

    Returns:
        - tuple[str, str, str, str, float, int, float, str]:
            Default values for all form fields in this order:
            (postal, dept, town, prop_type, area, rooms, land, result_text)
    """
    postal: str = ""
    dept: str = ""
    town: str = ""
    prop_type: str = "House"
    area: float = 0.0
    rooms: int = 0
    land: float = 0.0
    result_text: str = "Estimation : **--- €**"

    return postal, dept, town, prop_type, area, rooms, land, result_text
