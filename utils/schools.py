"""
School lookup utilities.

Loads canonical school names and aliases from data/schools.csv
and provides helpers for entity extraction.
"""

import pandas as pd
import re
from functools import lru_cache
from typing import Optional, Dict


@lru_cache
def load_school_lookup() -> Dict[str, Dict[str, str]]:
    """
    Returns a dict mapping normalized alias -> school record.
    """
    df = pd.read_csv("data/schools.csv")

    lookup = {}

    for _, row in df.iterrows():
        school_id = row["school_id"]
        canonical = row["canonical_name"]

        aliases = [canonical]

        if isinstance(row.get("aliases"), str):
            aliases.extend(a.strip() for a in row["aliases"].split(","))

        for alias in aliases:
            key = normalize(alias)
            lookup[key] = {
                "school_id": school_id,
                "canonical_name": canonical,
            }

    return lookup


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_school(text: str) -> Optional[str]:
    """
    Returns school_id if a school is mentioned, else None.
    """
    lookup = load_school_lookup()
    normalized_text = normalize(text)

    for alias, school in lookup.items():
        if alias in normalized_text:
            return school["school_id"]

    return None
``
