import html
from streamlit.components.v1 import html as raw_html


# --------------------------------------------------
# Text helpers
# --------------------------------------------------

def safe_text(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


# --------------------------------------------------
# Color helpers
# --------------------------------------------------

def get_colors(card):
    primary = (
        card.get("primary_color")
        or card.get("accent_color")
        or "#444444"
    )

    if isinstance(primary, str) and primary.startswith("#"):
        secondary = primary + "33"
    else:
        secondary = "#dddddd"

    return primary, secondary


# --------------------------------------------------
# Dispatcher
# --------------------------------------------------

def render_card(card):
    variant = card.get("variant", "recall")

    if variant == "ranking":
        render_ranking_card(card)
    else:
        render_recall_card(card)


# --------------------------------------------------
# Recall / Event Card (Phase 1)
# --------------------------------------------------

def render_recall_card(card):
    primary_color, secondary_color = get_colors(card)

    title = safe_text(card.get("title", ""))
    primary_value = safe_text(card.get("primary_value", ""))
    secondary_value = safe_text(card.get("secondary_value"))
    context = safe_text(card.get("context"))

    secondary_html = ""
    if secondary_value:
        secondary_html = f"""
        <div style="font-size:1rem;color:#333;margin-bottom:10px;">
            {secondary_value}
        </div>
        """

    context_html = ""
    if context:
        context_html = f"""
        <div style="
            border-top:1px solid {secondary_color};
            padding-top:8px;
            font-size:0.85rem;
            color:#666;
        ">
            {context}
        </div>
        """

    raw_html(
        f"""
        <div style="
            max-width: 380px;
            padding: 20px;
            margin-bottom: 6px;
            background: #ffffff;
            border-left: 8px solid {primary_color};
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">

            <div style="font-size:0.95rem;color:#555;margin-bottom:6px;">
                {title}
            </div>

            <div style="font-size:1.6rem;font-weight:700;margin-bottom:8px;">
                {primary_value}
            </div>

            {secondary_html}

            {context_html}

        </div>
        """,
        height=260,
    )


# --------------------------------------------------
# Ranking Card (Phase 1)
# --------------------------------------------------

def render_ranking_card(card):
    primary_color, secondary_color = get_colors(card)

    title = safe_text(card.get("title", ""))
    primary_value = safe_text(card.get("primary_value", ""))
    secondary_value = safe_text(card.get("secondary_value"))
    context = safe_text(card.get("context"))

    secondary_html = ""
    if secondary_value:
        secondary_html = f"""
        <div style="
            font-size:1.25rem;
            font-weight:600;
            color:{primary_color};
            margin-bottom:10px;
        ">
            {secondary_value}
        </div>
        """

    context_html = ""
    if context:
        context_html = f"""
        <div style="
            border-top:1px solid {secondary_color};
            padding-top:8px;
            font-size:0.85rem;
            color:#666;
        ">
            {context}
        </div>
        """

    raw_html(
        f"""
        <div style="
            max-width: 380px;
            padding: 20px;
            margin-bottom: 6px;
            background: #ffffff;
            border-left: 8px solid {primary_color};
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">

            <div style="font-size:0.95rem;color:#555;margin-bottom:8px;">
                {title}
            </div>

            <div style="font-size:1.5rem;font-weight:700;margin-bottom:4px;">
                {primary_value}
            </div>

            {secondary_html}

            {context_html}

        </div>
        """,
        height=260,
    )
