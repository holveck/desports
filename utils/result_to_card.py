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
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(normalize_school_name(champ_name))

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
    # SCHOOL SUMMARY (Phase 2 + Phase 3)
    # --------------------------------------------------
    if intent == "school_summary" and isinstance(result, pd.DataFrame):

        if result.empty:
            return None

        school_name = clean_text(result.iloc[0]["champion"])
        school_id = filters.get("school_id")
        classification_filter = filters.get("classification")

        if classification_filter:
            scoped_df = result[result["classification"] == classification_filter]
            scope_label = classification_filter
        else:
            scoped_df = result
            if filters.get("since_year"):
                scope_label = f"Since {filters['since_year']}"
            else:
                scope_label = "All-time total"

        total_titles = len(scoped_df)

        years = (
            scoped_df
            .sort_values("year")
            .apply(
                lambda row: format_year_with_classification(
                    int(row["year"]),
                    row.get("classification")
                ),
                axis=1
            )
            .tolist()
        )

        title = format_school_summary_title(school_name, filters)

        card = build_card_descriptor(
            title=title,
            primary_value=f"{total_titles} championships",
            secondary_value=", ".join(years),
            school_id=school_id,
            details_rows=scoped_df,
            school_styles=school_styles,
        )

        card["variant"] = "school_summary"
        card["context"] = scope_label
        card["details_years"] = years

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
