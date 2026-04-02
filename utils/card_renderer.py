import streamlit as st
import streamlit.components.v1 as components


def render_card(card):
    border_color = card.get("primary_color") or "#DDDDDD"

    html_block = f"""
    <div style="
        border: 3px solid {border_color};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        background-color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">
            {card["title"]}
        </div>

        <div style="font-size: 2rem; font-weight: 700; margin-bottom: 4px;">
            {card["primary_value"]}
        </div>
    """

    if card.get("secondary_value"):
        html_block += f"""
        <div style="font-size: 1rem; color: #555;">
            {card["secondary_value"]}
        </div>
        """

    html_block += "</div>"

    # ✅ Render as raw HTML, not Markdown
    components.html(html_block, height=180)

    if card.get("details_rows") is not None:
        with st.expander("Show details"):
            st.dataframe(card["details_rows"], use_container_width=True)
