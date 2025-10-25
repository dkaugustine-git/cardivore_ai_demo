# cardivore_ai/pipeline/pipeline_helper.py
import pandas as pd
import re
from sqlalchemy import create_engine
from cardivore_ai.utils.db_utils import get_engine_from_env
from cardivore_ai.utils.io_utils import normalize_column_headers
from cardivore_ai.utils.cards import build_search_string
import re
from urllib.parse import quote_plus

def build_search_string(card_name: str) -> tuple[str, bool]:
    """
    Generate a normalized eBay search string for a card name and flag if Japanese.

    Returns:
        (search_string, is_japanese)

    Behavior:
    - Removes trailing set or year info (e.g., "Sword & Shield:", "2021").
    - Keeps the portion before the first 4-digit year or colon.
    - Extracts the card number/code after '#'.
    - Adds "Black Star Promo" if detected.
    - Flags Japanese cards (case-insensitive match).
    - Returns a concise, search-optimized string like:
        "Pikachu 25 Black Star Promo"
    """
    if not isinstance(card_name, str):
        return "", False

    lowered = card_name.lower()
    is_japanese = "japanese" in lowered

    # Remove everything after a year (19xx or 20xx) or a colon (set names)
    clean_name = re.split(r"\s(?:19|20)\d{2}|\s*[:]", card_name)[0].strip()

    # Extract the card code/number (handles formats like #25, #25a, #025/025)
    match = re.search(r"#([\w/-]+)", card_name)
    code = match.group(1).strip() if match else ""

    # Detect and include promos
    promo = "Black Star Promo" if "black star promo" in lowered else ""

    # Build final search string components
    parts = [clean_name, code]
    if promo:
        parts.append(promo)
    if is_japanese:
        parts.append("Japanese")

    # Join and clean
    search_string = " ".join(p for p in parts if p).strip()

    return search_string, is_japanese


def build_ebay_search_url(card_name: str) -> str:
    """
    Build an eBay search URL for raw (ungraded) Pokémon cards.

    - Keeps card_name-derived search_string (e.g. "Steelix 150/132")
    - Adds filters for Near Mint, English, ungraded cards
    - Keeps 'Japanese' keyword in search if present
    """
    search_string, is_japanese = build_search_string(card_name)
    if not search_string:
        return ""

    # --- Base URL ---
    base_url = "https://www.ebay.com/sch/i.html"

    # --- Query params ---
    params = {
        "_nkw": search_string,                       # search keyword
        "_sacat": "0",                               # all categories
        "_from": "R40",                              # standard eBay browsing param
        "_dcat": "183454",                           # Pokémon TCG category
        "Card Condition": "Near Mint or Better",     # fix double-encoding
        "Graded": "No",
        "_sop": "1"                                  # sort by newest
    }

    # Only include Language=English if not Japanese
    if not is_japanese:
        params["Language"] = "English"

    # --- Build full URL ---
    query = "&".join(f"{quote_plus(k)}={quote_plus(str(v))}" for k, v in params.items())
    return f"{base_url}?{query}"

# --- Extraction ---
def load_sales_tables():
    """Load raw and PSA10 sales tables from MySQL into DataFrames."""
    engine = get_engine_from_env()
    raw = pd.read_sql("SELECT * FROM raw_historic_sales", engine)
    psa10 = pd.read_sql("SELECT * FROM psa10_historic_sales", engine)
    return raw, psa10, engine


# --- Transformation helpers ---
def add_common_card_name(df: pd.DataFrame, trim_right: int) -> pd.DataFrame:
    """Create common_card_name by trimming the right N chars from 'card'."""
    df["common_card_name"] = df["card"].str.slice(stop=-trim_right)
    return df


def summarize_sales(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Aggregate average price, volume, and last sale per common_card_name."""
    grouped = (
        df.groupby("common_card_name", as_index=False)
        .agg(
            **{
                f"{prefix}_avg": ("avg_price", "mean"),
                f"{prefix}_volume": ("num_sales", "mean"),
                f"{prefix}_last_sale": ("last_sale", lambda x: x.iloc[-1]),
            }
        )
    )
    return grouped


# --- Main pipeline ---
def build_card_summary():
    """Full pipeline to build and return the merged card summary DataFrame."""
    raw_df, psa_df, engine = load_sales_tables()

    # Normalize columns
    raw_df = normalize_column_headers(raw_df)
    psa_df = normalize_column_headers(psa_df)

    # Add common names
    raw_df = add_common_card_name(raw_df, trim_right=20)
    psa_df = add_common_card_name(psa_df, trim_right=7)

    # Summarize
    raw_summary = summarize_sales(raw_df, "raw")
    psa_summary = summarize_sales(psa_df, "psa10")

    # Merge
    summary = pd.merge(raw_summary, psa_summary, on="common_card_name", how="inner")

    # Add search strings
    summary[["search_string", "is_japanese"]] = summary["common_card_name"].apply(
        lambda x: pd.Series(build_search_string(x))
    )
    summary["ebay_url"] = summary["search_string"].apply(build_ebay_search_url)
    
    # --- ROI Calculation ---
    summary["effective_psa10_value"] = summary["psa10_avg"] * 0.85
    summary["cost_basis"] = summary["raw_avg"] + 25
    summary["roi_multiple"] = summary["effective_psa10_value"] / summary["cost_basis"]
    summary["roi_percent"] = (summary["roi_multiple"] - 1) * 100

    return summary, engine

# --- Retrieval helper ---
def get_summary_df():
    """
    Load the card summary DataFrame from MySQL.

    If the table 'card_summary' doesn't exist yet, it will build it
    using the current pipeline and return that fresh DataFrame.
    """
    from sqlalchemy.exc import ProgrammingError

    engine = get_engine_from_env()
    try:
        # Try to load existing table
        summary_df = pd.read_sql("SELECT * FROM card_summary", engine)
        print("✅ Loaded existing summary table from DB.")
    except ProgrammingError:
        # Build pipeline if table doesn't exist
        print("⚠️ Summary table not found — running build_card_summary()...")
        summary_df, engine = build_card_summary()
        summary_df.to_sql("card_summary", engine, if_exists="replace", index=False)
        print("✅ Created and saved summary table to DB.")

    return summary_df, engine
