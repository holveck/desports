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


def result_to_card(result, explanation, school_styles, school_name_lookup):

    # --- Champion lookup ---
    if isinstance(result, pd.DataFrame) and len(result) == 1 and "year" in result.columns:
        row = result.iloc[0]
        champ_name = clean_text(row["champion"])

        school_id = school_name_lookup.get(normalize_school_name(champ_name))

        score = None
        if pd.notna(row.get("champion_score")) and pd.notna(row.get("runner_up_score")):
            score = f"{row['champion_score']}-{row['runner_up_score']}"
            if pd.notna(row.get("score_note")):
                score = score + " (" + row["score_note"] + ")"

        secondary = None
        if score and pd.notna(row.get("runner_up")):
            secondary = "Defeated " + row["runner_up"] + " " + score

        return build_card_descriptor(
            title=f"{row['year']} {row['classification']} {row['sport'].title()} State Champion",
            primary_value=champ_name,
            secondary_value=clean_text(secondary),
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

    # --- Ranking ---
    if isinstance(result, pd.DataFrame) and "titles" in result.columns and len(result) >= 1:
        row = result.iloc[0]
        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(normalize_school_name(champ_name))

        return build_card_descriptor(
            title=f"Most {row.get('gender', '').title()} {row.get('sport', '').title()} State Championships".strip(),
            primary_value=champ_name,
            secondary_value=str(row["titles"]) + " titles",
            school_id=school_id,
            details_rows=result,
            school_styles=school_styles,
        )

    # --- Aggregation ---
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
