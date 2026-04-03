import streamlit as st
import pandas as pd
import html

from utils.rule_parser import parse_rule_based
from utils.llm_parser import parse_with_llm
from utils.query_executor import execute_query
from utils.query_normalizer import normalize_query
from utils.result_to_card import result_to_card
from utils.card_renderer import render_card
from utils.clarifier import needs_clarification, get_clarifying_prompts
from utils.explainer import render_explanation


# ---------------------------------
# Page configuration
# ---------------------------------

st.set_page_config(
    page_title="Delaware HS Championship Explorer",
    layout="wide",
)

st.title("🏆 Delaware High School Championship Explorer")
st.write(
    "Ask questions about Delaware high school state championships, "
    "such as who won a title in a given year or which school has the most championships."
)


# ---------------------------------
# Data loading
# ---------------------------------

@st.cache_data
def load_data():
    team_df = pd.read_csv(
        "data/results_team.csv",
        encoding="latin-1",
        engine="python",
    )

    rec_df = pd.read_csv(
        "data/recognitions.csv",
        encoding="latin-1",
        engine="python",
    )

    # defensively normalize entity-encoded strings
    for col in team_df.select_dtypes(include="object").columns:
        team_df[col] = (
            team_df[col]
            .map(lambda x: html.unescape(x) if isinstance(x, str) else x)
            .astype(str)
            .str.strip()
        )

    return team_df, rec_df


@st.cache_data
def load_school_styles():
    df = pd.read_csv("data/schools.csv")
    return {
        row["school_id"]: {
            "primary_color": row.get("primary_color"),
            "secondary_color": row.get("secondary_color"),
        }
        for _, row in df.iterrows()
    }


@st.cache_data
def load_school_name_lookup():
    """
    Build canonical_name → school_id mapping,
    using the SAME normalization as result_to_card.
    """
    df = pd.read_csv("data/schools.csv")
    return {
        (
            str(row["canonical_name"])
            .replace("\u00a0", " ")
            .lower()
            .strip()
            .replace("’", "'")
            .replace("–", "-")
        ): row["school_id"]
        for _, row in df.iterrows()
    }


team_df, rec_df = load_data()
school_styles = load_school_styles()
school_name_lookup = load_school_name_lookup()


# ---------------------------------
# Question input
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Who won the 2022 Division II field hockey state championship?",
)

if not question:
    st.stop()


# ---------------------------------
# Parse + normalize query
# ---------------------------------

query = parse_rule_based(question)
if query is None:
    query = parse_with_llm(question)

query = normalize_query(query)


# ---------------------------------
# Clarification handling
# ---------------------------------

if needs_clarification(query):
    for prompt in get_clarifying_prompts(query):
        st.info(prompt)
    st.stop()


# ---------------------------------
# Execute query
# ---------------------------------

result, explanation = execute_query(query, team_df, rec_df)


# ---------------------------------
# Render answer card
# ---------------------------------

card = result_to_card(
    result=result,
    explanation=explanation,
    query=query,
    school_styles=school_styles,
    school_name_lookup=school_name_lookup,
)

if card:
    render_card(card)
else:
    st.warning("I don’t see a matching record for that question.")


# ---------------------------------
# Explanation
# ---------------------------------

with st.expander("How this answer was found"):
    render_explanation(explanation)
