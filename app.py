import streamlit as st
import pandas as pd

from utils.rule_parser import parse_rule_based
from utils.llm_parser import parse_with_llm
from utils.query_executor import execute_query
from utils.clarifier import needs_clarification, build_clarifying_question
from utils.explainer import render_explanation

st.set_page_config(page_title="Delaware HS Champions", layout="wide")

st.title("🏆 Delaware High School Championship Explorer")
st.write("Ask questions about Delaware high school state championships.")

team_df = pd.read_csv("data/results_team.csv")
rec_df = pd.read_csv("data/recognitions.csv")

question = st.text_input("Ask a question:")

if question:
    query = parse_rule_based(question)
    if not query:
        query = parse_with_llm(question)

    result, explanation = execute_query(query, team_df, rec_df)

    if isinstance(result, pd.DataFrame):
        if needs_clarification(result):
            st.warning("I found multiple possible answers. Can you clarify?")
            st.dataframe(build_clarifying_question(result))
        else:
            st.subheader("Answer")
            st.dataframe(result)
            st.markdown(render_explanation(explanation))
    else:
        st.subheader("Answer")
        st.write(result)
        st.markdown(render_explanation(explanation))
