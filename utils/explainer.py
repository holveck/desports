import streamlit as st


def render_explanation(steps):
    if not steps:
        st.write("No explanation available.")
        return

    for step in steps:
        st.write(step)
