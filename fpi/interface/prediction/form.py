import re

import gradio as gr

from fpi.data_pipeline.schemas import PredictionFormSchema


def validate_inputs(
    postal: str,
    dept: str,
    town: str,
    prop_type: str,
    area: float,
    rooms: int,
    land: float,
) -> str:
    """Performs basic validation on raw form inputs."""

    required_fields: dict[str, str | float | int | None] = {
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

    try:
        if area <= 0 or area > 1000:
            return "Error : Living area must be positive and realistic (max 1000 m²)."
        if rooms <= 0 or rooms > 50:
            return "Error : Number of rooms must be positive and realistic (max 50)."
        if land < 0 or land > 100000:
            return "Error : Land area must be positive and realistic (max 10 hectares)."
    except (ValueError, TypeError):
        return "Error : Please enter valid numbers for areas and rooms."

    if not re.fullmatch(r"^\d{5}$", postal.strip()):
        return "Error : postal code must be a 5-digit number."

    return ""


def get_form() -> tuple[list[gr.components.FormComponent], gr.Dropdown]:
    """Creates the Gradio input form structure for property estimation."""
    with gr.Row():
        postal_input = gr.Textbox(label="Postal code", placeholder="Ex: 75001", lines=1, interactive=True)
        dept_code_input = gr.Textbox(label="Department code", placeholder="Ex: 75 ou 974", lines=1, interactive=True)
        town_code_input = gr.Textbox(label="Town code", placeholder="Ex: 75101", lines=1, interactive=True)

    with gr.Row():
        prop_type_input = gr.Dropdown(label="Property type", choices=["House", "Apartment"], value="House")
        area_input = gr.Number(label="Living area (m²)", minimum=1, step=1)
        rooms_input = gr.Number(label="Number of rooms", minimum=1, step=1)
        land_input = gr.Number(label="Land area (m²)", minimum=0, step=1)

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


def reset_form() -> PredictionFormSchema:
    """Return a new PredictionFormSchema with default values."""
    return PredictionFormSchema(postal="", dept="", town="", area=0.0, rooms=0, land=0.0)
