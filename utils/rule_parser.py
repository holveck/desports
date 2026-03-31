import re

SPORTS = ["basketball", "soccer", "lacrosse", "football"]
GENDERS = ["boys", "girls"]

def parse_rule_based(question: str):
    q = question.lower()

    year = None
    sport = None
    gender = None

    match = re.search(r"(19|20)\d{2}", q)
    if match:
        year = int(match.group())

    for s in SPORTS:
        if s in q:
            sport = s

    for g in GENDERS:
        if g in q:
            gender = g

    if "who won" in q or "champion" in q:
        return {
            "intent": "team_result",
            "filters": {
                "sport": sport,
                "gender": gender,
                "year": year,
                "recognition_type": None
            },
            "group_by": None,
            "aggregation": None,
            "derived_metric": None
        }

    return None
