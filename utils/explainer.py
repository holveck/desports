def render_explanation(steps):
    lines = ["How this answer was found:"]
    for step in steps:
        lines.append(f"- {step}")
    return "\n".join(lines)
