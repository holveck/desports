import pandas as pd
import re
from utils.card_descriptor import build_card_descriptor


# --------------------------------------------------
# Utilities
# --------------------------------------------------

def clean_text(value):
    """
    Enforce a hard invariant:
    card text fields may NEVER contain HTML.
    """
    if value is None:
        return None
    value = str(value)
    # Strip any legacy or accidental HTML tags
    value = re.sub(r"<[^>]*>", "", value)
    return value.strip()


# --------------------------------------------------
# Result → Card mapper
# --------------------------------------------------

def result_to_card(result, explanation, school_styles):
    """
    Convert executor output into a generic card descriptor.

    This function branches ONLY on result shape,
    never on intent type.
    """

    # --------------------------------------------------
    # Case 1: Single championship row (simple recall)
    # --------------------------------------------------
    if (
        isinstance(result, pd.DataFrame)
        and len(result) == 1
        and "year" in result.columns
    ):
        row = result.iloc[0]

        # Build score string with optional score_note
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
            title=clean_text(
                f'{row["year"]} {row["classification"]} {row["sport"].title()} State Champion'
            ),
            primary_value=clean_text(row["champion"]),
            secondary_value=clean_text(secondary),
            school_id=row.get("school_id"),
            details_rows=result,
            school_styles=school_styles,
        )

    # --------------------------------------------------
    # Case 2: Ranking result (e.g. "most titles")
    # --------------------------------------------------
    if (
        isinstance(result, pd.DataFrame)
        and {"champion", "titles"}.issubset(result.columns)
        and len(result) >= 1
    ):
        top = result.iloc[0]

        return build_card_descriptor(
            title="Most state championships",
            primary_value=clean_text(top["champion"]),
            secondary_value=clean_text(f'{top["titles"]} titles'),
            school_id=None,
            details_rows=result,
            school_styles=school_styles,
        )

    # --------------------------------------------------
    # Case 3: Aggregation (numeric answer)
    # --------------------------------------------------
    if isinstance(result, int):
        return build_card_descriptor(
            title="Total state championships",
            primary_value=clean_text(str(result)),
            secondary_value=None,
            school_id=None,
            details_rows=None,
            school_styles=school_styles,
        )

    # --------------------------------------------------
    # Fallback (should be rare)
    # --------------------------------------------------
    return None
