import streamlit as st
import pandas as pd
import html

from utils.rule_parser import parse_rule_based
from utils.llm_parser import parse_with_llm
from utils.query_executor import execute_query
from utils.query_normalizer import normalize_query
from utils.result_to_card import result_to_card
from utils.card_renderer import render_card
from utils.explainer import render_explanation


# ---------------------------------
# Page configuration
# ---------------------------------

st.set_page_config(
    page_title="Delaware HS Championship Explorer",
    layout="wide",
)

st.title("🏆 Delaware HS Championship Explorer")
st.write(
    "Ask questions about Delaware high school state championships, "
    "such as who won a title in a given year or which school has the most championships."
)


# ---------------------------------
# Session state
# ---------------------------------

if "selected_classification" not in st.session_state:
    st.session_state.selected_classification = None

if "combine_classifications" not in st.session_state:
    st.session_state.combine_classifications = False


# ---------------------------------
# Data loading
# ---------------------------------

@st.cache_data
def load_data():
    team_df = pd.read_csv("data/results_team.csv", encoding="latin-1")
    rec_df = pd.read_csv("data/recognitions.csv", encoding="latin-1")

    for col in team_df.select_dtypes(include="object").columns:
        team_df[col] = (
            team_df[col]
            .map(lambda x: html.unescape(x) if isinstance(x, str) else x)
            .astype(str)
            .str.strip()
        )

    return team_df, rec_df


team_df, rec_df = load_data()


# ---------------------------------
# Helper: should chips appear?
# ---------------------------------

def should_show_classification_chips(query, df):
    filters = query.get("filters", {})
    sport = filters.get("sport")
    year = filters.get("year")

    # If user explicitly named a classification in the text → no chips
    if "classification" in filters:
        return False

    if not sport:
        return False

    subset = df[df["sport"] == sport]
    if year is not None:
        subset = subset[subset["year"] == year]

    return subset["classification"].nunique() > 1


def get_classification_ranges(query, df):
    sport = query["filters"]["sport"]
    year = query["filters"].get("year")

    subset = df[df["sport"] == sport]
    if year is not None:
        subset = subset[subset["year"] == year]

    ranges = {}
    for cls, grp in subset.groupby("classification"):
        ranges[cls] = (grp["year"].min(), grp["year"].max())

    return ranges


# ---------------------------------
# Question input
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Who won the 2022 field hockey state title?",
)

if not question:
    st.stop()


# ---------------------------------
# Parse + normalize
# ---------------------------------

query = parse_rule_based(question)
if query is None:
    query = parse_with_llm(question)

query = normalize_query(query)


# ---------------------------------
# Default ranking behavior
# ---------------------------------

if query.get("intent") == "ranking":
    st.session_state.combine_classifications = True


# ---------------------------------
# Classification chips UI
# ---------------------------------

if should_show_classification_chips(query, team_df):
    sport = query["filters"]["sport"]
    cls_ranges = get_classification_ranges(query, team_df)

    st.markdown("**This sport has multiple championship classifications.**")
    st.markdown("Choose how you’d like to view the results:")

    for cls, (start, end) in sorted(cls_ranges.items()):
        selected = st.session_state.selected_classification == cls

        if selected:
            st.markdown(
                "<div style='border:2px solid #000;padding:6px;border-radius:6px;'>",
                unsafe_allow_html=True
            )

        if st.button(f"{cls} ({start}–{end})"):
            st.session_state.selected_classification = cls
            st.session_state.combine_classifications = False
            st.rerun()

        if selected:
            st.markdown("</div>", unsafe_allow_html=True)

    # Combined option
    combined_selected = st.session_state.combine_classifications

    if combined_selected:
        st.markdown(
            "<div style='border:2px solid #000;padding:6px;border-radius:6px;'>",
            unsafe_allow_html=True
        )

    if st.button("All Divisions (Combined)"):
        st.session_state.selected_classification = None
        st.session_state.combine_classifications = True
        st.rerun()

    if combined_selected:
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------
# Apply classification AFTER UI
# ---------------------------------

if st.session_state.selected_classification:
    query["filters"]["classification"] = st.session_state.selected_classification

if st.session_state.combine_classifications:
    query["filters"].pop("classification", None)


# ---------------------------------
# Execute query
# ---------------------------------

result, explanation = execute_query(query, team_df, rec_df)


# ---------------------------------
# Render
# ---------------------------------

card = result_to_card(
    result=result,
    explanation=explanation,
    query=query,
)

if card:
    render_card(card)
else:
    st.warning("I don’t see a matching record for that question.")


with st.expander("How this answer was found"):
    render_explanation(explanation)
