import streamlit as st

def render_card(card):
    border_color = card.get("accent_color") or "#DDDDDD"

    st.markdown(
        f"""
        <div style="
            border: 3px solid {border_color};
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            background-color: white;
        ">
            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">
                {card["title"]}
            </div>

            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 4px;">
                {card["primary_value"]}
            </div>

            {f'<div style="font-size: 1rem; color: #555;">{card["secondary_value"]}</div>'
             if card.get("secondary_value") else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if card.get("details_rows") is not None:
        with st.expander("Show details"):
            st.dataframe(card["details_rows"], use_container_width=True)
