def needs_clarification(df):
    return df is not None and len(df) > 1

def build_clarifying_question(df):
    return df[["year", "sport", "gender"]].drop_duplicates()
