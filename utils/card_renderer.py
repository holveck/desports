import streamlit as st
from streamlit.components.v1 import html as raw_html


def render_card(card):
    variant = card.get("variant", "recall")

    if variant == "ranking":
        render_ranking_card(card)
    else:
        render_recall_card(card)


def render_recall_card(card):
    raw_html(
        f"""
        <div style="
            max-width: 440px;
            margin: 0 auto 16px;
            padding: 22px;
            background: white;
            border-left: 10px solid {card['primary_color']};
            border-radius: 12px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont;
        ">
            <div style="font-size: 0.95rem; color: #555; margin-bottom: 6px;">
                {card['title']}
            </div>

            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 8px;">
                {card['primary_value']}
            </div>

            <div style="font-size: 1rem; color: #333;">
                {card.get("secondary_value", "")}
            </div>

            <div style="
                margin-top: 14px;
                padding-top: 8px;
                border-top: 1px solid {card['secondary_color']}33;
                font-size: 0.9rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>
        </div>
        """,
        height=260,
    )


def render_ranking_card(card):
    raw_html(
        f"""
        <div style="
            max-width: 440px;
            margin: 0 auto 16px;
            padding: 22px;
            background: white;
            border-left: 10px solid {card['primary_color']};
            border-radius: 12px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont;
        ">
            <div style="font-size: 0.95rem; color: #555; margin-bottom: 8px;">
                {card['title']}
            </div>

            <div style="font-size: 1.6rem; font-weight: 700; margin-bottom: 4px;">
                {card['primary_value']}
            </div>

            <div style="
                font-size: 1.4rem;
                font-weight: 600;
                color: {card['secondary_color']};
                margin-bottom: 10px;
            ">
                {card['secondary_value']}
            </div>

            <div style="
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px solid {card['secondary_color']}33;
                font-size: 0.9rem;
                color: #666;
            ">
                {card.get("context","")}
            </div>
        </div>
        """,
        height=260,
    )
