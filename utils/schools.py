"""
School lookup and extraction utilities.

This module:
- Loads canonical school names and aliases from data/schools.csv
- Normalizes text for safe matching
- Extracts school_id from natural-language questions
- Avoids false positives by using word-boundary and longest-match logic
"""

import pandas as pd
import re
from functools import lru_cache


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def normalize(text):
    """
    Normalize text by:
    - converting to lowercase
    - removing punctuation
    - collapsing whitespace
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------
# School lookup loading
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_school_lookup():
    """
    Load schools.csv and return a dict mapping
    normalized alias -> school record.

    Each record contains:
    - school_id
    - canonical_name
    """
    df = pd.read_csv("data/schools.csv")

    lookup = {}

    for _, row in df.iterrows():
        school_id = row["school_id"]
        canonical = row["canonical_name"]

        aliases = [canonical]

        if "aliases" in row and isinstance(row["aliases"], str):
            aliases.extend(
                a.strip() for a in row["aliases"].split(",") if a.strip()
            )

        for name in aliases:
            key = normalize(name)
            lookup[key] = {
                "school_id": school_id,
                "canonical_name": canonical,
            }

    return lookup


# --------------------------------------------------
# School extraction
# --------------------------------------------------

def extract_school(text):
    """
    Return the best-matching school_id from text.

    Matching rules:
    - ignore aliases shorter than 4 characters
    - match on whole words / phrases using word boundaries
    - if multiple schools match, prefer the longest alias
    """
    lookup = load_school_lookup()
    normalized_text = normalize(text)

    matches = []

    for alias, record in lookup.items():
        # Ignore extremely short aliases (e.g., "cr", "hs", "st")
        if len(alias) < 4:
            continue

        # Match alias as a whole word or phrase
        pattern = r"\b" + re.escape(alias) + r"\b"

        if re.search(pattern, normalized_text):
            matches.append((alias, record))

    if not matches:
        return None

    # Prefer the longest (most specific) alias
    matches.sort(key=lambda x: len(x[0]), reverse=True)

    return matches[0][1]["school_id"]
