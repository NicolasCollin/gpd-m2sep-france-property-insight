from typing import List, Any
import gradio as gr
import re  # For basic security/format validation


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
    This function performs basic security and validation checks on raw form inputs.

    Args:
        postal: Postal code (string).
        dept: Department code (string).
        town_code: Town code (string).
        prop_type: Property type ("House" / "Apartment").
        area: Living area in square meters (float).
        rooms: Number of rooms (integer).
        land: Land area in square meters (float).

    Returns:
        An error message string if validation fails, otherwise an empty string.
    """
    
    # Check for required fields (mandatory fields)
    required_fields: dict = {
        "Postal code": postal, 
        "Department code": dept, 
        "City": town, 
        "Living area": area, 
        "Number of rooms": rooms, 
        "Land area": land
    }
    
    for name, value in required_fields.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"Error : this field '{name}' is required."
    
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
    if not (isinstance(postal, str) and re.fullmatch(r"^\d{5}$", postal.strip())):
        return "Error : postal code must be a 5-digit number."

    return "" # Validation successful


# ==============================================================================
# FORM 
# ==============================================================================

def form() -> tuple[List[gr.components.Component], gr.Dropdown]:
    """
    Creates the Gradio input form structure for property estimation.

    Returns:
        A tuple containing:
        1. inputs_list: An ordered list of all input components (excluding prop_type).
        2. prop_type_input: The Dropdown component, returned separately for clarity.
    """

    # --- LOCATION ---
    with gr.Row():
        postal_input = gr.Textbox(label="Postal code", placeholder="Ex: 75001", lines=1, interactive=True)
        dept_code_input = gr.Textbox(label="Department code", placeholder="Ex: 75 ou 974", lines=1, interactive=True)
        town_code_input = gr.Textbox(label="Town code", placeholder="Ex: 75101", lines=1, interactive=True)

    # --- CHARACTERISTICS ---
    with gr.Row():
        prop_type_input = gr.Dropdown(
            label="Property type",
            choices=["House", "Apartment"],
            value="House"
        )
        area_input = gr.Number(label="Living area (m²)", minimum=1, step=1)
        rooms_input = gr.Number(label="Number of rooms", minimum=1, step=1)
        land_input = gr.Number(label="Land area (m²)", minimum=0, step=1)

    inputs_list: List[gr.components.Component] = [
        postal_input, dept_code_input, town_code_input, prop_type_input, area_input, rooms_input, land_input
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
    return [
        None,         # 1. postal
        None,         # 2. dept
        None,         # 3. town
        "House",      # 4. prop_type (Dropdown default value)
        None,         # 5. area
        None,         # 6. rooms
        None,         # 7. land
        ""            # 8. result_output (empty string)
    ]


    