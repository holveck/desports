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
from utils.schools import get_school_name_lookup, get_school_styles
from utils.schools_page import render_school_page


# ---------------------------------
# Page configuration
# ---------------------------------

st.set_page_config(
    page_title="Delaware High School Sports Handbook",
    layout="wide",
)


# ---------------------------------
# Session state
# ---------------------------------

if "main_view" not in st.session_state:
    st.session_state.main_view = "Home"

if "selected_classification" not in st.session_state:
    st.session_state.selected_classification = None

if "combine_classifications" not in st.session_state:
    st.session_state.combine_classifications = False

if "last_question" not in st.session_state:
    st.session_state.last_question = None

if "selected_school" not in st.session_state:
    st.session_state.selected_school = None


def reset_classification_state():
    st.session_state.selected_classification = None
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


@st.cache_data
def load_schools():
    schools_df = pd.read_csv("data/schools.csv", encoding="utf-8")

    for col in schools_df.select_dtypes(include="object").columns:
        schools_df[col] = schools_df[col].fillna("").astype(str).str.strip()

    schools_df = schools_df.sort_values("canonical_name").reset_index(drop=True)
    return schools_df


team_df, rec_df = load_data()
schools_df = load_schools()
school_styles = get_school_styles()
school_name_lookup = get_school_name_lookup()


# ---------------------------------
# Chip helpers
# ---------------------------------

def should_show_classification_chips(query, df):
    filters = query.get("filters", {})
    sport = filters.get("sport")
    year = filters.get("year")

    if query.get("intent") == "school_summary":
        return False

    if filters.get("classification") is not None:
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

    return {
        cls: (grp["year"].min(), grp["year"].max())
        for cls, grp in subset.groupby("classification")
    }


# ---------------------------------
# View renderers
# ---------------------------------

def render_home_page():
    question = st.text_input(
        "Ask a question:",
        placeholder="e.g. Who has won the most Division I field hockey state titles?",
    )

    if not question:
        return

    if st.session_state.last_question is not None and question != st.session_state.last_question:
        reset_classification_state()

    st.session_state.last_question = question

    query = parse_rule_based(question)
    if query is None:
        query = parse_with_llm(question)

    query = normalize_query(query)

    if (
        query.get("intent") == "ranking"
        and query["filters"].get("classification") is None
        and st.session_state.selected_classification is None
        and not st.session_state.combine_classifications
    ):
        st.session_state.combine_classifications = True

    if should_show_classification_chips(query, team_df):
        sport = query["filters"]["sport"]
        year = query["filters"].get("year")
        cls_ranges = get_classification_ranges(query, team_df)

        st.markdown("**This sport has had multiple championship formats over time.**")
        st.markdown("View results by division:")

        show_combined = query.get("intent") == "ranking"
        total_cols = len(cls_ranges) + (1 if show_combined else 0)
        cols = st.columns(total_cols)

        col_index = 0

        for cls, (start, end) in sorted(cls_ranges.items()):
            selected = (
                st.session_state.selected_classification == cls
                and not st.session_state.combine_classifications
            )

            with cols[col_index]:
                label = cls if year is not None else f"{cls} ({start}–{end})"

                if st.button(label, key=f"cls-{cls}"):
                    st.session_state.selected_classification = cls
                    st.session_state.combine_classifications = False
                    st.rerun()

                if selected:
                    st.caption("✓ Selected")

            col_index += 1

        if show_combined:
            with cols[col_index]:
                if st.button("All Divisions (Combined)", key="cls-combined"):
                    st.session_state.selected_classification = None
                    st.session_state.combine_classifications = True
                    st.rerun()

                if st.session_state.combine_classifications:
                    st.caption("✓ Selected")

    if (
        st.session_state.selected_classification
        and query.get("intent") != "school_summary"
    ):
        query["filters"]["classification"] = st.session_state.selected_classification

    if (
        st.session_state.combine_classifications
        and query.get("intent") == "ranking"
        and query["filters"].get("classification") is None
    ):
        query["filters"].pop("classification", None)

    result, explanation = execute_query(query, team_df, rec_df)

    card = result_to_card(
        result=result,
        explanation=explanation,
        query=query,
        school_styles=school_styles,
        school_name_lookup=school_name_lookup,
    )

    if card:
        render_card(card)

        if card.get("details_rows") is not None:
            with st.expander("Show details"):

                if card.get("details_years"):
                    st.markdown("**Years won:**")
                    st.write(", ".join(card["details_years"]))
                    st.markdown("---")

                st.dataframe(card["details_rows"], use_container_width=True)

    else:
        st.warning("I don’t see a matching record for that question.")

    with st.expander("How this answer was found"):
        render_explanation(explanation)


def render_schools_page():
    render_school_page(schools_df, team_df)


# ---------------------------------
# App header + navigation
# ---------------------------------

st.title("🐔 Delaware High School Sports Handbook")
st.write(
    "Explore state championship history across all high school sports."
)

selected_view = st.pills(
    "Navigation",
    options=["Home", "Schools"],
    selection_mode="single",
    default=st.session_state.main_view,
    key="main_view_pills",
    label_visibility="collapsed",
)

if selected_view is None:
    selected_view = "Home"

st.session_state.main_view = selected_view


# ---------------------------------
# Route view
# ---------------------------------

if st.session_state.main_view == "Home":
    render_home_page()
else:
    render_schools_page()
