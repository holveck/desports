import streamlit as st
import pandas as pd


def get_school_record(schools_df, canonical_name):
    match = schools_df[schools_df["canonical_name"] == canonical_name]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_team_titles_for_school(team_df, canonical_name):
    st.write("Selected school:", canonical_name)
    st.write("team_df columns:", list(team_df.columns))

    possible_cols = [col for col in team_df.columns if "school" in col.lower() or "team" in col.lower()]
    st.write("Possible school/team columns:", possible_cols)

    for col in possible_cols:
        sample_values = (
            team_df[col]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .sort_values()
            .head(20)
            .tolist()
        )
        st.write(f"Sample values from {col}:", sample_values)

    if "school_normalized" in team_df.columns:
        school_col = "school_normalized"
    elif "school" in team_df.columns:
        school_col = "school"
    else:
        st.warning("No matching school column found in team_df.")
        return pd.DataFrame()

    df = team_df.copy()
    df[school_col] = df[school_col].astype(str).str.strip()
    canonical_name = str(canonical_name).strip()

    matches = df[df[school_col] == canonical_name].copy()
    st.write("Exact match count:", len(matches))

    return matches


def build_school_summary(school_record, team_titles_df):
    total_titles = len(team_titles_df)

    latest_title = None
    if not team_titles_df.empty and "year" in team_titles_df.columns:
        latest_row = team_titles_df.sort_values("year", ascending=False).iloc[0]
        latest_year = latest_row.get("year")
        latest_sport = latest_row.get("sport", "Unknown sport")
        latest_classification = latest_row.get("classification")

        if pd.notna(latest_year):
            latest_title = {
                "year": int(latest_year),
                "sport": latest_sport,
                "classification": latest_classification,
            }

    recent_titles = pd.DataFrame()
    if not team_titles_df.empty:
        sort_cols = [col for col in ["year", "sport"] if col in team_titles_df.columns]
        if sort_cols:
            recent_titles = (
                team_titles_df.sort_values(sort_cols, ascending=[False, True][: len(sort_cols)])
                .head(3)
                .copy()
            )
        else:
            recent_titles = team_titles_df.head(3).copy()

    return {
        "total_titles": total_titles,
        "latest_title": latest_title,
        "recent_titles": recent_titles,
        "school_record": school_record,
    }


def render_school_selector(schools_df):
    school_options = schools_df["canonical_name"].dropna().tolist()

    return st.selectbox(
        "Select a school",
        options=school_options,
        index=None,
        placeholder="Choose a school",
        key="selected_school",
    )


def render_school_profile_card(summary):
    school = summary["school_record"]
    latest_title = summary["latest_title"]
    recent_titles = summary["recent_titles"]

    with st.container(border=True):
        st.subheader(school.get("canonical_name", "Unknown school"))

        context_bits = []
        for field in ["nickname", "city", "conference"]:
            value = school.get(field)
            if value and str(value).strip():
                context_bits.append(str(value).strip())

        if context_bits:
            st.caption(" • ".join(context_bits))

        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric("Team state titles", summary["total_titles"])

        with metric_col2:
            if latest_title:
                latest_label = f'{latest_title["sport"]} ({latest_title["year"]})'
                st.metric("Most recent title", latest_label)
            else:
                st.metric("Most recent title", "None found")

    st.markdown("### Recent championships")

    if recent_titles.empty:
        st.info("No team championship records found for this school.")
        return

    display_cols = [col for col in ["year", "sport", "classification"] if col in recent_titles.columns]
    recent_display = recent_titles[display_cols].copy()

    if "year" in recent_display.columns:
        recent_display["year"] = recent_display["year"].astype("Int64")

    st.dataframe(recent_display, use_container_width=True, hide_index=True)


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

    render_school_profile_card(summary)

    with st.expander("Show all team championship records"):
        if team_titles_df.empty:
            st.info("No championship rows found.")
        else:
            display_cols = [
                col for col in
                ["year", "sport", "classification", "opponent", "score", "coach"]
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
