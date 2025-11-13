from fpi.data_pipeline.loader import load_all_csv


def build_postal_town_mapping(df_root: str = "data/cleaned") -> dict[str, str]:
    """
    Build a mapping from postal codes to town names.

    Args:
        df_root (str): Path to the cleaned data directory.

    Returns:
        dict[str, str]: Mapping from postal code to town name.
    """
    df = load_all_csv(df_root)

    if "postal_code" not in df.columns or "town_name" not in df.columns:
        raise KeyError("Columns 'postal_code' and 'town_name' must exist in the dataset.")

    df = df.dropna(subset=["postal_code", "town_name"])
    df["postal_code"] = df["postal_code"].astype(str).str.zfill(5)

    # Keep the first town name for each postal code
    mapping = df.drop_duplicates(subset=["postal_code"]).set_index("postal_code")["town_name"].to_dict()
    return mapping


def suggest_postal_code(value: str, mapping: dict[str, str]) -> list[str]:
    """
    Suggest postal codes based on partial input.

    Args:
        value (str): Partial user input.
        mapping (dict[str, str]): Postal code → town name mapping.

    Returns:
        list[str]: List of matching postal code + town strings.
    """
    value = value.strip().lower()
    return [f"{code} - {town}" for code, town in mapping.items() if value in code or value in town.lower()]


def suggest_town(postal_code: str, value: str, mapping: dict[str, str]) -> list[str]:
    """
    Suggest towns within a postal code based on partial input.

    Args:
        postal_code (str): Selected postal code.
        value (str): Partial town name.
        mapping (dict[str, str]): Postal code → town name mapping.

    Returns:
        list[str]: Matching town names.
    """
    postal_code = str(postal_code).zfill(5)
    value = value.strip().lower()
    town = mapping.get(postal_code, "")
    return [town] if value in town.lower() else []
