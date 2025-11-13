from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_location_choices(df: pd.DataFrame) -> List[str]:
    """
    Get unique location choices from dataframe.

    Args:
        df: DataFrame containing property data

    Returns:
        List of location choices in format 'code - name'
    """
    choices = []
    if "postal_code" in df.columns and "town_name" in df.columns:
        towns = df[["postal_code", "town_name"]].drop_duplicates()
        choices.extend([f"{row['postal_code']} - {row['town_name']}" for _, row in towns.iterrows()])

    # Si on a le code département, on liste les départements
    if "department_code" in df.columns:
        departments = df[["department_code"]].drop_duplicates()
        choices.extend([str(row["department_code"]) for _, row in departments.iterrows() if str(row["department_code"]) not in choices])

    return sorted(choices)


def filter_data_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """
    Filter dataframe by selected location.

    Args:
        df: Complete property dataframe
        location: Selected location string (format: 'code - name' or 'code')

    Returns:
        Filtered dataframe for the specified location
    """
    if not location:
        return df

    # Postal code and town name
    if " - " in location and "postal_code" in df.columns:
        postal_code = location.split(" - ")[0].strip()
        return df[df["postal_code"].astype(str) == postal_code]

    # Department code
    elif "department_code" in df.columns:
        try:
            dept_code = int(location.strip())
            return df[df["department_code"] == dept_code]
        except ValueError:
            return df

    return df


def calculate_market_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate key market metrics for the filtered data.

    Args:
        df: Filtered property dataframe

    Returns:
        Dictionary containing market metrics
    """
    if df.empty:
        return {"avg_price_per_m2": 0, "total_transactions": 0, "price_evolution_1y": 0, "median_price": 0, "avg_surface": 0}

    # Ensure numeric columns
    df_clean = df.copy()
    if "property_value" in df_clean.columns:
        df_clean["property_value"] = pd.to_numeric(df_clean["property_value"], errors="coerce")
    if "building_area" in df_clean.columns:
        df_clean["building_area"] = pd.to_numeric(df_clean["building_area"], errors="coerce")

    # Calculate price per m²
    if "property_value" in df_clean.columns and "building_area" in df_clean.columns:
        df_clean = df_clean[(df_clean["building_area"] > 0) & (df_clean["property_value"] > 0)]
        total_value = df_clean["property_value"].sum()
        total_area = df_clean["building_area"].sum()
        avg_price_m2 = total_value / total_area
        median_price = df_clean["property_value"].median()
    else:
        avg_price_m2 = 0
        median_price = 0

    # Total transactions
    total_transactions = len(df_clean)

    # Average surface
    avg_surface = df_clean["building_area"].mean() if "building_area" in df_clean.columns else 0

    return {"avg_price_per_m2": avg_price_m2, "total_transactions": total_transactions, "median_price": median_price, "avg_surface": avg_surface}


def create_sales_by_property_type_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create sales volume by property type plot.

    Args:
        df: Filtered property dataframe

    Returns:
        Plotly figure showing sales by property type
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sales by property type", xaxis_title="Property type", yaxis_title="Number of sales")
        return fig

    # Group by property type
    if "property_type" in df.columns:
        sales_by_type = df["property_type"].value_counts().reset_index()
        sales_by_type.columns = ["property_type", "count"]
    else:
        sales_by_type = pd.DataFrame({"property_type": [], "count": []})

    if len(sales_by_type) > 0:
        fig = px.bar(
            sales_by_type,
            x="property_type",
            y="count",
            title="Sales by property type",
            labels={"property_type": "Property type", "count": "Number of sales"},
        )
        fig.update_traces(marker_color="#ff7f0e")
    else:
        fig = go.Figure()
        fig.update_layout(title="Sales by property type", xaxis_title="Property type", yaxis_title="Number of sales")

    fig.update_layout(height=400, showlegend=False)
    return fig


def create_volume_evolution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create sales volume evolution over time plot.

    Args:
        df: Filtered property dataframe

    Returns:
        Plotly figure showing volume evolution
    """
    if df.empty or "transaction_date" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Sales volume evolution", xaxis_title="Date", yaxis_title="Number of sales")
        return fig

    df_clean = df.copy()
    df_clean["transaction_date"] = pd.to_datetime(df_clean["transaction_date"], errors="coerce", dayfirst=True)
    df_clean = df_clean.dropna(subset=["transaction_date"])

    # Group by year-month
    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")
    monthly_volume = df_clean.groupby("year_month").size().reset_index(name="volume")
    monthly_volume["year_month"] = monthly_volume["year_month"].astype(str)

    if len(monthly_volume) > 0:
        fig = px.area(
            monthly_volume, x="year_month", y="volume", title="Sales volume evolution", labels={"year_month": "Date", "volume": "Number of sales"}
        )
        fig.update_traces(fillcolor="rgba(44, 160, 44, 0.3)", line_color="#2ca02c")
    else:
        fig = go.Figure()
        fig.update_layout(title="Sales volume evolution", xaxis_title="Date", yaxis_title="Number of sales")

    fig.update_layout(height=400, showlegend=False)
    return fig


def get_sales_by_type_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get sales data grouped by property type.

    Args:
        df: Filtered property dataframe

    Returns:
        DataFrame with sales count by property type
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

    Args:
        property_price: Total property price in euros
        personal_contribution: Personal contribution in euros
        loan_duration: Loan duration in years
        interest_rate: Annual interest rate in percentage

    Returns:
        Tuple containing (monthly_payment, total_cost, debt_ratio)
    """
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
    # Simplified debt ratio calculation (assuming 3000€ monthly income)
    debt_ratio = (monthly_payment / 3000) * 100 if monthly_payment > 0 else 0

    return round(monthly_payment, 2), round(total_cost, 2), round(debt_ratio, 2)


def compare_departments(df: pd.DataFrame, selected_departments: List[str]) -> pd.DataFrame:
    """
    Compare key market indicators across multiple departments.

    Args:
        df: Complete property dataframe
        selected_departments: List of selected departments (format: 'code - name' or 'code')

    Returns:
        DataFrame with comparison of average price/m², median price, and transaction count
    """
    from .market_analysis import calculate_market_metrics, filter_data_by_location

    results = []

    for dep in selected_departments:
        filtered = filter_data_by_location(df, dep)
        metrics = calculate_market_metrics(filtered)

        results.append(
            {
                "Department": dep,
                "Avg price/m² (€)": round(metrics["avg_price_per_m2"], 0),
                "Median price (€)": round(metrics["median_price"], 0),
                "Transactions": metrics["total_transactions"],
            }
        )

    return pd.DataFrame(results)
