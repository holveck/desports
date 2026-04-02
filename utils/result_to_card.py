import pandas as pd
from utils.card_descriptor import build_card_descriptor

def result_to_card(result, explanation, school_styles):
    """
    Convert executor output into a generic card descriptor.
    """

    # Case 1: Single-row championship result
    if hasattr(result, "iloc") and len(result) == 1:
        row = result.iloc[0]

        score = None
        if pd.notna(row.get("champion_score")) and pd.notna(row.get("runner_up_score")):
            score = f'{row["champion_score"]}–{row["runner_up_score"]}'
            if pd.notna(row.get("score_note")):
                score += f' ({row["score_note"]})'

        secondary = f'Defeated {row["runner_up"]} {score}' if score else None

        return build_card_descriptor(
            title=f'{row["year"]} {row["classification"]} {row["sport"].title()} State Champion',
            primary_value=row["champion"],
            secondary_value=secondary,
            school_id=row.get("school_id"),
            details_rows=result,
            school_styles=school_styles,
        )

    # Case 2: Ranking (most titles)
    if hasattr(result, "iloc") and "titles" in result.columns:
        top = result.iloc[0]
        return build_card_descriptor(
            title="Most championships",
            primary_value=top["champion"],
            secondary_value=f'{top["titles"]} titles',
            school_id=None,  # can enhance later
            details_rows=result,
            school_styles=school_styles,
        )

    # Case 3: Aggregation (numeric answer)
    if isinstance(result, int):
        return build_card_descriptor(
            title="Total championships",
            primary_value=str(result),
            secondary_value=None,
            details_rows=None,
            school_styles=school_styles,
        )

    return None
