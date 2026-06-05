import re
from utils.sport_config import SPORT_CONFIG

SUPERLATIVE_KEYWORDS = {
    "most",
    "fewest",
    "highest",
    "lowest",
    "top",
    "best",
}

def tokenize(text):
    return set(re.findall(r"\b\w+\b", text.lower()))

def normalize_query(query):
    if not query:
        return query

    filters = query.get("filters", {})
    raw_text = query.get("original_text", "")
    sport = filters.get("sport")

    if not sport or sport not in SPORT_CONFIG:
        return query

    sport_cfg = SPORT_CONFIG[sport]

    tokens = tokenize(raw_text)

    if SUPERLATIVE_KEYWORDS & tokens:
        query["intent"] = "ranking"

    gender = filters.get("gender")
    policy = sport_cfg.get("gender_policy")

    if gender == "overall" and policy in {"girls_only", "boys_only"}:
        gender = None

    if not gender:
        if policy == "girls_only":
            filters["gender"] = "girls"
        elif policy == "boys_only":
            filters["gender"] = "boys"
        elif policy == "mixed":
            filters["gender"] = "overall"
        else:
            filters["gender"] = None
    else:
        filters["gender"] = gender

    query["filters"] = filters
    return query
