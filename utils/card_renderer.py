import streamlit as st
from streamlit.components.v1 import html as raw_html


# --------------------------------------------------
# Color helpers
# --------------------------------------------------

def get_colors(card):
    """
    Safely derive primary and secondary colors from the card descriptor.

    Priority:
    1. Explicit primary_color / secondary_color (if ever provided)
    2. Existing accent_color (from build_card_descriptor)
    3. Neutral fallbacks
    """
    primary = (
        card.get("primary_color")
        or card.get("accent_color")
        or "#444444"
    )

    if primary.startswith("#") and len(primary) == 7:
        secondary = primary + "33"   # translucent version
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

    raw_html(
        f"""
        <div style="
            max-width: 440px;
            margin: 0 0 18px;
            padding: 22px;
            background: #ffffff;
            border-left: 10px solid {primary_color};
            border-radius: 12px;
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
                font-size: 1.65rem;
                font-weight: 700;
                color: #111;
                line-height: 1.2;
                margin-bottom: 10px;
            ">
                {card.get("primary_value","")}
            </div>

            <div style="
                font-size: 1rem;
                color: #333;
                margin-bottom: 16px;
            ">
                {card.get("secondary_value","")}
            </div>

            <div style="
                border-top: 1px solid {secondary_color};
                padding-top: 10px;
                font-size: 0.85rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>

        </div>
        """,
        height=260,
    )


# --------------------------------------------------
# Variant C: Ranking / Leaderboard card
# --------------------------------------------------

def render_ranking_card(card):
    primary_color, secondary_color = get_colors(card)

    raw_html(
        f"""
        <div style="
            max-width: 440px;
            margin: 0 0 18px;
            padding: 22px;
            background: #ffffff;
            border-left: 10px solid {primary_color};
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">

            <div style="
                font-size: 0.95rem;
                color: #555;
                margin-bottom: 10px;
            ">
                {card.get("title","")}
            </div>

            <div style="
                font-size: 1.55rem;
                font-weight: 700;
                color: #111;
                margin-bottom: 6px;
            ">
                {card.get("primary_value","")}
            </div>

            <div style="
                font-size: 1.3rem;
                font-weight: 600;
                color: {primary_color};
                margin-bottom: 14px;
            ">
                {card.get("secondary_value","")}
            </div>

            <div style="
                border-top: 1px solid {secondary_color};
                padding-top: 10px;
                font-size: 0.85rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>

        </div>
        """,
        height=260,
    )
