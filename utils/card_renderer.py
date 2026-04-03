import streamlit.components.v1 as components
import streamlit as st


def render_card(card):
    border_color = card.get("accent_color") or "#DDDDDD"

    html_block = f"""
    <div style="
        display: flex;
        margin-bottom: 8px;
    ">
        <div style="
            border: 3px solid {border_color};
            border-radius: 12px;
            padding: 14px 18px;
            background-color: #ffffff;
            max-width: 480px;
            width: 100%;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont,
                         'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        ">
            <div style="
                font-size: 0.95rem;
                font-weight: 600;
                margin-bottom: 6px;
                color: #333;
            ">
                {card["title"]}
            </div>

            <div style="
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 4px;
                color: #000;
                line-height: 1.2;
            ">
                {card["primary_value"]}
            </div>
    """

    if card.get("secondary_value"):
        html_block += f"""
            <div style="
                font-size: 1rem;
                color: #555;
                margin-top: 2px;
            ">
                {card["secondary_value"]}
            </div>
        """

    html_block += """
        </div>
    </div>
    """

    # ✅ Increase height so the iframe does not clip native Streamlit elements below
    components.html(html_block, height=140)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ✅ Native Streamlit expander — preserved exactly as you wanted
    if card.get("details_rows") is not None:
        with st.expander("Show details"):
            st.dataframe(card["details_rows"], use_container_width=True)
