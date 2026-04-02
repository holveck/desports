import pandas as pd
import html
import re
from utils.card_descriptor import build_card_descriptor


# --------------------------------------------------
# Normalization utilities
# --------------------------------------------------

def normalize_school_name(name: str) -> str:
    """
    Normalize school names so results_team.csv names
    reliably match schools.csv canonical_name.
    """
    return (
        str(name)
        .replace("\u00a0", " ")   # normalize non-breaking spaces
        .lower()
        .strip()
        .replace("’", "'")
        .replace("–", "-")
    )


def clean_text(value):
    if value is None:
        return None

    value = str(value)

    # repeatedly unescape HTML entities until stable
    prev = None
    while value != prev:
        prev = value
        value = html.unescape(value)

    # strip any literal HTML tags (defensive)
    value = re.sub(r"<[^>]+>", "", value)

    return value.strip()


# --------------------------------------------------
# Result → Card mapper
# --------------------------------------------------

def result_to_card(result, explanation, school_styles, school_name_lookup):
    """
    Convert executor output into a card descriptor.
    Branches only on result shape, never on intent.
    """

    # -------------------------------
    # Case 1: single championship row
    # -------------------------------
    if (
        isinstance(result, pd.DataFrame)
        and len(result) == 1
        and "year" in result.columns
    ):
        row = result.iloc[0]

        champ_name = clean_text(row["champion"])
        school_id = school_name_lookup.get(
            normalize_school_name(champ_name)
        )

        score = None
        if (
            pd.notna(row.get("champion_score"))
            and pd.notna(row.get("runner_up_score"))
        ):
            score = f'{row["champion_score"]}–{row["runner_up_score"]}'
            if pd.notna(row.get("score_note")):
                score += f' ({row["score_note"]})'

        secondary = (
            f'Defeated {row["runner_up"]} {score}'
            if score and pd.notna(row.get("runner_up"))
            else None
        )

        return build_card_descriptor(
            title=f'{row["year"]} {row["classification"]} {row["sport"].title()} State Champion',
            primary_value=champ_name,
            secondary_value=clean_text(secondary),
