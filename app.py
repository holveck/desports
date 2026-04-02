import streamlit as st
import pandas as pd

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
    layout="wide"
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
        engine="python"
    )
    rec_df = pd.read_csv(
        "data/recognitions.csv",
        encoding="latin-1",
        engine="python"
    )

    # Normalize champion strings to avoid hidden whitespace issues
    team_df["champion"] = (
        team_df["champion"]
        .astype(str)
        .str.strip()
    )

    return team_df, rec_df


@st.cache_data
def load_school_styles():
    df = pd.read_csv("data/schools.csv")
    styles = {}

    for _, row in df.iterrows():
        styles[row["school_id"]] = {
            "primary_color": row.get("primary_color"),
            "secondary_color": row.get("secondary_color"),
        }

    return styles


team_df, rec_df = load_data()
school_styles = load_school_styles()


# ---------------------------------
# Question input
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Who won the 2022 Division II field hockey state championship?"
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
    prompts = get_clarifying_prompts(query)
    for prompt in prompts:
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
    school_styles=school_styles,
)
st.stop()
if card:
    render_card(card)
else:
    st.warning("I don’t see a matching record for that question.")


# ---------------------------------
# Optional explanation block
# ---------------------------------

with st.expander("How this answer was found"):
    render_explanation(explanation)
