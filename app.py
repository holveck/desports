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

st.title("🏆 Delaware HS Championship Explorer")
st.write(
    "Ask questions about Delaware high school state championships, "
    "such as who won a title in a given year or which school has the most championships."
)


# ---------------------------------
# SESSION STATE
# ---------------------------------

if "selected_classification" not in st.session_state:
    st.session_state.selected_classification = None

if "combine_classifications" not in st.session_state:
    st.session_state.combine_classifications = False


# ---------------------------------
# DATA
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
    df = pd.read_csv("data/schools.csv")
    return {
        row["canonical_name"].lower().strip(): row["school_id"]
        for _, row in df.iterrows()
    }


team_df, rec_df = load_data()
school_styles = load_school_styles()
school_name_lookup = load_school_name_lookup()


# ---------------------------------
# CHIP HELPERS
# ---------------------------------

def get_relevant_classification_ranges(query, df):
    sport = query["filters"].get("sport")
    year = query["filters"].get("year")

    subset = df[df["sport"] == sport]
    if year is not None:
        subset = subset[subset["year"] == year]

    ranges = {}
    for cls, grp in subset.groupby("classification"):
        ranges[cls] = (int(grp["year"].min()), int(grp["year"].max()))

    return ranges


def should_show_classification_chips(query, df):
    if query.get("classification_from_query"):
        return False

    sport = query["filters"].get("sport")
    if not sport:
        return False

    subset = df[df["sport"] == sport]
    year = query["filters"].get("year")
    if year is not None:
        subset = subset[subset["year"] == year]

    return subset["classification"].nunique() > 1


def get_sport_year_span(sport, df):
    subset = df[df["sport"] == sport]
    return int(subset["year"].min()), int(subset["year"].max())


def is_selected(cls):
    return (
        st.session_state.selected_classification == cls
        and not st.session_state.combine_classifications
    )


def is_selected_combined():
    return st.session_state.combine_classifications is True


# ---------------------------------
# INPUT
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Who won the 2022 field hockey state title?",
)

if not question:
    st.stop()


# ---------------------------------
# PARSE + NORMALIZE
# ---------------------------------

query = parse_rule_based(question)
if query is None:
    query = parse_with_llm(question)

query = normalize_query(query)
query["classification_from_query"] = "classification" in query.get("filters", {})


# ---------------------------------
# RANKING DEFAULT: COMBINED
# ---------------------------------

if query.get("intent") == "ranking" and not query["classification_from_query"]:
    st.session_state.combine_classifications = True


# ---------------------------------
# APPLY SESSION STATE
# ---------------------------------

if st.session_state.selected_classification:
    query["filters"]["classification"] = st.session_state.selected_classification

if st.session_state.combine_classifications:
    query["filters"].pop("classification", None)


# ---------------------------------
# CLARIFIER (NON‑CLASSIFICATION ONLY)
# ---------------------------------

if (
    query.get("intent") != "ranking"
    and needs_clarification(query)
    and not should_show_classification_chips(query, team_df)
    and st.session_state.selected_classification is None
    and not st.session_state.combine_classifications
):
    for prompt in get_clarifying_prompts(query):
        st.info(prompt)
    st.stop()


# ---------------------------------
# CHIPS
# ---------------------------------

if should_show_classification_chips(query, team_df):
    sport = query["filters"].get("sport")

    st.markdown("**This sport has multiple championship structures.**")
    st.markdown("Choose how you’d like to view the results:")

    cls_ranges = get_relevant_classification_ranges(query, team_df)
    sport_start, sport_end = get_sport_year_span(sport, team_df)

    for cls, (start, end) in sorted(cls_ranges.items()):
        if cls.lower() == "overall":
            label = f"Overall ({start}–{end})"
            help_text = "Schools competed for one championship."
        else:
            label = f"{cls} ({start}–{end})"
            help_text = None

        if is_selected(cls):
            st.markdown(
                "<div style='border:2px solid #000;padding:6px;border-radius:6px;'>",
                unsafe_allow_html=True
            )

        if st.button(label, help=help_text):
            st.session_state.selected_classification = cls
            st.session_state.combine_classifications = False
            st.rerun()

        if is_selected(cls):
            st.markdown("</div>", unsafe_allow_html=True)

    combined_label = "All Divisions"
    combined_help = f"Includes all championships from {sport_start} to {sport_end}."

    if is_selected_combined():
        st.markdown(
            "<div style='border:2px solid #000;padding:6px;border-radius:6px;'>",
            unsafe_allow_html=True
        )

    if st.button(combined_label, help=combined_help):
        st.session_state.selected_classification = None
        st.session_state.combine_classifications = True
        st.rerun()

    if is_selected_combined():
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------
# EXECUTE
# ---------------------------------

result, explanation = execute_query(query, team_df, rec_df)


# ---------------------------------
# RENDER
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
# EXPLANATION
# ---------------------------------

with st.expander("How this answer was found"):
    render_explanation(explanation)
