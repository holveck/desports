def parse_with_llm(question: str):
    q = question.lower()

    if "highest combined score" in q:
        return {
            "intent": "aggregation",
            "filters": {
                "sport": "basketball",
                "gender": "boys",
                "year": None,
                "recognition_type": None
            },
            "group_by": None,
            "aggregation": {"function": "max", "field": "combined_score"},
            "derived_metric": {
                "name": "combined_score",
                "formula": "champion_score + runner_up_score"
            }
        }

    if "most" in q and "won" in q:
        return {
            "intent": "ranking",
            "filters": {
                "sport": None,
                "gender": None,
                "year": None,
                "recognition_type": None
            },
            "group_by": "champion",
            "aggregation": {"function": "count", "field": "year"},
            "derived_metric": None
        }

    return {"intent": "unsupported", "filters": {}, "group_by": None, "aggregation": None, "derived_metric": None}
