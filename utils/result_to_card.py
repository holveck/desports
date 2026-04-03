import pandas as pd
import html
import re

from utils.card_descriptor import build_card_descriptor


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

    value = re.sub(r"<[^>]+>", "", value)
    return value.strip()


def result_to_card(result, explanation, query, school_styles, school_name_lookup):

    # --------------------------------------------------
    # Champion recall (single row result)
    # --------------------------------------------------
    if isinstance(result, pd.DataFrame) and len(result) == 1 and "year" in result.columns:
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(
            normalize_school_name(champ_name)
        )

        title = (
            str(row["year"]) + " " +
            row["gender"].title() + " " +
            row["sport"].title() +
            " State Champion"
        )

        score = None
        if pd.notna(row.get("champion_score")) and pd.notna(row.get("runner_up_score")):
            score = str(row["champion_score"]) + "-" + str(row["runner_up_score"])
            if pd.notna(row.get("score_note")):
                score = score + " (" + str(row["score_note"]) + ")"

        secondary = None
        if score and pd.notna(row.get("runner_up")):
            secondary = "Defeated " + str(row["runner_up"]) + " " + score

        return build_card_descriptor(
            title=title,
            primary_value=champ_name,
            secondary_value=clean_text(secondary),
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

    # --------------------------------------------------
    # Ranking result (aggregation)
    # --------------------------------------------------
    if isinstance(result, pd.DataFrame) and "titles" in result.columns and len(result) >= 1:
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(
            normalize_school_name(champ_name)
        )

        filters = query.get("filters", {})
        sport = filters.get("sport", "")
        gender = filters.get("gender", "")

        if gender:
            title = "Most " + gender.title() + " " + sport.title() + " State Championships"
        else:
            title = "Most " + sport.title() + " State Championships"

        return build_card_descriptor(
            title=title,
            primary_value=champ_name,
            secondary_value=str(row["titles"]) + " titles",
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

    # --------------------------------------------------
    # Numeric aggregation
    # --------------------------------------------------
    if isinstance(result, int):
        return build_card_descriptor(
            title="Total state championships",
            primary_value=str(result),
            secondary_value=None,
            school_id=None,
            details_rows=None,
            school_styles=school_styles,
        )

    return None
