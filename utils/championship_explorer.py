import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.schools_page import (
    FONT_STACK,
    normalize_school_name,
    sort_titles_df,
    format_sport_label,
    format_score_text,
    get_story_url,
)


def clean_text(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def build_score_display(row):
    champion_score = clean_text(row.get("champion_score", ""))
    runner_up_score = clean_text(row.get("runner_up_score", ""))
    score_note = clean_text(row.get("score_note", ""))

    base_score = ""
    if champion_score and runner_up_score:
        base_score = f"{champion_score}-{runner_up_score}"

    if base_score and score_note:
        return f"{base_score} ({score_note})"

    if base_score:
        return base_score

    if score_note:
        return score_note

    return ""


def build_display_df(team_df):
    df = team_df.copy()

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df = sort_titles_df(df).copy()

    if "_season_sort_key" in df.columns:
        df = df.drop(columns=["_season_sort_key"])

    df["Sport"] = df.apply(format_sport_label, axis=1)
    df["Score"] = df.apply(build_score_display, axis=1)
    df["_story_url"] = df.apply(get_story_url, axis=1)

    return pd.DataFrame({
        "Year": df["year"].astype("Int64").astype(str).replace("<NA>", ""),
        "Sport": df["Sport"].map(clean_text),
        "Classification": df["classification"].map(clean_text) if "classification" in df.columns else "",
        "Champion": df["champion"].map(clean_text) if "champion" in df.columns else "",
        "Runner-up": df["runner_up"].map(clean_text) if "runner_up" in df.columns else "",
        "Score": df["Score"].map(clean_text),
        "Venue": df["venue"].map(clean_text) if "venue" in df.columns else "",
        "_story_url": df["_story_url"].map(clean_text),
    })


def render_explorer_table(display_df):
    if display_df.empty:
        st.info("No championship records found for the selected filters.")
        return

    rows_html = []

    for _, row in display_df.iterrows():
        year_html = html.escape(clean_text(row.get("Year", "")))
        sport_html = html.escape(clean_text(row.get("Sport", "")))
        classification_html = html.escape(clean_text(row.get("Classification", "")))
        champion_html = html.escape(clean_text(row.get("Champion", "")))
        runner_up_html = html.escape(clean_text(row.get("Runner-up", "")))
        venue_html = html.escape(clean_text(row.get("Venue", "")))
        score_text = clean_text(row.get("Score", ""))
        score_html = html.escape(score_text)
        story_url = clean_text(row.get("_story_url", ""))

        if story_url and score_text:
            score_html = (
                f'<a href="{html.escape(story_url)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#1f2937;text-decoration:underline;text-underline-offset:2px;">{score_html}</a>'
            )

        rows_html.append(
            f"""
            <tr>
                <td>{year_html}</td>
                <td>{sport_html}</td>
                <td>{classification_html}</td>
                <td>{champion_html}</td>
                <td>{runner_up_html}</td>
                <td>{score_html}</td>
                <td>{venue_html}</td>
            </tr>
            """
        )

    table_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: white;
                font-family: {FONT_STACK};
            }}
            .championship-table-wrap {{
                border: 1px solid rgba(49, 51, 63, 0.14);
                border-radius: 12px;
                overflow: hidden;
                background: #ffffff;
            }}
            .championship-table-scroll {{
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 980px;
                font-size: 0.95rem;
                line-height: 1.2;
                color: #1f2937;
            }}
            thead th {{
                text-align: left;
                font-weight: 700;
                background: #f8fafc;
                border-bottom: 1px solid rgba(49, 51, 63, 0.14);
                padding: 0.7rem 0.8rem;
                white-space: nowrap;
            }}
            tbody td {{
                padding: 0.68rem 0.8rem;
                border-bottom: 1px solid rgba(49, 51, 63, 0.09);
                vertical-align: top;
            }}
            tbody tr:last-child td {{
                border-bottom: none;
            }}
            tbody tr:hover {{
                background: rgba(248, 250, 252, 0.85);
            }}
            a {{
                color: #1f2937;
                text-decoration: underline;
                text-underline-offset: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="championship-table-wrap">
            <div class="championship-table-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>Year</th>
                            <th>Sport</th>
                            <th>Classification</th>
                            <th>Champion</th>
                            <th>Runner-up</th>
                            <th>Score</th>
                            <th>Venue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows_html)}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    table_height = min(900, max(420, 88 + 38 * len(display_df)))
    components.html(table_html, height=table_height, scrolling=True)


def render_championship_explorer(team_df, schools_df):
    st.markdown(
        f'<div style="font-family:{FONT_STACK};font-size:1.45rem;line-height:1.15;font-weight:700;color:#1f2937;margin:0 0 0.35rem 0;">Championship Explorer</div>',
        unsafe_allow_html=True,
    )
    st.caption("Browse Delaware state championship results by school, year, or sport.")

    base_df = team_df.copy()
    base_df["Sport"] = base_df.apply(format_sport_label, axis=1)

    school_options = ["All schools"] + (
        schools_df["canonical_name"]
        .dropna()
        .astype(str)
        .sort_values()
        .tolist()
    )

    year_values = (
        pd.to_numeric(base_df["year"], errors="coerce")
        .dropna()
        .astype(int)
        .sort_values(ascending=False)
        .unique()
        .tolist()
    )
    year_options = ["All years"] + year_values

    sport_values = (
        base_df["Sport"]
        .dropna()
        .astype(str)
        .map(str.strip)
        .loc[lambda s: s != ""]
        .sort_values()
        .unique()
        .tolist()
    )
    sport_options = ["All sports"] + sport_values

    default_school = st.session_state.get("explorer_selected_school", "All schools")
    if default_school not in school_options:
        default_school = "All schools"

    col1, col2, col3 = st.columns([1.3, 1, 1])

    with col1:
        selected_school = st.selectbox(
            "School",
            options=school_options,
            index=school_options.index(default_school),
            key="championship_explorer_school",
        )

    with col2:
        selected_year = st.selectbox(
            "Year",
            options=year_options,
            index=0,
            key="championship_explorer_year",
        )

    with col3:
        selected_sport = st.selectbox(
            "Sport",
            options=sport_options,
            index=0,
            key="championship_explorer_sport",
        )

    st.session_state["explorer_selected_school"] = selected_school

    filtered_df = base_df.copy()

    if selected_school != "All schools":
        school_match = normalize_school_name(selected_school)
        filtered_df = filtered_df[
            filtered_df["champion"].map(normalize_school_name) == school_match
        ].copy()

    if selected_year != "All years":
        filtered_df = filtered_df[
            pd.to_numeric(filtered_df["year"], errors="coerce") == int(selected_year)
        ].copy()

    if selected_sport != "All sports":
        filtered_df = filtered_df[filtered_df["Sport"] == selected_sport].copy()

    display_df = build_display_df(filtered_df)
    render_explorer_table(display_df)
