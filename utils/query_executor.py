def execute_query(query, team_df, rec_df):
    explanation = []

    if query["intent"] == "team_result":
    df = team_df.copy()

    filters = query["filters"]

    if filters.get("sport"):
        df = df[df["sport"] == filters["sport"]]
        explanation.append(f"Filtered by sport = {filters['sport']}")

    if filters.get("gender"):
        df = df[df["gender"] == filters["gender"]]
        explanation.append(f"Filtered by gender = {filters['gender']}")

    if filters.get("year"):
        df = df[df["year"] == filters["year"]]
        explanation.append(f"Filtered by year = {filters['year']}")

    if filters.get("classification"):
        df = df[df["classification"] == filters["classification"]]
        explanation.append(
            f"Filtered by classification = {filters['classification']}"
        )

    return df, explanation

    if query["intent"] == "aggregation":
        df = team_df.copy()
        if query.get("derived_metric"):
            df["combined_score"] = df["champion_score"] + df["runner_up_score"]
            explanation.append("Calculated combined score")
        result = df["combined_score"].max()
        explanation.append("Selected maximum combined score")
        return result, explanation

    if query["intent"] == "ranking":
        df = team_df.copy()
        grouped = df.groupby(query["group_by"]).count().reset_index()
        ranked = grouped.sort_values("year", ascending=False)
        explanation.append(f"Grouped by {query['group_by']}")
        explanation.append("Ranked results")
        return ranked.head(1), explanation

    return None, ["Unsupported query"]
