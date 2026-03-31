def render_explanation(steps):
    return "
".join(["**How this answer was found:**"] + [f"- {s}" for s in steps])
