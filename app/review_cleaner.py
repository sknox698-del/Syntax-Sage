def clean_optional_improvements(text, force_no_optional=False):
    if not force_no_optional:
        return text

    lines = text.splitlines()

    cleaned_lines = []
    found_optional_section = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if (
            stripped.startswith("3.")
            and "optional improvements" in lower
        ):
            found_optional_section = True

            cleaned_lines.append(line)
            cleaned_lines.append("")
            cleaned_lines.append(
                "No optional improvements recommended."
            )

            break

        cleaned_lines.append(line)

    if not found_optional_section:
        cleaned_lines.append("")
        cleaned_lines.append("3. Optional improvements")
        cleaned_lines.append("")
        cleaned_lines.append(
            "No optional improvements recommended."
        )

    return "\n".join(cleaned_lines)