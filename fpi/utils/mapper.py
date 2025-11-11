from fpi.data_pipeline.loader import load_all_csv
from fpi.utils.constants import DEPT_NAMES


def suggest_department(value: str) -> list[str]:
    """
    Suggest department codes or names based on partial user input.

    Args:
        value (str): Partial input entered by the user (code or name).

    Returns:
        list[str]: A list of matching suggestions formatted as 'code - name'.

    Examples:
        >>> suggest_department("75")
        ['75 - Paris']
        >>> suggest_department("par")
        ['75 - Paris']
        >>> suggest_department("9")
        ['91 - Essonne', '92 - Hauts-de-Seine', '93 - Seine-Saint-Denis', '94 - Val-de-Marne', '95 - Val-d’Oise']
    """
    value = value.strip().lower()
    suggestions = []

    for code, name in DEPT_NAMES.items():
        if value in code or value in name.lower():
            suggestions.append(f"{code} - {name}")

    return suggestions


def get_dept_town_mapping(df_root: str = "data/cleaned") -> dict[str, list[str]]:
    """
    Build a mapping between department codes and the list of towns within each department.

    The function loads all cleaned CSV files using `load_all_csv`, extracts
    the relevant columns (`department_code`, `town_name`), and constructs a
    dictionary mapping each department code to a sorted list of unique town names.

    Args:
        data_root (str): Root directory containing yearly cleaned data folders.

    Returns:
        Dict[str, List[str]]: A dictionary mapping department codes (as strings)
        to sorted lists of corresponding town names.
    """
    df = load_all_csv(df_root)

    if "department_code" not in df.columns or "town_name" not in df.columns:
        raise KeyError("Columns 'department_code' and 'town_name' must exist in the dataset.")

    df = df.dropna(subset=["department_code", "town_name"])
    df["department_code"] = df["department_code"].astype(str).str.zfill(2)

    dept_town_map: dict[str, list[str]] = (
        df.groupby("department_code")["town_name"].unique().apply(lambda towns: sorted(towns.tolist())).to_dict()
    )

    return dept_town_map


def suggest_town(department_code: str, value: str, mapping: dict[str, list[str]]) -> list[str]:
    """
    Suggest towns based on partial input and a selected department.

    Examples:
        >>> suggest_town("75", "saint", mapping)
        ['Saint-Mandé', 'Saint-Ouen-sur-Seine', 'Saint-Denis']

    Args:
        department_code (str): Department code selected by the user.
        value (str): Partial name of the town.
        mapping (Dict[str, List[str]]): Department-to-towns mapping.

    Returns:
        List[str]: List of matching towns.
    """
    department_code = str(department_code).zfill(2)
    value = value.strip().lower()
    towns = mapping.get(department_code, [])

    return [town for town in towns if value in town.lower()]
