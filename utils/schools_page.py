import html
import pandas as pd
import streamlit as st
import string


FONT_STACK = "'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


def normalize_school_name(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = text.replace("&", "and")
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text


def get_school_record(schools_df, canonical_name):
    match = schools_df[schools_df["canonical_name"] == canonical_name]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_team_titles_for_school(team_df, canonical_name):
    if "champion" not in team_df.columns:
        return pd.DataFrame()

    df = team_df.copy()
    df["_champion_match"] = df["champion"].map(normalize_school_name)
    selected_match = normalize_school_name(canonical_name)

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    matched = df[df["_champion_match"] == selected_match].copy()

    if "_champion_match" in matched.columns:
        matched = matched.drop(columns=["_champion_match"])

    return matched


def build_school_summary(school_record, team_titles_df):
    total_titles = len(team_titles_df)

    recent_titles = pd.DataFrame()
    if not team_titles_df.empty:
        if "year" in team_titles_df.columns:
            recent_titles = team_titles_df.sort_values("year", ascending=False).head(3).copy()
        else:
            recent_titles = team_titles_df.head(3).copy()

    return {
        "school_record": school_record,
        "total_titles": total_titles,
        "recent_titles": recent_titles,
    }


def render_school_selector(schools_df):
    school_options = (
        schools_df["canonical_name"]
        .dropna()
        .astype(str)
        .sort_values()
        .tolist()
    )

    return st.selectbox(
        "",
        options=school_options,
        index=None,
        placeholder="Choose a school",
        key="selected_school",
        label_visibility="collapsed",
    )


def render_school_identity_card(summary):
    school = summary["school_record"]

    school_name = school.get("canonical_name", "Unknown school")
    nickname = school.get("nickname", "")
    location = school.get("location", "")

    primary_color = school.get("primary_color", "#1569B3")
    if pd.isna(primary_color) or not str(primary_color).strip():
        primary_color = "#1569B3"
    primary_color = str(primary_color).strip()

    if not primary_color.startswith("#"):
        primary_color = f"#{primary_color}"

    nickname_text = ""
    if pd.notna(nickname) and str(nickname).strip():
        nickname_text = str(nickname).strip()

    location_text = ""
    if pd.notna(location) and str(location).strip():
        location_text = str(location).strip()

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 0.75rem;
            padding: 1.05rem 1.2rem 0.95rem 1.2rem;
            background: radial-gradient(circle at top left, #ffffff 0%, #ffffff 10%, {primary_color} 100%);
            margin-bottom: 0.55rem;
        ">
            <div style="
                font-family: {FONT_STACK};
                font-size: 2rem;
                line-height: 1.02;
                font-weight: 700;
                margin: 0;
                padding: 0;
                color: #1f2937;
            ">
                {html.escape(str(school_name))}
            </div>
            <div style="
                font-family: {FONT_STACK};
                font-size: 0.95rem;
                line-height: 1.1;
                font-weight: 400;
                color: rgba(31, 41, 55, 0.8);
                margin-top: 0.18rem;
            ">
                {html.escape(nickname_text)}
            </div>
            <div style="
                font-family: {FONT_STACK};
                font-size: 0.9rem;
                line-height: 1.1;
                font-weight: 400;
                color: rgba(31, 41, 55, 0.72);
                margin-top: 0.08rem;
            ">
                {html.escape(location_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_school_kpi(summary):
    total_titles = summary["total_titles"]

    st.markdown(
        f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 0.5rem 0 1.1rem 0;
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.55rem;
                margin: 0;
                padding: 0;
            ">
                <div style="
                    font-size: 1.5rem;
                    line-height: 1;
                ">🏆</div>
                <div style="
                    font-family: {FONT_STACK};
                    font-size: 2.35rem;
                    line-height: 1;
                    font-weight: 700;
                    margin: 0;
                    padding: 0;
                    color: #1f2937;
                ">
                    {total_titles}
                </div>
            </div>
            <div style="
                font-family: {FONT_STACK};
                font-size: 0.95rem;
                line-height: 1.2;
                font-weight: 400;
                color: rgba(49, 51, 63, 0.72);
                margin-top: 0.4rem;
            ">
                State Championships
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_sport_label(row):
    sport = str(row.get("sport", "")).strip()
    gender = str(row.get("gender", "")).strip().lower()

    if not sport:
        return ""

    multi_gender_sports = {
        "lacrosse",
        "soccer",
        "basketball",
        "cross country",
        "swimming",
        "swimming and diving",
        "indoor track",
        "outdoor track",
        "track",
        "tennis",
        "volleyball",
        "wrestling",
    }

    if gender in {"girls", "boys"} and sport.lower() in multi_gender_sports:
        return f"{gender.title()} {sport}"

    return sport


def format_score_text(row):
    champion_score = row.get("champion_score", "")
    runner_up_score = row.get("runner_up_score", "")

    if (
        pd.notna(champion_score)
        and str(champion_score).strip()
        and pd.notna(runner_up_score)
        and str(runner_up_score).strip()
    ):
        return f"{str(champion_score).strip()}-{str(runner_up_score).strip()}"

    score_note = row.get("score_note", "")
    if pd.notna(score_note) and str(score_note).strip():
        return str(score_note).strip()

    return ""


def get_story_url(row):
    if "link" in row.index and pd.notna(row["link"]) and str(row["link"]).strip():
        return str(row["link"]).strip()
    return ""


def build_recent_result_text(row):
    runner_up = str(row.get("runner_up", "")).strip()
    score_text = format_score_text(row)

    parts = ["Defeated"]
    if runner_up:
        parts.append(runner_up)
    if score_text:
        parts.append(score_text)

    return " ".join(parts).strip()


def render_recent_championships(team_titles_df):
    st.markdown(
        f'<div style="font-family:{FONT_STACK};font-size:1.08rem;line-height:1.15;font-weight:700;color:#1f2937;margin:0.1rem 0 0.45rem 0;">Recent Championships</div>',
        unsafe_allow_html=True,
    )

    if team_titles_df.empty:
        st.markdown(
            f'<div style="border:1px solid rgba(49,51,63,0.14);border-radius:0.75rem;padding:0.7rem 0.95rem;margin-bottom:0.35rem;background:#ffffff;font-family:{FONT_STACK};font-size:0.95rem;line-height:1.15;color:rgba(31,41,55,0.72);">No recent championships available.</div>',
            unsafe_allow_html=True,
        )
        return

    recent_df = team_titles_df.copy()

    if "year" in recent_df.columns:
        recent_df["year"] = pd.to_numeric(recent_df["year"], errors="coerce")
        recent_df = recent_df.sort_values("year", ascending=False, na_position="last")

    recent_df = recent_df.head(3)

    row_blocks = []

    for _, row in recent_df.iterrows():
        year_text = ""
        if "year" in row.index and pd.notna(row["year"]):
            try:
                year_text = str(int(row["year"]))
            except Exception:
                year_text = str(row["year"]).strip()

        sport_text = format_sport_label(row)
        result_text = build_recent_result_text(row)
        story_url = get_story_url(row)

        year_html = html.escape(year_text)
        sport_html = html.escape(sport_text)
        result_label_html = html.escape(result_text)

        if story_url:
            result_html = (
                f'<a href="{html.escape(story_url)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#1f2937;text-decoration:underline;text-underline-offset:2px;">{result_label_html}</a>'
            )
        else:
            result_html = f'<span style="color:#1f2937;">{result_label_html}</span>'

        row_blocks.append(
            f'<div style="display:grid;grid-template-columns:3.7rem 10.75rem 1fr;gap:0.45rem;align-items:start;padding:0.16rem 0;">'
            f'<div style="font-family:{FONT_STACK};font-size:0.95rem;line-height:1.15;font-weight:600;color:#1f2937;white-space:nowrap;">{year_html}</div>'
            f'<div style="font-family:{FONT_STACK};font-size:0.95rem;line-height:1.15;font-weight:600;color:#1f2937;">{sport_html}</div>'
            f'<div style="font-family:{FONT_STACK};font-size:0.95rem;line-height:1.15;font-weight:400;color:#1f2937;">{result_html}</div>'
            f'</div>'
        )

    box_html = (
        f'<div style="border:1px solid rgba(49,51,63,0.14);border-radius:0.75rem;padding:0.5rem 0.95rem;margin-bottom:0.3rem;background:#ffffff;">'
        f'{"".join(row_blocks)}'
        f'</div>'
    )

    st.markdown(box_html, unsafe_allow_html=True)

    if st.button("View All", key="view_all_championships", use_container_width=False):
        st.session_state["show_all_titles_expanded"] = True


def render_all_team_titles(team_titles_df):
    expanded = st.session_state.get("show_all_titles_expanded", False)

    with st.expander("Show all team championship records", expanded=expanded):
        if team_titles_df.empty:
            st.info("No championship rows found.")
            return

        display_cols = [
            col for col in [
                "year",
                "sport",
                "gender",
                "classification",
                "champion",
                "runner_up",
                "head_coach",
                "champion_score",
                "runner_up_score",
                "score_note",
                "venue",
                "link",
            ]
            if col in team_titles_df.columns
        ]

        all_titles = team_titles_df.copy()

        if "year" in all_titles.columns:
            all_titles["year"] = pd.to_numeric(all_titles["year"], errors="coerce")
            all_titles = all_titles.sort_values("year", ascending=False, na_position="last")
            all_titles["year"] = all_titles["year"].astype("Int64")

        st.dataframe(
            all_titles[display_cols],
            use_container_width=True,
            hide_index=True,
        )


def render_school_page(schools_df, team_df):
    selected_school = render_school_selector(schools_df)

    if not selected_school:
        st.info("Choose a school to view its profile.")
        return

    school_record = get_school_record(schools_df, selected_school)
    if school_record is None:
        st.warning("That school could not be found.")
        return

    team_titles_df = get_team_titles_for_school(team_df, selected_school)
    summary = build_school_summary(school_record, team_titles_df)

    if "show_all_titles_expanded" not in st.session_state:
        st.session_state["show_all_titles_expanded"] = False

    render_school_identity_card(summary)
    render_school_kpi(summary)
    render_recent_championships(team_titles_df)
    render_all_team_titles(team_titles_df)
