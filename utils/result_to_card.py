import pandas as pd
import html
import re

from utils.card_descriptor import build_card_descriptor
from utils.sport_config import SPORT_CONFIG


# --------------------------------------------------
# Helpers
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
# Title helpers (SPORT_CONFIG-driven)
# --------------------------------------------------

def format_sport_label(row):
    sport_key = row["sport"].lower()
    gender = row.get("gender", "").title()

    config = SPORT_CONFIG.get(sport_key)

    if config and config.get("gender_policy") == "gendered" and gender:
        return f"{gender} {row['sport'].title()}"

    return row["sport"].title()


def format_ranking_title(filters):
    sport_key = filters.get("sport", "").lower()
    sport = filters.get("sport", "").title()
    gender = filters.get("gender", "").title()

    config = SPORT_CONFIG.get(sport_key)

    if config and config.get("gender_policy") == "gendered" and gender:
        return f"All-Time {gender} {sport} State Championships"

    return f"All-Time {sport} State Championships"


def format_school_summary_title(school_name, filters):
    sport_key = filters.get("sport", "").lower()
    sport = filters.get("sport", "").title()
    gender = filters.get("gender", "").title()

    config = SPORT_CONFIG.get(sport_key)

    if config and config.get("gender_policy") == "gendered" and gender:
        return f"{school_name} {gender} {sport} State Championships"

    return f"{school_name} {sport} State Championships"


# --------------------------------------------------
# Phase 2/3 helper: year + classification annotation
# --------------------------------------------------

def format_year_with_classification(year, classification):
    if not classification or classification == "Overall":
        return str(year)

    if classification == "Division I":
        return f"{year} (D-I)"

    if classification == "Division II":
        return f"{year} (D-II)"

    if classification.startswith("Class"):
        return f"{year} ({classification})"

    return str(year)


# --------------------------------------------------
# Result -> Card mapping
# --------------------------------------------------

def result_to_card(result, explanation, query, school_styles, school_name_lookup):

    intent = query.get("intent")
    filters = query.get("filters", {})

    # --------------------------------------------------
    # TEAM RESULT (recall)
    # --------------------------------------------------
    if (
        intent == "team_result"
        and isinstance(result, pd.DataFrame)
        and len(result) == 1
        and "year" in result.columns
    ):
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
    # RANKING
    # --------------------------------------------------
    if intent == "ranking" and isinstance(result, pd.DataFrame) and "titles" in result.columns:
        if result.empty:
            return None

        title = format_ranking_title(filters)
        top_titles = int(result.iloc[0]["titles"])

        leaders = [
            clean_text(name)
            for name in result["champion"].tolist()
            if pd.notna(name)
        ]

        if len(leaders) == 1:
            champ_name = leaders[0]
            school_id = school_name_lookup.get(normalize_school_name(champ_name))

            card = build_card_descriptor(
                title=title,
                primary_value=champ_name,
                secondary_value=f"{top_titles} championships",
                school_id=school_id,
                details_rows=result,
                school_styles=school_styles,
            )
        else:
            leader_text = ", ".join(leaders[:3])
            if len(leaders) > 3:
                leader_text += f" +{len(leaders) - 3} more"

            card = build_card_descriptor(
                title=title,
                primary_value=leader_text,
                secondary_value=f"{len(leaders)} schools with {top_titles} championships",
                school_id=None,
                details_rows=result,
                school_styles=school_styles,
            )

            card["tie_leaders"] = leaders
            card["tie_summary"] = leader_text

        card["variant"] = "ranking"
        card["context"] = filters.get("classification", "All Divisions (Combined)")
        return card

    # --------------------------------------------------
    # LEGACY NUMERIC AGGREGATION
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
