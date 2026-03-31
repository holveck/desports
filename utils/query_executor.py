def execute_query(query, team_df, rec_df):
    explanation = []
    filters = query.get("filters", {})

    # --------------------------------------------------
    # TEAM RESULT (existing behavior, unchanged)
    # --------------------------------------------------
    if query["intent"] == "team_result":
        df = team_df.copy()

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

    # --------------------------------------------------
    # AGGREGATION: title counts
    # --------------------------------------------------
    if query["intent"] == "aggregation":
        df = team_df.copy()

        # Apply standard filters
        if filters.get("sport"):
            df = df[df["sport"] == filters["sport"]]
            explanation.append(f"Filtered by sport = {filters['sport']}")

        if filters.get("gender"):
            df = df[df["gender"] == filters["gender"]]
            explanation.append(f"Filtered by gender = {filters['gender']}")

        if filters.get("classification"):
            df = df[df["classification"] == filters["classification"]]
            explanation.append(
                f"Filtered by classification = {filters['classification']}"
            )

        # Apply school filter (critical step)
        if filters.get("school_id"):
            canonical = get_canonical_school_name(filters["school_id"])
            if canonical:
                df = df[df["champion"] == canonical]
                explanation.append(f"Filtered by champion = {canonical}")

        # Count titles
        count = len(df)
        explanation.append("Counted championship results")

        return count, explanation

    # --------------------------------------------------
    # RANKING: which school has won the most titles
    # --------------------------------------------------
    if query["intent"] == "ranking":
        df = team_df.copy()

        if filters.get("sport"):
            df = df[df["sport"] == filters["sport"]]
            explanation.append(f"Filtered by sport = {filters['sport']}")

        if filters.get("gender"):
            df = df[df["gender"] == filters["gender"]]
            explanation.append(f"Filtered by gender = {filters['gender']}")

        if filters.get("classification"):
            df = df[df["classification"] == filters["classification"]]
            explanation.append(
                f"Filtered by classification = {filters['classification']}"
            )

        # Group and rank
        grouped = (
            df.groupby("champion")
              .size()
              .reset_index(name="titles")
              .sort_values("titles", ascending=False)
        )

        explanation.append("Grouped championships by school")
        explanation.append("Ranked schools by number of titles")

        # Return top result only (extendable later)
        return grouped.head(1), explanation

    return None, ["Unsupported query"]
