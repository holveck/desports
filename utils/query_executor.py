from utils.schools import load_school_lookup


# --------------------------------------------------
# Helper: school_id -> canonical school name
# --------------------------------------------------

def get_canonical_school_name(school_id):
    lookup = load_school_lookup()
    for record in lookup.values():
        if record["school_id"] == school_id:
            return record["canonical_name"]
    return None


# --------------------------------------------------
# Helper: apply row-level filters BEFORE aggregation
# --------------------------------------------------

def apply_team_filters(df, filters, explanation):
    """
    Apply all row-level filters to the raw team results DataFrame.
    This must ALWAYS be called before any grouping or aggregation.
    """

    if filters.get("sport"):
        df = df[df["sport"] == filters["sport"]]
        explanation.append(f"Filtered by sport = {filters['sport']}")

    if filters.get("gender"):
        df = df[df["gender"] == filters["gender"]]
        explanation.append(f"Filtered by gender = {filters['gender']}")

    if filters.get("year"):
        df = df[df["year"] == filters["year"]]
        explanation.append(f"Filtered by year = {filters['year']}")

    # ✅ Defensive classification filter (prevents KeyError)
    if filters.get("classification") and "classification" in df.columns:
        df = df[df["classification"] == filters["classification"]]
        explanation.append(
            f"Filtered by classification = {filters['classification']}"
        )

    return df


# --------------------------------------------------
# Main executor
# --------------------------------------------------

def execute_query(query, team_df, rec_df):
    explanation = []
    filters = query.get("filters", {})

    # --------------------------------------------------
    # TEAM RESULT (single championship answers)
    # --------------------------------------------------
    if query["intent"] == "team_result":
        df = team_df.copy()

        df = apply_team_filters(df, filters, explanation)

        return df, explanation

    # --------------------------------------------------
    # AGGREGATION (title counts)
    # --------------------------------------------------
    if query["intent"] == "aggregation":
        df = team_df.copy()

        # ✅ ALL filtering happens first
        df = apply_team_filters(df, filters, explanation)

        # ✅ Apply school filter AFTER standard filters
        if filters.get("school_id"):
            canonical = get_canonical_school_name(filters["school_id"])
            if canonical:
                df = df[df["champion"] == canonical]
                explanation.append(f"Filtered by champion = {canonical}")

        count = len(df)
        explanation.append("Counted championship results")

        return count, explanation

    # --------------------------------------------------
    # RANKING (most championships)
    # --------------------------------------------------
    if query["intent"] == "ranking":
        df = team_df.copy()

        # ✅ ALL filtering happens first
        df = apply_team_filters(df, filters, explanation)

        grouped = (
            df.groupby("champion")
              .size()
              .reset_index(name="titles")
              .sort_values("titles", ascending=False)
        )

        explanation.append("Grouped championships by school")
        explanation.append("Ranked schools by number of titles")

        # Return the top result only (easy to expand later)
        return grouped.head(1), explanation

    return None, ["Unsupported query"]
``
