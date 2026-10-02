"""Guard single-file AI reviews with verified analysis facts."""

import re


def _extract_what_code_does(ai_response):
    match = re.search(
        r"1\.\s*\**What the code does\**\s*:?\s*(.*?)(?=\n\s*2\.)",
        ai_response,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return "No AI explanation available."

    content = match.group(1).strip()

    return content or "No AI explanation available."


def enforce_verified_single_file_review(
    ai_response,
    analysis,
):
    """Present AI explanation but only verified problems."""

    explanation = _extract_what_code_does(
        ai_response
    )

    lines = [
        "1. What the code does",
        "",
        explanation,
        "",
        "2. Verified problems",
        "",
    ]

    if analysis.get("syntax_valid") is False:
        lines.append(
            "Syntax error: "
            f"{analysis.get('syntax_error')}"
        )
    else:
        lines.append(
            "No verified problems found by static analysis."
        )

    return "\n".join(lines).strip()