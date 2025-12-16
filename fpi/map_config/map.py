import folium
import geopandas as gpd
import gradio as gr
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster

from fpi.map_config.geocoding import geocode_address


def aggregate_properties(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregate properties to reduce the number of points to geocode.
    Rules: same transaction date, address, property value and land area.

    Args:
        df(pd.DataFrame): Original DataFrame with property transactions.

    Returns:
        df_agg(pd.DataFrame): Aggregated DataFrame.

    """
    df_map: pd.DataFrame = df.copy()

    df_map["address"] = (
        df_map["street_number"].astype(str).str.strip()
        + " "
        + df_map["street_type"].str.strip()
        + " "
        + df_map["street_name"].str.strip()
        + ", "
        + df_map["postal_code"].astype(str).str.strip()
        + " "
        + df_map["town_name"].str.strip()
        + ", FRANCE"
    )

    df_map["property_value"] = pd.to_numeric(df_map["property_value"], errors="coerce")
    df_map["building_area"] = pd.to_numeric(df_map["building_area"], errors="coerce")
    df_map["land_area"] = pd.to_numeric(df_map["land_area"], errors="coerce")

    group_cols: list = ["transaction_date", "address", "property_value", "land_area", "property_type"]

    agg_df: pd.DataFrame = df_map.groupby(group_cols, as_index=False).agg(
        building_total=("building_area", "sum"),
        nb_lots=("building_area", "count"),
        property_value=("property_value", "first"),
        transaction_date=("transaction_date", "first"),
        main_rooms=("main_rooms", "first") if "main_rooms" in df.columns else ("property_value", "first"),
        property_type=("property_type", "first")
        if "property_type" in df.columns
        else (("transaction_type", "first") if "transaction_type" in df.columns else ("property_value", "first")),
    )

    total_area = agg_df["building_total"] + agg_df["land_area"].replace(0, np.nan).fillna(0)
    agg_df["price_m2"] = agg_df["property_value"] / total_area
    agg_df["price_m2"] = agg_df["price_m2"].replace([np.inf, -np.inf], np.nan)

    print(f"Aggregated address: {len(df_map)} → {len(agg_df)} address ({(1 - len(agg_df)/len(df_map))*100:.1f}%)")

    return agg_df


def build_map_gdf(df: pd.DataFrame) -> tuple[gpd.GeoDataFrame, list]:
    """
    Build GeoDataFrame for mapping by geocoding addresses (limited to 200 addresses).

    Args:
        df(pd.DataFrame): aggregated DataFrame.

    Returns:
        gdf(gpd.GeoDataFrame): GeoDataFrame with geometry column.
        geocoded_addresses(list): List of successfully geocoded addresses.

    """
    df_agg: pd.DataFrame = aggregate_properties(df)

    if len(df_agg) > 200:
        print(f"Limited to 200 adresses (on {len(df_agg)})")
        df_agg_sample: pd.DataFrame = df_agg.sample(n=200, random_state=42, ignore_index=True)
    else:
        df_agg_sample = df_agg

    print(f"📍 Geocoding {len(df_agg_sample)} adresses...")

    coordinates: list = []
    total: int = len(df_agg_sample)

    for i, address in enumerate(df_agg_sample["address"]):
        lat, lng = geocode_address(address)
        coordinates.append((lat, lng))
        if i % 100 == 0 and i > 0:
            print(f"  {i}/{total} geocoded")

    df_agg_sample["lat"], df_agg_sample["lng"] = zip(*coordinates)

    before_filter: int = len(df_agg_sample)
    df_agg_filter: pd.DataFrame = df_agg_sample.dropna(subset=["lat", "lng"])
    after_filter: int = len(df_agg_filter)
    print(f"✅ {after_filter}/{before_filter} geocoded successfully.")

    geocoded_addresses: list = sorted(df_agg_filter["address"].unique().tolist())

    gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(df_agg_filter, geometry=gpd.points_from_xy(df_agg_filter.lng, df_agg_filter.lat), crs="EPSG:4326")

    return gdf, geocoded_addresses


def generate_map(gdf: gpd.GeoDataFrame) -> str:
    """
    Generate a Folium map from the GeoDataFrame with property markers and popups.

    Args:
        gdf(gpd.GeoDataFrame): GeoDataFrame with geocoded properties.

    Returns:
        str: HTML representation of the Folium map.
    """
    m: folium.Map = folium.Map(location=[48.8566, 2.3522], zoom_start=10, tiles="CartoDB positron")

    marker_cluster: MarkerCluster = MarkerCluster(
        name="Properties", options={"maxClusterRadius": 80, "spiderfyOnMaxZoom": True, "showCoverageOnHover": False}
    )
    marker_cluster.add_to(m)

    for idx, row in gdf.iterrows():
        popup_html: str = f"""
        <div style="font-family: Arial; font-size: 12px; width: 250px;">
            <strong>{row['address'][:50]}...</strong>
            <hr style="margin: 5px 0;">
            <strong>💰 Price:</strong> {row['property_value']:,.0f} €<br>
            <strong>🏠 Type:</strong> {row.get('property_type', 'N/A')}<br>
            <strong>🛏️ Main rooms:</strong> {row.get('main_rooms', 'N/A')}<br>
            <strong>📅 Transaction date:</strong> {row['transaction_date']}<br>
            <strong>📏 Surface:</strong> {row.get('building_total', 0):.0f} m²<br>
            <strong>🏷️ Price/m²:</strong> {row.get('price_m2', 0):.0f} €<br>
            <strong>📦 Lots:</strong> {row.get('nb_lots', 1)}
        </div>
        """

        if "price_m2" in row and not pd.isna(row["price_m2"]):
            color = "green" if row["price_m2"] < 3000 else "orange" if row["price_m2"] < 6000 else "red"
        else:
            color = "blue"

        marker = folium.Marker(
            location=[row["lat"], row["lng"]], popup=folium.Popup(popup_html, max_width=300), icon=folium.Icon(color=color, icon="home", prefix="fa")
        )
        marker.add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    return m._repr_html_()


def create_map_with_search(df: pd.DataFrame) -> gr.Blocks:
    """
    Create a Gradio interface with an interactive map and address search.

    Args:
        df(pd.DataFrame): Original DataFrame with property transactions.

    Returns:
        gr.Blocks: Gradio Blocks interface with map and search functionality.
    """

    gdf, address_list = build_map_gdf(df)
    initial_map: str = generate_map(gdf)

    with gr.Blocks() as interface:
        gr.Markdown("# 🗺️ Île-de-France Map")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Research an address")
                address_search = gr.Dropdown(choices=address_list, label="Select an address", interactive=True, allow_custom_value=False)

                show_btn: gr.Button = gr.Button("📍 Show on map", variant="primary")
                reset_btn: gr.Button = gr.Button("🗺️ Full view")

                gr.Markdown(f"**{len(address_list)}** addresses available")
                gr.Markdown("*Click on a marker for details*")

            with gr.Column(scale=3):
                map_display = gr.HTML(initial_map, label="Interactive Map")

        def show_address(address) -> str:
            """
            Show only the selected address on the map.

            Args:
                address(str): The selected address from the dropdown.

            Returns:
                str: HTML representation of the updated Folium map.

            """
            if not address:
                return initial_map

            filtered_gdf = gdf[gdf["address"] == address]

            if not filtered_gdf.empty:
                m_filtered: folium.Map = folium.Map(
                    location=[filtered_gdf.iloc[0]["lat"], filtered_gdf.iloc[0]["lng"]], zoom_start=16, tiles="CartoDB positron"
                )

                row = filtered_gdf.iloc[0]
                popup_html: str = f"""
                <div style="font-family: Arial; font-size: 12px; width: 250px;">
                    <strong>{row['address'][:50]}...</strong>
                    <hr style="margin: 5px 0;">
                    <strong>💰 Price:</strong> {row['property_value']:,.0f} €<br>
                    <strong>🏠 Type:</strong> {row.get('property_type', 'N/A')}<br>
                    <strong>🛏️ Main rooms:</strong> {row.get('main_rooms', 'N/A')}<br>
                    <strong>📅 Transaction date:</strong> {row['transaction_date']}<br>
                </div>
                """

                folium.Marker(
                    location=[row["lat"], row["lng"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color="red", icon="home", prefix="fa"),
                ).add_to(m_filtered)

                return m_filtered._repr_html_()

            return initial_map

        show_btn.click(fn=show_address, inputs=[address_search], outputs=[map_display])

        reset_btn.click(fn=lambda: initial_map, inputs=[], outputs=[map_display])

    return interface
