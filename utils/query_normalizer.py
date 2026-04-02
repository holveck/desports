from utils.sport_config import SPORT_CONFIG

# Words that imply a ranking query, regardless of initial parser intent
SUPERLATIVE_KEYWORDS = {
    "most",
    "fewest",
    "highest",
    "lowest",
    "top",
    "best",
}


def normalize_query(query):
    """
    Normalize query intent and gender semantics so that the
    executor always receives a structurally valid query.

    This function:
    - Enforces intent precedence (ranking vs aggregation)
    - Resolves gender according to SPORT_CONFIG semantics
    - Treats 'overall' as non-binding for single-gender sports
    """

    if not query:
        return query

    filters = query.get("filters", {})
    raw_text = query.get("original_text", "")
    sport = filters.get("sport")

    # If we can't reason about the sport, return as-is
    if not sport or sport not in SPORT_CONFIG:
        return query

    sport_cfg = SPORT_CONFIG[sport]

    # --------------------------------------------------
    # 1. Intent precedence enforcement
    # --------------------------------------------------
    text_lower = raw_text.lower()
    for word in SUPERLATIVE_KEYWORDS:
        if word in text_lower:
            query["intent"] = "ranking"
            break

    # --------------------------------------------------
    # 2. Gender normalization (universal rule)
    # --------------------------------------------------
    gender = filters.get("gender")
    policy = sport_cfg.get("gender_policy")

    # Treat "overall" as unspecified for single-gender sports
    if gender == "overall" and policy in {"girls_only", "boys_only"}:
        gender = None

    # Apply implicit gender when unspecified
    if not gender:
        if policy == "girls_only":
            filters["gender"] = "girls"
        elif policy == "boys_only":
            filters["gender"] = "boys"
        elif policy == "mixed":
            filters["gender"] = "overall"
        else:
            # gendered sport (boys & girls exist) and user did not specify
            filters["gender"] = None

    query["filters"] = filters
    return query
