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

    Returns:
        list[str]: A sorted list of unique location choices that can be used in
        selection widgets. Format:
            - "postal_code - town_name"
            - "department_code"
    """
    choices: list[str] = []

    # Postal code + city
    if {"postal_code", "town_name"}.issubset(df.columns):
        towns: pd.DataFrame = df[["postal_code", "town_name"]].drop_duplicates()
        for _, row in towns.iterrows():
            postal_code: str = str(row["postal_code"])
            town_name: str = str(row["town_name"])
            choices.append(f"{postal_code} - {town_name}")

    # Department codes
    if "department_code" in df.columns:
        departments: pd.DataFrame = df[["department_code"]].drop_duplicates()
        for _, row in departments.iterrows():
            dep_code: str = str(row["department_code"])
            if dep_code not in choices:
                choices.append(dep_code)

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
    if not location:
        return df

    # Case 1: "postal_code - town_name"
    if " - " in location and "postal_code" in df.columns:
        postal_code: str = location.split(" - ")[0].strip()
        return df[df["postal_code"].astype(str) == postal_code]

    # Case 2: department code
    if "department_code" in df.columns:
        try:
            dept_code: int = int(location.strip())
            return df[df["department_code"] == dept_code]
        except ValueError:
            return df

    return df


def calculate_market_metrics(df: pd.DataFrame) -> dict[str, float]:
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

    # Compute price per m²
    if {"property_value", "building_area"}.issubset(df_clean.columns):
        df_clean = df_clean[(df_clean["property_value"] > 0) & (df_clean["building_area"] > 0)]

        total_value: float = float(df_clean["property_value"].sum())
        total_area: float = float(df_clean["building_area"].sum())
        avg_price_m2: float = total_value / total_area if total_area > 0 else 0.0

        median_price: float = float(df_clean["property_value"].median())
    else:
        avg_price_m2 = 0.0
        median_price = 0.0

    total_transactions: int = len(df_clean)
    avg_surface: float = float(df_clean["building_area"].mean()) if "building_area" in df_clean.columns else 0.0

    return {"avg_price_per_m2": avg_price_m2, "total_transactions": total_transactions, "median_price": median_price, "avg_surface": avg_surface}


def create_sales_by_property_type_plot(df: pd.DataFrame) -> go.Figure:
    """
    Build a bar chart representing the number of real-estate transactions
    grouped by property type (e.g., house, apartment).

    Args:
        df (pd.DataFrame):
            Filtered transaction data. Must contain "property_type".

    Returns:
        go.Figure: A Plotly figure representing sale counts.
    """
    if df.empty:
        fig: go.Figure = go.Figure()
        fig.update_layout(title="Sales by property type", xaxis_title="Property type", yaxis_title="Number of sales")
        return fig

    if "property_type" in df.columns:
        sales_by_type: pd.DataFrame = df["property_type"].value_counts().reset_index()
        sales_by_type.columns = ["property_type", "count"]
    else:
        sales_by_type = pd.DataFrame({"property_type": [], "count": []})

    if not sales_by_type.empty:
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
    Build a time series chart showing monthly transaction volume.

    Args:
        df (pd.DataFrame):
            Must include a "transaction_date" column compatible with datetime.

    Returns:
        go.Figure: A Plotly figure showing evolution of sales volume.
    """
    if df.empty or "transaction_date" not in df.columns:
        fig: go.Figure = go.Figure()
        fig.update_layout(title="Sales volume evolution", xaxis_title="Date", yaxis_title="Number of sales")
        return fig

    df_clean: pd.DataFrame = df.copy()
    df_clean["transaction_date"] = pd.to_datetime(df_clean["transaction_date"], errors="coerce", dayfirst=True)
    df_clean = df_clean.dropna(subset=["transaction_date"])

    df_clean["year_month"] = df_clean["transaction_date"].dt.to_period("M")

    monthly_volume: pd.DataFrame = df_clean.groupby("year_month").size().reset_index(name="volume")
    monthly_volume["year_month"] = monthly_volume["year_month"].astype(str)

    if not monthly_volume.empty:
        fig = px.area(
            monthly_volume,
            x="year_month",
            y="volume",
            title="Sales volume evolution",
            labels={"year_month": "Date", "volume": "Number of sales"},
        )
        fig.update_traces(fillcolor="rgba(44, 160, 44, 0.3)", line_color="#2ca02c")
    else:
        fig = go.Figure()
        fig.update_layout(title="Sales volume evolution", xaxis_title="Date", yaxis_title="Number of sales")

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
    property_price: float, personal_contribution: float, loan_duration: int, interest_rate: float
) -> tuple[float, float, float]:
    """
    Estimate the financial cost of a mortgage based on standard amortization formulas.

    Args:
        property_price (float): Total property cost in euros.
        personal_contribution (float): Amount contributed upfront.
        loan_duration (int): Duration of the loan in years.
        interest_rate (float): Annual interest rate (%).

    Returns:
        tuple[float, float, float]:
            - monthly_payment
            - total_cost
            - debt_ratio (assuming 3000€/month income)
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
    debt_ratio: float = (monthly_payment / 3000) * 100 if monthly_payment > 0 else 0.0

    return round(monthly_payment, 2), round(total_cost, 2), round(debt_ratio, 2)


def compare_departments(df: pd.DataFrame, selected_departments: list[str]) -> pd.DataFrame:
    """
    Compare market indicators across multiple departments.

    Args:
        df (pd.DataFrame):
            Full property dataset.
        selected_departments (list[str]):
            list of department selections (e.g., ["75", "92"]).

    Returns:
        pd.DataFrame:
            Columns:
                - "Department"
                - "Avg price/m² (€)"
                - "Median price (€)"
                - "Transactions"
    """

    results: list[dict[str, str | float | int]] = []

    for dep in selected_departments:
        filtered: pd.DataFrame = filter_data_by_location(df, dep)
        metrics: dict[str, float] = calculate_market_metrics(filtered)

        results.append(
            {
                "Department": dep,
                "Avg price/m² (€)": round(metrics["avg_price_per_m2"], 0),
                "Median price (€)": round(metrics["median_price"], 0),
                "Transactions": metrics["total_transactions"],
            }
        )

    return pd.DataFrame(results)
