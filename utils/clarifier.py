"""
Clarification utilities.

This file is responsible ONLY for:
- deciding WHAT needs clarification (based on parser output)
- generating HUMAN-READABLE clarification prompts

It does NOT inspect DataFrames or guess ambiguity.
"""

from typing import List, Dict


# ---------------------------
# Human-readable prompts
# ---------------------------

CLARIFICATION_PROMPTS = {
    "year": "Which year are you asking about?",
    "gender": "Is this for boys or girls?",
    "classification": (
        "There were multiple champions. Which classification did you mean?"
    ),
}


# ---------------------------
# Public API
# ---------------------------

def needs_clarification(query: Dict) -> bool:
    """
    Return True if the parser has identified missing required fields.
    """
    return bool(query.get("needs_clarification"))


def get_clarifying_prompts(query: Dict) -> List[str]:
    """
    Convert missing fields into user-facing clarification prompts.
    """
    prompts = []
    for field in query.get("needs_clarification", []):
        prompt = CLARIFICATION_PROMPTS.get(
            field,
            f"Please specify {field}."
        )
        prompts.append(prompt)
    return prompts
