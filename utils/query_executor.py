from utils.schools import load_school_lookup


def get_canonical_school_name(school_id):
    lookup = load_school_lookup()
    for record in lookup.values():
        if record["school_id"] == school_id:
            return record["canonical_name"]
    return None


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

    if filters.get("classification") and "classification" in df.columns:
        df = df[df["classification"] == filters["classification"]]
        explanation.append(
            f"Filtered by classification = {filters['classification']}"
        )

    return df


def execute_query(query, team_df, rec_df):
    explanation = []
    filters = query.get("filters", {})

    # TEAM RESULT
    if query["intent"] == "team_result":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)
        return df, explanation

    # AGGREGATION (title counts)
    if query["intent"] == "aggregation":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)

        if filters.get("school_id"):
            canonical = get_canonical_school_name(filters["school_id"])
            if canonical:
                df = df[df["champion"] == canonical]
                explanation.append(f"Filtered by champion = {canonical}")

        explanation.append("Counted championship results")
        return len(df), explanation

    # RANKING
    if query["intent"] == "ranking":
        df = team_df.copy()
        df = apply_team_filters(df, filters, explanation)

        grouped = (
            df.groupby("champion")
              .size()
              .reset_index(name="titles")
              .sort_values("titles", ascending=False)
        )

        explanation.append("Grouped championships by school")
        explanation.append("Ranked schools by number of titles")

        return grouped.head(1), explanation

    return None, ["Unsupported query"]
