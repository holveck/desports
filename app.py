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
    page_title="Delaware High School Sports Handbook",
    layout="wide",
)

st.title("🐔 Delaware High School Sports Handbook")
st.write(
    "Explore state championship history across all high school sports."
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
# Chip helpers
# ---------------------------------

def should_show_classification_chips(query, df):
    filters = query.get("filters", {})
    sport = filters.get("sport")
    year = filters.get("year")

    # Never show chips for school summaries
    if query.get("intent") == "school_summary":
        return False

    # Explicit classification suppresses chips
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
# Question input
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Who has won the most Division I field hockey state titles?",
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
# Ranking default (combined totals ONCE)
# ✅ FIX: only default if classification not explicitly provided
# ---------------------------------

if (
    query.get("intent") == "ranking"
    and query["filters"].get("classification") is None
    and st.session_state.selected_classification is None
    and not st.session_state.combine_classifications
):
    st.session_state.combine_classifications = True


# ---------------------------------
# Classification chips
# ---------------------------------

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


# ---------------------------------
# Apply classification AFTER UI
# ✅ FIX: do not override parser classification
# ---------------------------------

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


# ---------------------------------
# Execute query
# ---------------------------------

result, explanation = execute_query(query, team_df, rec_df)


# ---------------------------------
# Render result
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

    # ---------------------------------
    # Show details
    # ---------------------------------

    if card.get("details_rows") is not None:
        with st.expander("Show details"):

            if card.get("details_years"):
                st.markdown("**Years won:**")
                st.write(", ".join(card["details_years"]))
                st.markdown("---")

            st.dataframe(card["details_rows"], use_container_width=True)

else:
    st.warning("I don’t see a matching record for that question.")


# ---------------------------------
# Explanation
# ---------------------------------

with st.expander("How this answer was found"):
    render_explanation(explanation)
