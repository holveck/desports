import html
import re
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

def safe_color(value, default):
    if not isinstance(value, str):
        return default

    value = value.strip()

    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value

    if re.fullmatch(r"#[0-9a-fA-F]{8}", value):
        return value

    return default


def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.strip()

    if re.fullmatch(r"#[0-9a-fA-F]{6}", hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    if re.fullmatch(r"#[0-9a-fA-F]{8}", hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    return f"rgba(68, 68, 68, {alpha})"


def get_colors(card):
    primary = safe_color(
        card.get("primary_color") or card.get("accent_color"),
        "#444444",
    )

    if re.fullmatch(r"#[0-9a-fA-F]{6}", primary):
        secondary = primary + "22"
    elif re.fullmatch(r"#[0-9a-fA-F]{8}", primary):
        secondary = primary
    else:
        secondary = "#dddddd"

    return primary, secondary


# --------------------------------------------------
# Font stacks
# --------------------------------------------------

SANS_STACK = "'Helvetica Neue', 'Arial Nova', Helvetica, Arial, sans-serif"
SERIF_STACK = "Georgia, 'Droid Serif', serif"


# --------------------------------------------------
# Shared renderer
# --------------------------------------------------

def render_base_card(
    card,
    title_margin_bottom,
    primary_font_size,
    primary_margin_bottom,
    secondary_html,
):
    primary_color, secondary_color = get_colors(card)

    title = safe_text(card.get("title", ""))
    primary_value = safe_text(card.get("primary_value", ""))
    context = safe_text(card.get("context"))

    accent_tint = hex_to_rgba(primary_color, 0.10)
    accent_text = hex_to_rgba(primary_color, 0.95)

    header_accent_html = f"""
    <div style="
        display:flex;
        align-items:center;
        gap:8px;
        margin-bottom:10px;
        font-size:0.78rem;
        letter-spacing:0.02em;
        color:{accent_text};
        font-family:{SANS_STACK};
        font-weight:600;
        white-space:normal;
        overflow-wrap:anywhere;
        word-break:break-word;
    ">
        <span style="
            display:inline-block;
            width:8px;
            height:8px;
            min-width:8px;
            border-radius:999px;
            background:{primary_color};
        "></span>
        <span>Delaware High School Sports</span>
    </div>
    """

    context_html = ""
    if context:
        context_html = f"""
        <div style="
            margin-top:12px;
            padding-top:10px;
            border-top:1px solid rgba(17, 17, 17, 0.08);
            font-size:0.84rem;
            line-height:1.4;
            color:#666;
            font-family:{SANS_STACK};
            white-space:normal;
            overflow-wrap:anywhere;
            word-break:break-word;
        ">
            <span style="
                display:inline-block;
                padding:4px 8px;
                border-radius:999px;
                background:{accent_tint};
                color:{accent_text};
            ">
                {context}
            </span>
        </div>
        """

    raw_html(
        f"""
        <div style="
            max-width:380px;
            padding:20px;
            margin-bottom:6px;
            background:#fcfcfb;
            border:1px solid rgba(17, 17, 17, 0.08);
            border-radius:14px;
            box-shadow:
                0 1px 2px rgba(17, 17, 17, 0.03),
                0 8px 24px rgba(17, 17, 17, 0.04);
            font-family:{SERIF_STACK};
            color:#111;
        ">

            {header_accent_html}

            <div style="
                font-size:0.95rem;
                line-height:1.35;
                color:#555;
                font-family:{SANS_STACK};
                margin-bottom:{title_margin_bottom};
                white-space:normal;
                overflow-wrap:anywhere;
                word-break:break-word;
            ">
                {title}
            </div>

            <div style="
                font-size:{primary_font_size};
                font-weight:700;
                line-height:1.15;
                font-family:{SANS_STACK};
                margin-bottom:{primary_margin_bottom};
                white-space:normal;
                overflow-wrap:anywhere;
                word-break:break-word;
            ">
                {primary_value}
            </div>

            {secondary_html}

            {context_html}

        </div>
        """,
        height=320,
    )


# --------------------------------------------------
# Dispatcher
# --------------------------------------------------

def render_card(card):
    variant = card.get("variant", "recall")

    if variant == "ranking":
        render_ranking_card(card)
    elif variant == "school_summary":
        render_school_summary_card(card)
    else:
        render_recall_card(card)


# --------------------------------------------------
# Recall / Event Card
# --------------------------------------------------

def render_recall_card(card):
    secondary_value = safe_text(card.get("secondary_value"))

    secondary_html = ""
    if secondary_value:
        secondary_html = f"""
        <div style="
            font-size:1rem;
            line-height:1.45;
            color:#333;
            font-family:{SERIF_STACK};
            margin-bottom:10px;
            white-space:normal;
            overflow-wrap:anywhere;
            word-break:break-word;
        ">
            {secondary_value}
        </div>
        """

    render_base_card(
        card=card,
        title_margin_bottom="6px",
        primary_font_size="1.6rem",
        primary_margin_bottom="8px",
        secondary_html=secondary_html,
    )


# --------------------------------------------------
# Ranking Card
# --------------------------------------------------

def render_ranking_card(card):
    primary_color, _ = get_colors(card)
    secondary_value = safe_text(card.get("secondary_value"))

    secondary_html = ""
    if secondary_value:
        secondary_html = f"""
        <div style="
            font-size:1.18rem;
            font-weight:600;
            line-height:1.3;
            color:{primary_color};
            font-family:{SANS_STACK};
            margin-bottom:10px;
            white-space:normal;
            overflow-wrap:anywhere;
            word-break:break-word;
        ">
            {secondary_value}
        </div>
        """

    render_base_card(
        card=card,
        title_margin_bottom="8px",
        primary_font_size="1.5rem",
        primary_margin_bottom="4px",
        secondary_html=secondary_html,
    )


# --------------------------------------------------
# School Summary Card
# --------------------------------------------------

def render_school_summary_card(card):
    secondary_value = safe_text(card.get("secondary_value"))

    secondary_html = ""
    if secondary_value:
        secondary_html = f"""
        <div style="
            font-size:1rem;
            line-height:1.5;
            color:#333;
            font-family:{SERIF_STACK};
            margin-bottom:10px;
            white-space:normal;
            overflow-wrap:anywhere;
            word-break:break-word;
        ">
            {secondary_value}
        </div>
        """

    render_base_card(
        card=card,
        title_margin_bottom="6px",
        primary_font_size="1.55rem",
        primary_margin_bottom="8px",
        secondary_html=secondary_html,
    )
