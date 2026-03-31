import streamlit as st
import pandas as pd

from utils.rule_parser import parse_rule_based
from utils.llm_parser import parse_with_llm
from utils.query_executor import execute_query
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
# Load data
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

    # Normalize champion names to avoid hidden whitespace / Unicode issues
    team_df["champion"] = (
        team_df["champion"]
        .astype(str)
        .str.strip()
    )

    return team_df, rec_df

team_df, rec_df = load_data()
# ---------------------------------
# Question input
# ---------------------------------

question = st.text_input(
    "Ask a question:",
    placeholder="e.g., Who won the girls lacrosse state championship in 2023?"
)


# ---------------------------------
# Main app logic
# ---------------------------------

if question:
    # 1. Parse using rule-based parser first
    query = parse_rule_based(question)

    # 2. Fall back to LLM parser if rule-based fails
    if query is None:
        query = parse_with_llm(question)

    # 3. Check whether clarification is required
    if needs_clarification(query):
        st.warning("I need a bit more information to answer that.")

        for prompt in get_clarifying_prompts(query):
            st.write(f"- {prompt}")

        # IMPORTANT: stop execution until user clarifies
        st.stop()

    # 4. Execute the query only when it is complete
    result, explanation = execute_query(query, team_df, rec_df)

    # ---------------------------------
    # Render the answer
    # ---------------------------------

    st.subheader("Answer")

    if isinstance(result, pd.DataFrame):
        if result.empty:
            st.info("I don’t see a matching record for that question in the dataset.")
        else:
            st.dataframe(result, use_container_width=True)
    else:
        st.write(result)

    # ---------------------------------
    # Render explanation
    # ---------------------------------

    if explanation:
        st.markdown(render_explanation(explanation))
