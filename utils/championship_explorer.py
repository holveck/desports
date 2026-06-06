import html
import pandas as pd
import streamlit as st

from utils.schools_page import (
    FONT_STACK,
    normalize_school_name,
    sort_titles_df,
    format_sport_label,
    format_score_text,
    get_story_url,
)


def build_score_display(row):
    score_text = format_score_text(row)
    score_note = str(row.get("score_note", "")).strip()

    if score_text and score_note:
        if score_note.lower() not in score_text.lower():
            return f"{score_text} ({score_note})"
        return score_text

    if score_text:
        return score_text

    if score_note:
        return score_note

    return ""


def build_explorer_display_df(team_df):
    df = sort_titles_df(team_df).copy()

    if "_season_sort_key" in df.columns:
        df = df.drop(columns=["_season_sort_key"])

    if "year" in df.columns:
        df["year"] = df["year"].astype("Int64")

    df["Sport"] = df.apply(format_sport_label, axis=1)
    df["Score"] = df.apply(build_score_display, axis=1)
    df["_story_url"] = df.apply(get_story_url, axis=1)

    display_df = pd.DataFrame({
        "Year": df["year"].astype(str).replace("<NA>", ""),
        "Sport": df["Sport"].fillna(""),
        "Classification": df["classification"].fillna("") if "classification" in df.columns else "",
        "Champion": df["champion"].fillna("") if "champion" in df.columns else "",
        "Runner-up": df["runner_up"].fillna("") if "runner_up" in df.columns else "",
        "Score": df["Score"].fillna(""),
        "Venue": df["venue"].fillna("") if "venue" in df.columns else "",
        "_story_url": df["_story_url"].fillna(""),
        "_year_numeric": pd.to_numeric(df["year"], errors="coerce"),
    })

    return display_df


def sort_explorer_df(display_df, sort_by):
    df = display_df.copy()

    if sort_by == "Most recent":
        return df.sort_values(
            ["_year_numeric"],
            ascending=[False],
            na_position="last",
            kind="stable",
        )

    if sort_by == "Year":
        return df.sort_values(
            ["_year_numeric", "Sport", "Champion"],
            ascending=[False, True, True],
            na_position="last",
            kind="stable",
        )

    if sort_by == "Sport":
        return df.sort_values(
            ["Sport", "_year_numeric", "Champion"],
            ascending=[True, False, True],
            na_position="last",
            kind="stable",
        )

    return df


def render_explorer_table(display_df):
    if display_df.empty:
        st.info("No championship records found for the selected filters.")
        return

    rows_html = []

    for _, row in display_df.iterrows():
        year_html = html.escape(str(row.get("Year", "") or ""))
        sport_html = html.escape(str(row.get("Sport", "") or ""))
        classification_html = html.escape(str(row.get("Classification", "") or ""))
        champion_html = html.escape(str(row.get("Champion", "") or ""))
        runner_up_html = html.escape(str(row.get("Runner-up", "") or ""))
        venue_html = html.escape(str(row.get("Venue", "") or ""))
        score_label = html.escape(str(row.get("Score", "") or ""))
        story_url = str(row.get("_story_url", "") or "").strip()

        if story_url and score_label:
            score_html = (
                f'<a href="{html.escape(story_url)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#1f2937;text-decoration:underline;text-underline-offset:2px;">{score_label}</a>'
            )
        else:
            score_html = f"<span>{score_label}</span>"

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
    <style>
        .championship-table-wrap {{
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 0.75rem;
            overflow: hidden;
            background: #ffffff;
        }}

        .championship-table-scroll {{
            overflow-x: auto;
        }}

        table.championship-table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 980px;
            font-family: {FONT_STACK};
            font-size: 0.95rem;
            line-height: 1.2;
            color: #1f2937;
        }}

        .championship-table thead th {{
            text-align: left;
            font-weight: 700;
            background: #f8fafc;
            border-bottom: 1px solid rgba(49, 51, 63, 0.14);
            padding: 0.7rem 0.8rem;
            white-space: nowrap;
        }}

        .championship-table tbody td {{
            padding: 0.68rem 0.8rem;
            border-bottom: 1px solid rgba(49, 51, 63, 0.09);
            vertical-align: top;
        }}

        .championship-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        .championship-table tbody tr:hover {{
            background: rgba(248, 250, 252, 0.9);
        }}
    </style>

    <div class="championship-table-wrap">
        <div class="championship-table-scroll">
            <table class="championship-table">
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
    """

    st.markdown(table_html, unsafe_allow_html=True)


def render_championship_explorer(team_df, schools_df):
    st.markdown(
        f'<div style="font-family:{FONT_STACK};font-size:1.45rem;line-height:1.15;font-weight:700;color:#1f2937;margin:0 0 0.35rem 0;">Championship Explorer</div>',
        unsafe_allow_html=True,
    )
    st.caption("Browse Delaware state championship results by school, year, or sport.")

    school_options = ["All schools"] + (
        schools_df["canonical_name"]
        .dropna()
        .astype(str)
        .sort_values()
        .tolist()
    )

    default_school = st.session_state.get("explorer_selected_school", "All schools")
    if default_school not in school_options:
        default_school = "All schools"

    control_col1, control_col2 = st.columns([1.45, 1])

    with control_col1:
        selected_school = st.selectbox(
            "School",
            options=school_options,
            index=school_options.index(default_school),
            key="championship_explorer_school",
        )

    with control_col2:
        sort_by = st.selectbox(
            "Sort by",
            options=["Most recent", "Year", "Sport"],
            index=0,
            key="championship_explorer_sort",
        )

    st.session_state["explorer_selected_school"] = selected_school

    filtered_df = team_df.copy()

    if selected_school != "All schools":
        school_match = normalize_school_name(selected_school)
        filtered_df = filtered_df[
            filtered_df["champion"].map(normalize_school_name) == school_match
        ].copy()

    display_df = build_explorer_display_df(filtered_df)
    display_df = sort_explorer_df(display_df, sort_by)

    if "_year_numeric" in display_df.columns:
        display_df = display_df.drop(columns=["_year_numeric"])

    if "_story_url" not in display_df.columns:
        display_df["_story_url"] = ""

    render_explorer_table(display_df)
