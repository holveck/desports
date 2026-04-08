import pandas as pd
import html
import re

from utils.card_descriptor import build_card_descriptor
from utils.sport_config import SPORT_CONFIG


# --------------------------------------------------
# Helpers (unchanged)
# --------------------------------------------------

def normalize_school_name(name):
    return (
        str(name)
        .replace("\u00a0", " ")
        .lower()
        .strip()
    )


def clean_text(value):
    if value is None:
        return None

    value = str(value)

    prev = None
    while value != prev:
        prev = value
        value = html.unescape(value)

    value = re.sub(r"&lt;[^&gt;]+&gt;", "", value)
    return value.strip()


# --------------------------------------------------
# Phase 1 title formatting (config‑driven)
# --------------------------------------------------

def format_sport_label(row):
    """
    Build the sport label for card titles using SPORT_CONFIG.

    Rule:
    - Include gender ONLY when gender_policy == "gendered"
    - Omit gender for boys_only / girls_only / mixed
    """
    sport_key = row["sport"].lower()
    gender = row.get("gender", "").title()

    config = SPORT_CONFIG.get(sport_key)

    # Defensive fallback
    if not config:
        return f"{gender} {row['sport'].title()}" if gender else row["sport"].title()

    if config.get("gender_policy") == "gendered" and gender:
        return f"{gender} {row['sport'].title()}"

    return row["sport"].title()


def format_ranking_title(filters):
    sport_key = filters.get("sport", "").lower()
    sport_name = filters.get("sport", "").title()
    gender = filters.get("gender", "").title()

    config = SPORT_CONFIG.get(sport_key)

    if config and config.get("gender_policy") == "gendered" and gender:
        return f"All‑Time {gender} {sport_name} State Championships"

    return f"All‑Time {sport_name} State Championships"


# --------------------------------------------------
# Result → Card mapping (Phase 1)
# --------------------------------------------------

def result_to_card(result, explanation, query, school_styles, school_name_lookup):

    # --------------------------------------------------
    # Champion recall (single row) → Variant A
    # --------------------------------------------------
    if isinstance(result, pd.DataFrame) and len(result) == 1 and "year" in result.columns:
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(normalize_school_name(champ_name))

        sport_label = format_sport_label(row)
        title = f"{row['year']} {sport_label} State Champion"

        score = None
        if pd.notna(row.get("champion_score")) and pd.notna(row.get("runner_up_score")):
            score = f"{row['champion_score']}-{row['runner_up_score']}"
            if pd.notna(row.get("score_note")):
                score += f" ({row['score_note']})"

        secondary = None
        if score and pd.notna(row.get("runner_up")):
            secondary = f"Defeated {row['runner_up']} {score}"

        card = build_card_descriptor(
            title=title,
            primary_value=champ_name,
            secondary_value=clean_text(secondary),
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

        card["variant"] = "recall"

        if pd.notna(row.get("classification")):
            card["context"] = row["classification"]

        return card

    # --------------------------------------------------
    # Ranking / aggregation → Variant C
    # --------------------------------------------------
    if isinstance(result, pd.DataFrame) and "titles" in result.columns and len(result) >= 1:
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(normalize_school_name(champ_name))

        filters = query.get("filters", {})
        title = format_ranking_title(filters)

        card = build_card_descriptor(
            title=title,
            primary_value=champ_name,
            secondary_value=f"{row['titles']} championships",
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

        card["variant"] = "ranking"
        card["context"] = filters.get("classification", "All Divisions (Combined)")

        return card

    # --------------------------------------------------
    # Numeric aggregation (reserved for Phase 2)
    # --------------------------------------------------
    if isinstance(result, int):
        return build_card_descriptor(
            title="Total State Championships",
            primary_value=str(result),
            secondary_value=None,
            school_id=None,
            details_rows=None,
            school_styles=school_styles,
        )

    return None
