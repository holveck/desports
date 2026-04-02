from utils.sport_config import SPORT_CONFIG


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
    Normalize intent and gender so the executor
    always receives a structurally executable query.
    """

    filters = query.get("filters", {})
    intent = query.get("intent")
    raw_text = query.get("original_text", "").lower()

    sport = filters.get("sport")
    if not sport or sport not in SPORT_CONFIG:
        return query  # nothing to normalize safely

    sport_cfg = SPORT_CONFIG[sport]

    # ----------------------------------
    # 1. Intent precedence enforcement
    # ----------------------------------

    if any(word in raw_text for word in SUPERLATIVE_KEYWORDS):
        query["intent"] = "ranking"

    # ----------------------------------
    # 2. Gender resolution for ranking
    # ----------------------------------

    if query["intent"] == "ranking":
        gender = filters.get("gender")
        policy = sport_cfg.get("gender_policy")

        if gender:
            pass  # user explicitly specified gender
        elif policy == "girls_only":
            filters["gender"] = "girls"
        elif policy == "boys_only":
            filters["gender"] = "boys"
        elif policy == "mixed":
            filters["gender"] = "overall"
        else:
            # gendered sport, but user didn’t specify
            # executor will require grouping per gender later if needed
            filters["gender"] = None

    query["filters"] = filters
    return query
``
