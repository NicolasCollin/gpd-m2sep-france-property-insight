import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_location_choices(df: pd.DataFrame) -> list[str]:
    """
    Generate a formatted list of available location identifiers from a real-estate dataset.

    This function extracts:
        - postal codes combined with town names (e.g., "75015 - Paris")
        - department codes (e.g., "75")
    ensuring each value appears only once.

    Args:
        df (pd.DataFrame):
            DataFrame containing at least the columns:
            - "postal_code" (str or int)
            - "town_name" (str)
            - "department_code" (int)
            Additional columns are ignored.

    """
    choices: list[str] = []
    if not df.empty:
        if "postal_code" in df.columns and "town_name" in df.columns:
            towns = df[["postal_code", "town_name"]].drop_duplicates()
            choices.extend([f"{row['postal_code']} - {row['town_name']}" for _, row in towns.iterrows()])

        if "department_code" in df.columns:
            departments = df[["department_code"]].drop_duplicates()
            dept_choices = [
                str(row["department_code"])
                for _, row in departments.iterrows()
                if str(row["department_code"]) not in [c.split(" - ")[0] for c in choices]
            ]
            choices.extend(dept_choices)

    return sorted(choices)


def filter_data_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """
    Filter a property dataset to retain only rows matching a specific location.

    The function supports two formats:
        1. "postal_code - town_name"
        2. "department_code"

    Args:
        df (pd.DataFrame):
            The complete real-estate dataset.
        location (str):
            The selected location string. May be empty or None, in which case the
            original DataFrame is returned.

    Returns:
        pd.DataFrame: The filtered DataFrame containing only rows associated with
        the requested location.
    """

    # Case 0: empty location
    if location == "":
        return df
    # Case 1: "postal_code - town_name"
    if " - " in location and "postal_code" in df.columns:
        postal_code = location.split(" - ")[0].strip()
        return df[df["postal_code"].astype(str) == postal_code]

    # Case 2: department code
    if "department_code" in df.columns:
        dept_code: str = location.strip()  # leave as string
        return df[df["department_code"].astype(str) == dept_code]
    return df


def filter_data_by_criteria(
    df: pd.DataFrame,
    min_rooms: int | None = None,
    min_surface: float | None = None,
    max_surface: float | None = None,
    property_type: str | None = None,
) -> pd.DataFrame:
    """
    Filter a real-estate dataset using optional user-defined criteria.

    Supported filters:
        - Minimum number of rooms
        - Minimum surface area
        - Maximum surface area
        - Property type (e.g., "Appartement", "Maison")

    Each criterion is applied only if it is provided (not None and valid).

    Args:
        df (pd.DataFrame):
            The full real-estate dataset.
        min_rooms (int | None):
            Minimum required number of rooms. Rows with fewer rooms are excluded.
        min_surface (float | None):
            Minimum required building area in m².
        max_surface (float | None):
            Maximum allowed building area in m².
        property_type (str | None):
            Property type to keep. If None or "All", no filter is applied on type.

    Returns:
        pd.DataFrame:
            A DataFrame containing only rows that match the provided filter criteria.
    """

    df_filtered: pd.DataFrame = df.copy()

    # Coerce numeric columns
    if "main_rooms" in df_filtered.columns:
        df_filtered["main_rooms"] = pd.to_numeric(df_filtered["main_rooms"], errors="coerce")
    if "building_area" in df_filtered.columns:
        df_filtered["building_area"] = pd.to_numeric(df_filtered["building_area"], errors="coerce")

    # Filter by rooms
    if min_rooms is not None and min_rooms > 0:
        df_filtered = df_filtered[df_filtered["main_rooms"] >= min_rooms]

    # Filter by surface minimum
    if min_surface is not None and min_surface > 0:
        df_filtered = df_filtered[df_filtered["building_area"] >= min_surface]

    # Filter by surface maximum
    if max_surface is not None and max_surface > 0:
        df_filtered = df_filtered[df_filtered["building_area"] <= max_surface]

    # Filter by property type
    if property_type and property_type != "All":
        df_filtered = df_filtered[df_filtered["property_type"] == property_type]

    return df_filtered


def calculate_median_price_per_m2_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate median price per m² grouped by property type.

    Arg:
        df: pd.DataFrame

    Return:
        pd.DataFrame: a dataframe of median price per m² by property type

    """
    if df.empty or not {"property_value", "building_area", "land_area", "property_type"}.issubset(df.columns):
        return pd.DataFrame({"property_type": ["No data"], "median_price_per_m2": ["No available"]})

    df_clean: pd.DataFrame = df.copy()
    df_clean["property_value"] = pd.to_numeric(df_clean["property_value"], errors="coerce")
    df_clean["building_area"] = pd.to_numeric(df_clean["building_area"], errors="coerce")
    df_clean["land_area"] = pd.to_numeric(df_clean["land_area"], errors="coerce")
    df_clean = df_clean[
        (df_clean["building_area"] > 0)
        & (df_clean["property_value"] > 0)
        & (df_clean["land_area"] > 0)
        & (df_clean["property_value"].notna())
        & (df_clean["building_area"].notna())
        & (df_clean["land_area"].notna())
    ]

    if df_clean.empty:
        return pd.DataFrame({"property_type": ["No data"], "median_price_per_m2": ["No available"]})

    df_clean["price_m2"] = df_clean["property_value"] / (df_clean["building_area"] + df_clean["land_area"])
    median_by_type = df_clean.groupby("property_type")["price_m2"].median().reset_index()
    median_by_type.rename(columns={"price_m2": "median_price_per_m2"}, inplace=True)

    expected_types = ["Appartement", "Maison", "Local industriel. commercial ou assimilé"]
    results = []

    for t in expected_types:
        mask = median_by_type["property_type"] == t
        if mask.any():
            val = median_by_type.loc[mask, "median_price_per_m2"].iloc[0]
            results.append({"property_type": t, "median_price_per_m2": round(val, 0)})
        else:
            results.append({"property_type": t, "median_price_per_m2": "No available"})

    return pd.DataFrame(results)


def calculate_market_metrics(df: pd.DataFrame) -> dict[str, int | float | dict]:
    """
    Compute key market indicators for a given subset of real-estate transactions.

    Metrics include:
        - average price per m²
        - median sale price
        - number of transactions
        - average surface area

    Args:
        df (pd.DataFrame):
            Filtered DataFrame. Must contain:
            - "property_value"
            - "building_area"
            Optional additional columns are ignored.

    Returns:
        dict[str, float]: A dictionary with the computed metrics:
            {
                "avg_price_per_m2": float,
                "total_transactions": int,
                "median_price": float,
                "avg_surface": float
            }
    """
    if df.empty:
        return {"avg_price_per_m2": 0.0, "total_transactions": 0, "median_price": 0.0, "avg_surface": 0.0}

    df_clean: pd.DataFrame = df.copy()

    # Coerce numeric values
    if "property_value" in df_clean.columns:
        df_clean["property_value"] = pd.to_numeric(df_clean["property_value"], errors="coerce")

    if "building_area" in df_clean.columns:
        df_clean["building_area"] = pd.to_numeric(df_clean["building_area"], errors="coerce")

    total_transactions = len(df_clean)
    valid_surfaces = df_clean[df_clean["building_area"] > 0]["building_area"] if "building_area" in df_clean.columns else pd.Series([])
    avg_surface = round(valid_surfaces.mean(), 1) if not valid_surfaces.empty else 0
    median_by_type_df = calculate_median_price_per_m2_by_type(df_clean)
    median_by_type_dict = {}

    for _, row in median_by_type_df.iterrows():
        median_by_type_dict[row["property_type"]] = row["median_price_per_m2"]

    return {"total_transactions": total_transactions, "avg_surface": avg_surface, "median_price_per_m2_by_type": median_by_type_dict}


def create_sales_by_property_type_plot(df: pd.DataFrame) -> go.Figure:
    """
    Build a bar chart representing the number of real-estate transactions
    grouped by property type (e.g., house, apartment).

    Args:
        df (pd.DataFrame):
            Filtered transaction data. Must contain "property_type".

    Return:
        go.Figure: a plotly figure object representing sales by property type
    """
    if df.empty or "property_type" not in df.columns:
        fig = go.Figure()
        fig.update_layout(xaxis_title="Property type", yaxis_title="Number of sales", height=400)
        return fig

    sales_by_type: pd.DataFrame = df["property_type"].value_counts().reset_index()
    sales_by_type.columns = ["property_type", "count"]

    if not sales_by_type.empty:
        fig = px.bar(
            sales_by_type,
            x="property_type",
            y="count",
            labels={"property_type": "Property type", "count": "Number of sales"},
        )
        fig.update_traces(marker_color="darkturquoise")
    else:
        fig = go.Figure()
        fig.update_layout(xaxis_title="Property type", yaxis_title="Number of sales")

    fig.update_layout(height=400, showlegend=False)
    return fig


def create_sales_by_date_plot(df: pd.DataFrame) -> go.Figure:
    """
    Build a time series chart showing monthly transaction volume.

    Args:
        df (pd.DataFrame):
            Must include a "transaction_date" column compatible with datetime.

    Return:
        go.Figure: a plotly figure object representing sales volume evolution
    """
    fig: go.Figure = go.Figure()
    if df.empty or "transaction_date" not in df.columns:
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of sales", height=400)
        return fig

    df_clean: pd.DataFrame = df.copy()
    df_clean["transaction_date"] = pd.to_datetime(df_clean["transaction_date"], errors="coerce", dayfirst=True)
    df_clean = df_clean.dropna(subset=["transaction_date"])

    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")

    monthly_volume: pd.DataFrame = df_clean.groupby("year_month").size().reset_index(name="volume")
    monthly_volume["year_month"] = monthly_volume["year_month"].astype(str)

    if len(monthly_volume) > 0:
        fig = px.area(monthly_volume, x="year_month", y="volume", labels={"year_month": "Date", "volume": "Number of sales"})
        fig.update_traces(fillcolor="rgba(44, 160, 44, 0.3)", line_color="aquamarine")
    else:
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of sales")

    fig.update_layout(height=400, showlegend=False)
    return fig


def get_sales_by_type_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame summarizing the number of transactions for each property type.

    Args:
        df (pd.DataFrame): Filtered property dataset.

    Returns:
        pd.DataFrame: Columns:
            - "property_type"
            - "transaction_count"
    """
    if df.empty or "property_type" not in df.columns:
        return pd.DataFrame({"property_type": ["No data available"], "transaction_count": [0]})

    sales_by_type: pd.DataFrame = df["property_type"].value_counts().reset_index()
    sales_by_type.columns = ["property_type", "transaction_count"]
    return sales_by_type


def calculate_financing_simulation(
    property_price: float, personal_contribution: float, income: float, loan_duration: int, interest_rate: float
) -> tuple[float, float, float]:
    """
    Estimate the financial cost of a mortgage based on standard amortization formulas.

    Args:
        property_price (float): Total property cost in euros.
        personal_contribution (float): Amount contributed upfront.
        income (float): Personal salary per month.
        loan_duration (int): Duration of the loan in years.
        interest_rate (float): Annual interest rate (%).

    Returns:
        tuple[float, float, float]:
            - monthly_payment
            - total_cost
            - debt_ratio
    """
    loan_amount: float = property_price - personal_contribution

    if loan_amount <= 0:
        return 0.0, 0.0, 0.0

    monthly_rate: float = interest_rate / 100 / 12
    months: int = loan_duration * 12

    if monthly_rate > 0:
        monthly_payment: float = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    else:
        monthly_payment = loan_amount / months

    total_cost: float = monthly_payment * months
    debt_ratio: float = (monthly_payment / income) * 100 if monthly_payment > 0 else 0.0

    return round(monthly_payment, 2), round(total_cost, 2), round(debt_ratio, 2)


def compare_departments_by_criteria(
    df: pd.DataFrame,
    selected_departments: list[str],
    property_type: str | None = None,
    min_rooms: int | None = None,
    min_surface: float | None = None,
    max_surface: float | None = None,
) -> pd.DataFrame:
    """
    Compare key metrics (number of transactions and median price per m²)
    for a list of departments after applying the given filters.

    Args:
        df (pd.DataFrame): Transaction dataset.
        selected_departments (list[str]): Department codes to compare.
        property_type (str | None): Property type to filter by ("Maison", "Appartement")
            or None/"All" for all types.
        min_rooms (int | None): Minimum number of rooms.
        min_surface (float | None): Minimum surface in m².
        max_surface (float | None): Maximum surface in m².

    Returns:
        pd.DataFrame: Summary with one row per department containing :
            - "Department"
            - "Transactions"
            - "Median price per m² – [Type]" columns for available property types.
    """

    results: list[dict] = []

    for dep in selected_departments:
        filtered_loc: pd.DataFrame = filter_data_by_location(df, dep)
        filtered_dep: pd.DataFrame = filter_data_by_criteria(
            filtered_loc, property_type=property_type, min_rooms=min_rooms, min_surface=min_surface, max_surface=max_surface
        )

        metrics: dict = calculate_market_metrics(filtered_dep)
        median_prices: dict = metrics.get("median_price_per_m2_by_type", {})

        row: dict[str, str | float | int] = {
            "Department": dep,
            "Transactions": metrics.get("total_transactions", 0),
        }

        if property_type and property_type != "All":
            row[f"Median price per m² – {property_type}"] = median_prices.get(property_type, "No available")
        else:
            for t, val in median_prices.items():
                row[f"Median price per m² – {t}"] = val

        results.append(row)

    return pd.DataFrame(results)


def create_department_cards(
    df: pd.DataFrame, departments: list[str], property_type: str, min_rooms: int, min_surface: float, max_surface: float
) -> list[str]:
    """
    Generate an HTML string containing styled cards to compare key metrics
    across multiple departments based on filter criteria.

    Args:
        df (pd.DataFrame): Real-estate dataset.
        departments (list[str]): List of department codes to include.
        property_type (str): Property type to filter by.
        min_rooms (int): Minimum number of rooms.
        min_surface (float): Minimum surface area in m².
        max_surface (float): Maximum surface area in m².

    Returns:
        list[str]: HTML string with comparison cards displayed in a flex container.

    """

    cards: list[str] = []
    comparison_df: pd.DataFrame = compare_departments_by_criteria(
        df, selected_departments=departments, property_type=property_type, min_rooms=min_rooms, min_surface=min_surface, max_surface=max_surface
    )

    for _, row in comparison_df.iterrows():
        card_style = (
            "border: 1px solid #e0e0e0; "
            "border-radius: 10px; "
            "padding: 15px; "
            "box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.05); "
            "background-color: #f9f9f9; "
            "width: 100%;"
        )

        card_content = f'<div class="comparison-card" style="{card_style}">'
        title_style = "font-size: 1.2em; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 5px; margin-top: 0; margin-bottom: 10px;"

        card_content += f'<h3 style="{title_style}">{row["Department"]}</h3>'
        card_content += '<ul style="list-style-type: none; padding-left: 0; margin-bottom: 0;">'

        li_style = "margin-bottom: 6px; line-height: 1.4;"

        card_content += f'<li style="{li_style}"><b>Type :</b> {property_type if property_type != "All" else "All"}</li>'
        card_content += f'<li style="{li_style}"><b>Min rooms :</b> {min_rooms}</li>'
        card_content += f'<li style="{li_style}"><b>Surface range :</b> {min_surface} – {max_surface} m²</li>'
        card_content += f'<li style="{li_style}"><b>Transactions :</b> {row["Transactions"]}</li>'

        price_style = "font-weight: bold; color: #343a40; margin-left: 5px;"

        if property_type != "All":
            key = f"Median price per m² – {property_type}"
            price_value = row.get(key, "No available")
            card_content += f'<li style="{li_style}">Median price/m² ({property_type}) : <span style="{price_style}">{price_value} €/m²</span></li>'
        else:
            for col in row.index:
                if col.startswith("Median price per m² – "):
                    prop = col.split("–")[1].strip()
                    card_content += f'<li style="{li_style}">{prop} price/m²: <span style="{price_style}">{row[col]} €/m²</span></li>'

        card_content += "</ul>"
        card_content += "</div>"
        cards.append(card_content)

    return cards


def create_department_trend_plots(
    df: pd.DataFrame, departments: list[str], property_type: str, min_rooms: int, min_surface: float, max_surface: float
) -> list[go.Figure]:
    """
    Create sales trend plots (sales by date) for each selected department,
    applying the provided filters.

    Args:
        df (pd.DataFrame): Property dataset.
        departments (list[str]): Department codes to include.
        property_type (str): Property type to filter by (or "All").
        min_rooms (int): Minimum number of rooms (or None).
        min_surface (float): Minimum surface area in m² (or None).
        max_surface (float): Maximum surface area in m² (or None).

    Returns:
        list[go.Figure]: One Plotly figure per department showing sales over time.
    """
    plots: list[go.Figure] = []

    LINE_COLOR = "#007bff"
    FILL_COLOR = "rgba(0, 123, 255, 0.15)"

    for dep in departments:
        filtered_loc: pd.DataFrame = filter_data_by_location(df, dep)
        filtered: pd.DataFrame = filter_data_by_criteria(
            filtered_loc, property_type=property_type, min_rooms=min_rooms, min_surface=min_surface, max_surface=max_surface
        )

        if filtered.empty:
            fig_empty = go.Figure()
            fig_empty.update_layout(title=f"Sales trend – Department {dep} (No data)", plot_bgcolor="#f5f5f5")
            plots.append(fig_empty)
            continue

        fig: go.Figure = create_sales_by_date_plot(filtered)

        fig.update_layout(
            title=f"Sales trend – Department {dep}",
            title_font_size=14,
            title_x=0.5,
            plot_bgcolor="#fcfcfc",
            xaxis_title=None,
            yaxis_title="Volume of Sales",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
        )

        for trace in fig.data:
            trace.update(
                line_shape="spline",
                line=dict(width=3, color=LINE_COLOR),
                fillcolor=FILL_COLOR,
                mode="lines",
                hovertemplate="%{y} sales<br>%{x}<extra></extra>",
            )

        plots.append(fig)

    return plots
