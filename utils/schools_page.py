import pandas as pd
import streamlit as st
import string


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
        "Select a school",
        options=school_options,
        index=None,
        placeholder="Choose a school",
        key="selected_school",
    )


def render_school_identity_card(summary):
    school = summary["school_record"]

    school_name = school.get("canonical_name", "Unknown school")
    nickname = school.get("nickname", "")
    city = school.get("city", "")
    state = school.get("state", "")

    location_bits = [str(x).strip() for x in [city, state] if pd.notna(x) and str(x).strip()]
    location_line = ", ".join(location_bits)

    sub_bits = []
    if pd.notna(nickname) and str(nickname).strip():
        sub_bits.append(str(nickname).strip())
    if location_line:
        sub_bits.append(location_line)

    sub_line = " • ".join(sub_bits)

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.75rem;
            padding: 1.1rem 1.25rem 1rem 1.25rem;
            background: transparent;
            margin-bottom: 0.75rem;
        ">
            <div style="
                font-family: 'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 2rem;
                line-height: 1.05;
                font-weight: 700;
                margin: 0;
                padding: 0;
            ">
                {school_name}
            </div>
            <div style="
                font-family: 'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 0.95rem;
                line-height: 1.2;
                font-weight: 400;
                color: rgba(49, 51, 63, 0.72);
                margin-top: 0.25rem;
            ">
                {sub_line}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_school_kpi_card(summary):
    total_titles = summary["total_titles"]

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.75rem;
            padding: 1.1rem 1.25rem 1rem 1.25rem;
            background: transparent;
            margin-bottom: 1rem;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 0.55rem;
                margin: 0;
                padding: 0;
            ">
                <div style="
                    font-size: 1.5rem;
                    line-height: 1;
                ">🏆</div>
                <div style="
                    font-family: 'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                    font-size: 2rem;
                    line-height: 1;
                    font-weight: 700;
                    margin: 0;
                    padding: 0;
                ">
                    {total_titles}
                </div>
            </div>
            <div style="
                font-family: 'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 0.95rem;
                line-height: 1.2;
                font-weight: 400;
                color: rgba(49, 51, 63, 0.72);
                margin-top: 0.45rem;
            ">
                State Championships
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recent_championships_placeholder():
    st.markdown("### Recent championships")
    st.info("Recent championships section will be restyled next.")


def render_all_team_titles(team_titles_df):
    with st.expander("Show all team championship records"):
        if team_titles_df.empty:
            st.info("No championship rows found.")
            return

        display_cols = [
            col for col in [
                "year",
                "sport",
                "classification",
                "champion",
                "runner_up",
                "head_coach",
                "champion_score",
                "runner_up_score",
                "score_note",
                "venue",
            ]
            if col in team_titles_df.columns
        ]

        all_titles = team_titles_df.copy()

        if "year" in all_titles.columns:
            all_titles = all_titles.sort_values("year", ascending=False)
            all_titles["year"] = all_titles["year"].astype("Int64")

        st.dataframe(
            all_titles[display_cols],
            use_container_width=True,
            hide_index=True,
        )


def render_school_page(schools_df, team_df):
    st.subheader("Schools")

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

    render_school_identity_card(summary)
    render_school_kpi_card(summary)
    render_recent_championships_placeholder()
    render_all_team_titles(team_titles_df)
