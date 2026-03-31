"""
Rule-based parser for Delaware high school sports questions.
"""

import re

from utils.sport_config import SPORT_CONFIG
from utils.schools import extract_school


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def normalize(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def remove_noise(text):
    noise_words = [
        "state",
        "high school",
        "championship",
        "champions",
        "champion",
        "title",
        "final",
        "won",
        "winner",
        "who",
        "did",
        "the",
        "has",
        "have",
        "how many",
    ]
    for word in noise_words:
        text = text.replace(word, "")
    return normalize(text)


# --------------------------------------------------
# Attribute extractors
# --------------------------------------------------

def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", text)
    if match:
        return int(match.group())
    return None


def extract_gender(text):
    if "girls" in text:
        return "girls"
    if "boys" in text:
        return "boys"
    return None


def extract_sport(text):
    for sport in SPORT_CONFIG.keys():
        if sport in text:
            return sport
    return None


def extract_classification(text):
    match = re.search(r"class\s*(1a|2a|3a)", text)
    if match:
        return f"Class {match.group(1).upper()}"

    match = re.search(r"division\s*(i{1,2})", text)
    if match:
        return f"Division {match.group(1).upper()}"

    return None


# --------------------------------------------------
# Intent detection
# --------------------------------------------------

def detect_intent(text):
    if "how many" in text or "most" in text:
        return "aggregation"
    return "team_result"


# --------------------------------------------------
# Main parser
# --------------------------------------------------

def parse_rule_based(question):
    text = normalize(question)
    cleaned = remove_noise(text)

    sport = extract_sport(cleaned)
    if not sport:
        return None  # fall back to LLM

    config = SPORT_CONFIG[sport]

    year = extract_year(cleaned)
    gender = extract_gender(cleaned)
    classification = extract_classification(cleaned)
    school_id = extract_school(question)
    intent = detect_intent(text)

    if not config.get("gendered", False):
        gender = "overall"

    valid_classes = config["classifications"]
    if classification and classification not in valid_classes:
        classification = None

    query = {
        "intent": intent,
        "filters": {
            "sport": sport,
            "gender": gender,
            "year": year,
            "classification": classification,
            "school_id": school_id,
        },
        "needs_clarification": [],
    }

    # ------------------------
    # Required fields
    # ------------------------

    if intent == "team_result" and year is None:
        query["needs_clarification"].append("year")

    if config.get("gendered", False) and gender is None:
        query["needs_clarification"].append("gender")

    if len(valid_classes) > 1 and classification is None:
        query["needs_clarification"].append("classification")

    return query
