from utils.schools import get_canonical_school_name


def apply_team_filters(df, filters, explanation):
    if filters.get("sport"):
        df = df[df["sport"] == filters["sport"]]
        explanation.append(f"Filtered by sport = {filters['sport']}")

    if filters.get("gender"):
        df = df[df["gender"] == filters["gender"]]
        explanation.append(f"Filtered by gender = {filters['gender']}")

    if filters.get("year"):
        df = df[df["year"] == filters["year"]]
        explanation.append(f"Filtered by year = {filters['year']}")

    if filters.get("since_year"):
        df = df[df["year"] >= filters["since_year"]]
        explanation.append(f"Filtered by year >= {filters['since_year']}")

    if filters.get("classification") and "classification" in df.columns:
        df = df[df["classification"] == filters["classification"]]
        explanation.append(
            f"Filtered by classification = {filters['classification']}"
        )

    return df


def apply_school_filter(df, filters, explanation):
    school_id = filters.get("school_id")
    if not school_id:
        return df

    canonical = get_canonical_school_name(school_id)
    if canonical:
        df = df[df["champion"] == canonical]
        explanation.append(f"Filtered by champion = {canonical}")

    return df


def build_ranking_leaders(df, explanation):
    grouped = (
        df.groupby("champion", as_index=False)
          .size()
          .rename(columns={"size": "titles"})
          .sort_values(["titles", "champion"], ascending=[False, True])
    )

    explanation.append("Grouped championships by school")
    explanation.append("Ranked schools by number of titles")

    if grouped.empty:
        return grouped

    top_titles = grouped.iloc[0]["titles"]
    leaders = grouped[grouped["titles"] == top_titles].reset_index(drop=True)

    explanation.append(
        f"Found {len(leaders)} top school(s) tied at {top_titles} titles"
    )

    return leaders


def execute_query(query, team_df, rec_df):
    explanation = []
    filters = query.get("filters", {})
    intent = query.get("intent")

    if intent == "team_result":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)
        return df, explanation

    if intent == "school_summary":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)
        df = apply_school_filter(df, filters, explanation)

        explanation.append("Summarized championships for a single school")
        return df, explanation

    if intent == "aggregation":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)
        df = apply_school_filter(df, filters, explanation)

        explanation.append("Counted championship results")
        return len(df), explanation

    if intent == "ranking":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)
        leaders = build_ranking_leaders(df, explanation)
        return leaders, explanation
