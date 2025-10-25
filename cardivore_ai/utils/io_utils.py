import re
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# 🗺️  Column mappings and ordering for Market Movers CSV normalization
# ----------------------------------------------------------------------

CSV_TO_DB = {
    "Card": "card",  # standardized name for pipeline compatibility
    "Card Name": "card",
    "Price Change %": "price_change_pct",
    "Price Change $": "price_change_usd",
    "Starting Price": "starting_price",
    "Last Sale": "last_sale",
    "Avg": "avg_price",
    "Min Sale": "min_sale",
    "Max Sale": "max_sale",
    "Volume Change %": "volume_change_pct",
    "# of Sales": "num_sales",
    "Total Sales $": "total_sales_usd",
}

DB_COL_ORDER = [
    "card",
    "price_change_pct",
    "price_change_usd",
    "starting_price",
    "last_sale",
    "avg_price",
    "min_sale",
    "max_sale",
    "volume_change_pct",
    "num_sales",
    "total_sales_usd",
]

# ----------------------------------------------------------------------
# 💵 Universal numeric cleaning
# ----------------------------------------------------------------------

def _extract_first_number(x):
    """
    Extract the first numeric token from a cell.
    Handles '$1.23', '122.22', '$2.20 (10/11/2025)', or numeric 1.23.
    """
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.integer, np.floating)):
        return float(x)

    s = str(x).replace(",", "").replace("$", "").strip()
    # Capture only the first number before any extra text (e.g., date)
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else np.nan


def _clean_money(series: pd.Series) -> pd.Series:
    """Clean $, commas, or extra text in currency columns."""
    return series.map(_extract_first_number).astype(float)


def _clean_percent(series: pd.Series) -> pd.Series:
    """Clean percent or numeric strings like '78.20' or '78.20%'."""
    return series.map(_extract_first_number).astype(float)


def _clean_int(series: pd.Series) -> pd.Series:
    """Coerce integer fields like '# of Sales'."""
    cleaned = (
        series.astype(str)
        .str.extract(r"(\d+)")
        .fillna(0)
    )
    cleaned = cleaned.infer_objects(copy=False).astype(int)
    return cleaned


# ----------------------------------------------------------------------
# 🧹 Column Normalization for SQL compatibility
# ----------------------------------------------------------------------

def normalize_column_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column headers for SQL compatibility.
    - Lowercase
    - Replace spaces/special characters with underscores
    - Remove %,$,#, and other illegal SQL chars
    - Ensures uniqueness by appending suffix if needed
    """
    new_cols = []
    seen = {}
    for col in df.columns:
        clean = col.strip().lower()
        clean = re.sub(r"[%$#]", "", clean)
        clean = re.sub(r"[^0-9a-zA-Z_]+", "_", clean)
        clean = re.sub(r"_+", "_", clean).strip("_")
        # Handle duplicates
        if clean in seen:
            seen[clean] += 1
            clean = f"{clean}_{seen[clean]}"
        else:
            seen[clean] = 1
        new_cols.append(clean)
    df.columns = new_cols
    return df


# ----------------------------------------------------------------------
# 🧭 Market Movers CSV normalization
# ----------------------------------------------------------------------

def normalize_market_movers_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a MarketMovers CSV so it fits your MySQL schema.
    - Renames columns
    - Fills missing expected columns
    - Cleans percent, money, and integer fields
    """
    df = df.copy()

    # Map column names to DB field names
    rename_map = {c: CSV_TO_DB[c] for c in df.columns if c in CSV_TO_DB}
    df = df.rename(columns=rename_map)

    # Ensure all expected columns exist (fill missing with NaN)
    for col in DB_COL_ORDER:
        if col not in df.columns:
            df[col] = np.nan

    # Clean numeric fields
    if "price_change_pct" in df:
        df["price_change_pct"] = _clean_percent(df["price_change_pct"])
    if "volume_change_pct" in df:
        df["volume_change_pct"] = _clean_percent(df["volume_change_pct"])

    for money_col in [
        "price_change_usd", "starting_price", "last_sale", "avg_price",
        "min_sale", "max_sale", "total_sales_usd"
    ]:
        if money_col in df:
            df[money_col] = _clean_money(df[money_col])

    if "num_sales" in df:
        df["num_sales"] = _clean_int(df["num_sales"])

    # Reorder columns consistently
    return df[DB_COL_ORDER]
