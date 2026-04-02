def build_card_descriptor(
    *,
    title,
    primary_value,
    secondary_value=None,
    school_id=None,
    details_rows=None,
    school_styles=None,
):
    accent_color = None

    if school_id and school_styles and school_id in school_styles:
        accent_color = school_styles[school_id]["primary_color"]

    return {
        "title": title,
        "primary_value": primary_value,
        "secondary_value": secondary_value,
        "school_id": school_id,
        "accent_color": accent_color,
        "details_rows": details_rows,
    }
