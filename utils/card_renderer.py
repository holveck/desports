import streamlit as st


# --------------------------------------------------
# Color helpers
# --------------------------------------------------

def get_colors(card):
    """
    Safely derive primary and secondary colors from the card descriptor.
    Falls back gracefully when colors are missing.
    """
    primary = (
        card.get("primary_color")
        or card.get("accent_color")
        or "#444444"
    )

    if isinstance(primary, str) and primary.startswith("#") and len(primary) == 7:
        secondary = primary + "33"  # translucent divider
    else:
        secondary = "#dddddd"

    return primary, secondary


# --------------------------------------------------
# Dispatcher
# --------------------------------------------------

def render_card(card):
    """
    Entry point called by app.py.
    Chooses layout based on card['variant'].
    """
    variant = card.get("variant", "recall")

    if variant == "ranking":
        render_ranking_card(card)
    else:
        render_recall_card(card)


# --------------------------------------------------
# Variant A: Recall / Event card
# --------------------------------------------------

def render_recall_card(card):
    primary_color, secondary_color = get_colors(card)

    st.markdown(
        f"""
        <div style="
            max-width: 440px;
            margin-bottom: 8px;
            padding: 20px;
            background: #ffffff;
            border-left: 8px solid {primary_color};
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">

            <div style="
                font-size: 0.95rem;
                color: #555;
                margin-bottom: 6px;
            ">
                {card.get("title","")}
            </div>

            <div style="
                font-size: 1.6rem;
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 8px;
                color: #111;
            ">
                {card.get("primary_value","")}
            </div>

            <div style="
                font-size: 1rem;
                color: #333;
                margin-bottom: 10px;
            ">
                {card.get("secondary_value","")}
            </div>

            <div style="
                border-top: 1px solid {secondary_color};
                padding-top: 8px;
                font-size: 0.85rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Variant C: Ranking / Leaderboard card
# --------------------------------------------------

def render_ranking_card(card):
    primary_color, secondary_color = get_colors(card)

    st.markdown(
        f"""
        <div style="
            max-width: 440px;
            margin-bottom: 8px;
            padding: 20px;
            background: #ffffff;
            border-left: 8px solid {primary_color};
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">

            <div style="
                font-size: 0.95rem;
                color: #555;
                margin-bottom: 8px;
            ">
                {card.get("title","")}
            </div>

            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 4px;
                color: #111;
            ">
                {card.get("primary_value","")}
            </div>

            <div style="
                font-size: 1.25rem;
                font-weight: 600;
                color: {primary_color};
                margin-bottom: 10px;
            ">
                {card.get("secondary_value","")}
            </div>

            <div style="
                border-top: 1px solid {secondary_color};
                padding-top: 8px;
                font-size: 0.85rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )
