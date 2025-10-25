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


import re
from urllib.parse import quote_plus
from cardivore_ai.utils.cards import build_search_string  # already returns (search_string, is_japanese)

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

