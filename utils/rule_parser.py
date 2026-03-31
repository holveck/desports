"""
Rule-based parser for Delaware high school sports questions.

This parser:
- Extracts attributes first (sport, year, gender, classification)
- Infers intent separately
- Decides what information is missing (needs_clarification)
- Does NOT guess or answer questions
- Hands off complex cases to the LLM fallback
"""

import re
from typing import Optional, Dict, Any

from utils.sport_config import SPORT_CONFIG


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def remove_noise(text: str) -> str:
    """
    Remove words that help humans but add no meaning
    for structured parsing.
    """
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
    ]
    for word in noise_words:
        text = text.replace(word, "")
    return normalize(text)


# --------------------------------------------------
# Attribute extractors
# --------------------------------------------------

def extract_year(text: str) -> Optional[int]:
    match = re.search(r"\b(19|20)\d{2}\b", text)
    if match:
        return int(match.group())
    return None


def extract_gender(text: str) -> Optional[str]:
    if "girls" in text:
        return "girls"
    if "boys" in text:
        return "boys"
    return None


def extract_sport(text: str) -> Optional[str]:
    for sport in SPORT_CONFIG.keys():
        if sport in text:
            return sport
    return None


def extract_classification(text: str) -> Optional[str]:
    """
    Extract Division / Class information if present.
    """
    # Class 1A / 2A / 3A
    match = re.search(r"class\s*(1a|2a|3a)", text)
    if match:
        return f"Class {match.group(1).upper()}"

    # Division I / II
    match = re.search(r"division\s*(i{1,2})", text)
    if match:
        roman = match.group(1).upper()
        if roman == "I":
            return "Division I"
        if roman == "II":
            return "Division II"

    return None


# --------------------------------------------------
# Intent detection
# --------------------------------------------------

def detect_intent(text: str) -> str:
    """
    Determine what type of question this is.
    """
    if any(word in text for word in ["most", "highest", "lowest"]):
        return "aggregation"

    if any(word in text for word in ["how many", "most titles", "most championships"]):
        return "ranking"

    if any(word in text for word in ["player of the year", "mvp"]):
        return "recognition"

    # Default intent
    return "team_result"


# --------------------------------------------------
# Main rule-based parser
# --------------------------------------------------

def parse_rule_based(question: str) -> Optional[Dict[str, Any]]:
    """
    Parse a question using deterministic rules.

    Returns:
        query dict with:
          - intent
          - filters
          - needs_clarification

        OR None if the question should fall back to LLM parsing.
    """

    original_text = question
    text = normalize(question)
    cleaned = remove_noise(text)

    # Extract attributes
    year = extract_year(cleaned)
    sport = extract_sport(cleaned)
    gender = extract_gender(cleaned)
    classification = extract_classification(cleaned)
    intent = detect_intent(cleaned)

    # If we cannot even identify the sport, defer to LLM
    if not sport:
        return None

    config = SPORT_CONFIG[sport]

    # Handle gender logic
    if config.get("gendered", False):
        # Gender required but may be missing — handled later
        pass
    else:
        # For non-gendered sports, normalize gender
        gender = "overall"

    # Validate classification if present
    valid_classes = config["classifications"]
    if classification and classification not in valid_classes:
        classification = None

    # Assemble base query
    query: Dict[str, Any] = {
        "intent": intent,
        "filters": {
            "sport": sport,
            "gender": gender,
            "year": year,
            "classification": classification,
        },
        "needs_clarification": [],
    }

    # --------------------------------------------------
    # Required-field validation
    # --------------------------------------------------

    # Year is required for team_result questions
    if intent == "team_result" and year is None:
        query["needs_clarification"].append("year")

    # Gender required if the sport is gendered
    if config.get("gendered", False) and gender is None:
        query["needs_clarification"].append("gender")

    # Classification required only if more than one exists
    if len(valid_classes) > 1 and classification is None:
        query["needs_clarification"].append("classification")

    return query
