from typing import Optional, Union
from fpi.utils.constants import DEPT_NAMES

def get_department_info(value: Optional[Union[str, int]] = None) -> Union[str, dict]:
    """
    Return name or code of department of Île-de-France depending on a given value entry.
    - If `value` is code (e.g: "75"), return "Paris".
    - If`value` is name (e.g: "Paris"), return"75".
    - If`value` is None, return complete map.

    Args:
        value (Optional[Union[str, int]]): Code or department name.

    Returns:
        Union[str, dict]: Name, code, or complet dictionnary.
    """
    
    if value is None:
        return DEPT_NAMES  

    value_str = str(value).strip().capitalize()

    # Research by code
    if value_str in DEPT_NAMES:
        return DEPT_NAMES[value_str]

    # Research by name
    for code, name in DEPT_NAMES.items():
        if name.lower() == value_str.lower():
            return code

    # If nothing found
    raise ValueError(f" Department'{value}' not found. Use code (e.g: '75') or name (e.g: 'Paris').")
