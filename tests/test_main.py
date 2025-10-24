import pandas as pd

from fpi.analysis.explore import load_data, preprocess


# --- Test load_data ---
def test_load_data():
    df = load_data("data/raw/sample2024.txt")
    # Check it's a DataFrame
    assert isinstance(df, pd.DataFrame)
    # Check expected columns exist
    assert "Valeur fonciere" in df.columns


# --- Test preprocess ---
def test_preprocess():
    df = load_data("data/raw/sample2024.txt")
    df_clean = preprocess(df)
    # Check column names are translated
    expected_cols = ["land_value", "postal_code", "building_surface", "mutation_date", "land_surface", "main_rooms"]
    assert list(df_clean.columns) == expected_cols
    # Check shape hasn't increased
    assert df_clean.shape[0] == df.shape[0]


# --- Test save_hist
def test_save_hist(tmp_path):
    # tmp_path est un dossier temporaire fourni par pytest
    df = pd.DataFrame({"building_surface": [50, 100, 70], "land_surface": [200, 500, 300], "main_rooms": [2, 3, 4]})
    from fpi.analysis.utils_plot import save_hist

    save_hist(df, ["building_surface", "land_surface", "main_rooms"], output_dir=tmp_path)
    # Check files exist
    for col in ["building_surface", "land_surface", "main_rooms"]:
        assert (tmp_path / f"{col}_hist.png").exists()

def test_save_lv(tmp_path):
    from src.analysis.utils_plot import save_lv

    df = pd.DataFrame({
        "land_value": ["100000", "250000", "500000", "NaN", "750000€", "1 000 000"]
    })

    save_lv(df, "land_value", output_dir=tmp_path)

    # Check the PNG file was created
    assert (tmp_path / "land_value_boxplot.png").exists()