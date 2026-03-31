"""
School lookup and extraction utilities.
"""

import pandas as pd
import re
from functools import lru_cache


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def load_school_lookup():
    """
    Load schools.csv and return a dict mapping alias -> school record.
    """
    df = pd.read_csv("data/schools.csv")

    lookup = {}

    for _, row in df.iterrows():
        school_id = row["school_id"]
        canonical = row["canonical_name"]

        aliases = [canonical]

        if isinstance(row.get("aliases"), str):
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


def extract_school(text):
    """
    Return school_id if a known school is mentioned in the text.
    """
    lookup = load_school_lookup()
    normalized_text = normalize(text)

    for alias, record in lookup.items():
        if alias in normalized_text:
            return record["school_id"]

    return None
