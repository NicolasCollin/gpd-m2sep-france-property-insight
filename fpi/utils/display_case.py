import re


def format_display_name(var_name: str) -> str:
    """
    Convert variable names with underscores or camelCase to a display-friendly format.

    Args:
        - var_name (str): name to format

    Returns:
        formatted name ready for display

    Example:
        >>> format_display_name("property_value")
        'Property value'
        >>> format_display_name("yearBuilt")
        'Year built'
    """
    if not var_name:
        return ""
    var_name = re.sub(r"([a-z])([A-Z])", r"\1 \2", var_name)  # handle camelCase
    return var_name.replace("_", " ").strip().capitalize()
