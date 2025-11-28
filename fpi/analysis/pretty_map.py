"""
Generate an interactive choropleth map for real-estate data in Île-de-France.

This script:
1. Downloads the Île-de-France GeoJSON 
2. calls load_all_csv function from fpi.data_pipeline.loader
3. Aggregates real-estate data by town (mean property value)
4. Merges the aggregated data with the GeoJSON
5. Produces a Plotly choropleth map ready for use in Gradio
"""

from __future__ import annotations

import json
from pathlib import Path
import requests
import pandas as pd
import plotly.express as px
from fpi.data_pipeline.loader import load_all_csv


GEO_URL = (
    "https://github.com/gregoiredavid/france-geojson/tree/"
    "master/regions/ile-de-france/departements-ile-de-france.geojson"
)

GEO_PATH = Path("data/geo/ile_de_france_communes.geojson")



def download_geojson(path: Path = GEO_PATH, url: str = GEO_URL) -> Path:
    """
    Download the Île-de-France GeoJSON file as it does'nt exist in our dataset.

    Args:
        path: Local path where the GeoJSON should be stored.
        url: URL of the GeoJSON file on GitHub.

    Returns:
        Path to the downloaded or existing GeoJSON file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        print(f"GeoJSON already present: {path}")
        return path

    print(f"Downloading GeoJSON from {url} ...")
    response = requests.get(url)
    response.raise_for_status()
    path.write_bytes(response.content)

    print(f"GeoJSON saved at: {path}")
    return path


def load_geojson(path: Path = GEO_PATH) -> dict:
    """
    Load the GeoJSON file into a Python dictionary.

    Args:
        path: Path to the GeoJSON file.

    Returns:
        Dictionary containing geometries.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_property_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute mean property value per commune.

    Args:
        df: DVF dataset containing columns:
            - 'property_value'
            - 'town_code'

    Returns:
        DataFrame with aggregated mean values per town_code.
    """
    grouped = (
        df.groupby("town_code", as_index=False)
        .agg(mean_value=("property_value", "mean"),
             count=("property_value", "size"))
    )
    return grouped


def create_choropleth(agg_df: pd.DataFrame, geojson: dict):
    """
    Create a Plotly choropleth map using aggregated DVF data and the GeoJSON.

    Args:
        agg_df: Aggregated DVF data per town_code.
        geojson: GeoJSON geometry dictionary.

    Returns:
        A Plotly figure object.
    """
    fig = px.choropleth(
        agg_df,
        geojson=geojson,
        locations="town_code",
        featureidkey="postal_code",  # check if matches GeoJSON structure
        color="mean_value",
        hover_name="town_code",
        hover_data={"mean_value": True, "count": True},
        title="Mean Property Value – Île-de-France",
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

    return fig


def save_map(fig, path: str = "idf_map.html") -> None:
    """
    Save the generated map as an HTML file.

    Args:
        fig: Plotly figure.
        path: Output HTML file path.
    """
    fig.write_html(path)
    print(f"Map saved at {path}")



def generate_idf_map() -> None:
    """
    Full pipeline:
    1. Download & load GeoJSON
    2. Load raw DVF data
    3. Aggregate by town
    4. Build map
    5. Save to HTML + return figure
    """
    # Geo
    geo_path = download_geojson()
    geojson = load_geojson(geo_path)

    # load data
    df = load_all_csv()

    # Aggregate property values
    agg = aggregate_property_values(df)

    # Generate figure
    fig = create_choropleth(agg, geojson)

    # Save for debugging / external usage
    save_map(fig)

    return fig
