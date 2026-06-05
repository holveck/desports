"""
School lookup and extraction utilities.

This module:
- Loads canonical school names, aliases, and styles from data/schools.csv
- Normalizes text for safe matching
- Extracts school_id from natural-language questions
- Exposes shared lookup maps for canonical names, aliases, and styles
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
# Base data loading
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_schools_df():
    """
    Load schools.csv once and return the dataframe.
    """
    return pd.read_csv("data/schools.csv")


# --------------------------------------------------
# School lookup loading
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_school_lookup():
    """
    Return a dict mapping normalized alias -> school record.

    Each record contains:
    - school_id
    - canonical_name
    - primary_color
    - secondary_color
    """
    df = load_schools_df()
    lookup = {}

    for _, row in df.iterrows():
        school_id = row["school_id"]
        canonical = row["canonical_name"]

        record = {
            "school_id": school_id,
            "canonical_name": canonical,
            "primary_color": row.get("primary_color"),
            "secondary_color": row.get("secondary_color"),
        }

        aliases = [canonical]

        if "aliases" in row and isinstance(row["aliases"], str):
            aliases.extend(
                a.strip() for a in row["aliases"].split(",") if a.strip()
            )

        for name in aliases:
            lookup[normalize(name)] = record

    return lookup


@lru_cache(maxsize=1)
def load_school_lookup_by_id():
    """
    Return a dict mapping school_id -> school record.
    """
    lookup = load_school_lookup()
    by_id = {}

    for record in lookup.values():
        school_id = record.get("school_id")
        if school_id and school_id not in by_id:
            by_id[school_id] = record

    return by_id


@lru_cache(maxsize=1)
def load_school_name_lookup():
    """
    Return a dict mapping lowercase canonical school name -> school_id.
    """
    df = load_schools_df()
    return {
        str(row["canonical_name"]).lower().strip(): row["school_id"]
        for _, row in df.iterrows()
    }


@lru_cache(maxsize=1)
def load_school_styles():
    """
    Return a dict mapping school_id -> style info.
    """
    df = load_schools_df()
    return {
        row["school_id"]: {
            "primary_color": row.get("primary_color"),
            "secondary_color": row.get("secondary_color"),
        }
        for _, row in df.iterrows()
    }


# --------------------------------------------------
# Lookup helpers
# --------------------------------------------------

def get_school_by_id(school_id):
    """
    Return the school record for a school_id, or None.
    """
    if not school_id:
        return None

    return load_school_lookup_by_id().get(school_id)


def get_canonical_school_name(school_id):
    """
    Return the canonical school name for a school_id, or None.
    """
    record = get_school_by_id(school_id)
    if not record:
        return None

    return record.get("canonical_name")


def get_school_styles():
    """
    Return school_id -> style mapping.
    """
    return load_school_styles()


def get_school_name_lookup():
    """
    Return canonical school name -> school_id mapping.
    """
    return load_school_name_lookup()


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
        if len(alias) < 4:
            continue

        pattern = r"\b" + re.escape(alias) + r"\b"

        if re.search(pattern, normalized_text):
            matches.append((alias, record))

    if not matches:
        return None

    matches.sort(key=lambda x: len(x[0]), reverse=True)
    return matches[0][1]["school_id"]
