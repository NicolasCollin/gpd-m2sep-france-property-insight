from typing import Dict, List, Tuple, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_location_choices(df: pd.DataFrame) -> List[str]:
    """
    Get location from dataframe aboout postal code and town name or just a department to discover analysis.

    Arg:
        df: pd.DataFrame

    Return :
        List[str] : a choice

    """
    choices = []
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
    Filter dataframe by selected location.

    Arg:
        df: pd.DataFrame
        str: location

    Return:
        pd.DataFrame : a dataframe filted by location

    """
    if not location or df.empty:
        return df

    if " - " in location and "postal_code" in df.columns:
        postal_code = location.split(" - ")[0].strip()
        return df[df["postal_code"].astype(str) == postal_code]

    elif "department_code" in df.columns:
        try:
            dept_code = location.strip()
            return df[df["department_code"].astype(str) == dept_code]
        except ValueError:
            return df

    return df


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

    df_clean = df.copy()
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


def calculate_market_metrics(df: pd.DataFrame) -> Dict[str, Union[int, float, Dict]]:
    """
    Calculate key market metrics for the filtered data.

    Arg:
        df: pd.DataFrame

    Return:
        Dict[str, Union[int, float, Dict]]: a dictionary with total transactions, average surface, and median price per m² by property type
    """
    if df.empty:
        return {"total_transactions": 0, "avg_surface": 0, "median_price_per_m2_by_type": {}}

    df_clean = df.copy()
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
    Create sales volume by property type plot.

    Arg:
        df: pd.DataFrame

    Return:
        go.Figure: a plotly figure object representing sales by property type
    """
    if df.empty or "property_type" not in df.columns:
        fig = go.Figure()
        fig.update_layout(xaxis_title="Property type", yaxis_title="Number of sales", height=400)
        return fig

    sales_by_type = df["property_type"].value_counts().reset_index()
    sales_by_type.columns = ["property_type", "count"]

    if len(sales_by_type) > 0:
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
    Create sales volume evolution over time plot.

    Arg:
        df: pd.DataFrame

    Return:
        go.Figure: a plotly figure object representing sales volume evolution
    """
    if df.empty or "transaction_date" not in df.columns:
        fig = go.Figure()
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of sales", height=400)
        return fig

    df_clean = df.copy()
    df_clean["transaction_date"] = pd.to_datetime(df_clean["transaction_date"], errors="coerce", dayfirst=True)
    df_clean = df_clean.dropna(subset=["transaction_date"])

    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")
    monthly_volume = df_clean.groupby("year_month").size().reset_index(name="volume")
    monthly_volume["year_month"] = monthly_volume["year_month"].astype(str)

    if len(monthly_volume) > 0:
        fig = px.area(monthly_volume, x="year_month", y="volume", labels={"year_month": "Date", "volume": "Number of sales"})
        fig.update_traces(fillcolor="rgba(44, 160, 44, 0.3)", line_color="aquamarine")
    else:
        fig = go.Figure()
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of sales")

    fig.update_layout(height=400, showlegend=False)
    return fig


def get_sales_by_type_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get sales data grouped by property type.

    Return:
        pd.DataFrame: a dataframe with property type and corresponding transaction counts
    """
    if df.empty or "property_type" not in df.columns:
        return pd.DataFrame({"property_type": ["No data available"], "transaction_count": [0]})

    sales_by_type = df["property_type"].value_counts().reset_index()
    sales_by_type.columns = ["property_type", "transaction_count"]
    return sales_by_type


def calculate_financing_simulation(
    property_price: float, personal_contribution: float, loan_duration: int, interest_rate: float
) -> Tuple[float, float, float]:
    """
    Calculate financing simulation results.
    """
    # Validate inputs
    property_price = max(0, float(property_price or 0))
    personal_contribution = max(0, float(personal_contribution or 0))
    loan_duration = max(1, int(loan_duration or 1))
    interest_rate = max(0, float(interest_rate or 0))

    loan_amount = property_price - personal_contribution

    if loan_amount <= 0:
        return 0.0, 0.0, 0.0

    monthly_rate = interest_rate / 100 / 12
    months = loan_duration * 12

    if monthly_rate > 0:
        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    else:
        monthly_payment = loan_amount / months

    total_cost = monthly_payment * months
    debt_ratio = (monthly_payment / 3000) * 100 if monthly_payment > 0 else 0

    return round(monthly_payment, 2), round(total_cost, 2), round(debt_ratio, 2)


def compare_departments(df: pd.DataFrame, selected_departments: List[str]) -> pd.DataFrame:
    """
    Compare key market indicators across multiple departments.

    Args:
        pd.DataFrame : df (fpi data)
        List[str] : selected departments

    Return:
        pd.DataFrame: a dataframe comparing median price per m² and transaction counts across departments
    """
    results = []

    for dep in selected_departments:
        filtered = filter_data_by_location(df, dep)
        metrics = calculate_market_metrics(filtered)

        median_prices = metrics.get("median_price_per_m2_by_type", {})

        row = {
            "Department": dep,
            "Transactions": metrics.get("total_transactions", "No available"),
        }

        if isinstance(median_prices, dict) and median_prices:
            for prop_type, value in median_prices.items():
                row[f"Median price per m² – {prop_type}"] = value
        else:
            row["Median price per m² – Overall"] = "No available"

        representative = "No available"
        if isinstance(median_prices, dict) and median_prices:
            if median_prices.get("Appartement") not in (None, "No available"):
                representative = median_prices["Appartement"]

            elif median_prices.get("Maison") not in (None, "No available"):
                representative = median_prices["Maison"]

            else:
                representative = next(iter(median_prices.values()), "No available")

        row["Median price per m² (Representative)"] = representative

        results.append(row)

    return pd.DataFrame(results)
