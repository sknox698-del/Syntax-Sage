import re

from app.issue_collector import collect_project_issues


def _extract_optional_improvements(ai_response):
    match = re.search(
        r"6\.\s*Optional improvements\s*(.*)",
        ai_response,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return "No optional improvements recommended."

    content = match.group(1).strip()

    if not content:
        return "No optional improvements recommended."

    return content


def enforce_verified_project_errors(
    ai_response,
    project_files,
):
    issues = collect_project_issues(project_files)

    verified_errors = [
        issue
        for issue in issues
        if issue["severity"].lower() == "error"
    ]

    if not verified_errors:
        return ai_response.strip()

    lines = [
        "5. Real problems",
        "",
    ]

    for issue in verified_errors:
        lines.append(
            f"- {issue['path']}: {issue['message']}"
        )

    optional_improvements = (
        _extract_optional_improvements(ai_response)
    )

    lines.extend(
        [
            "",
            "6. Optional improvements",
            "",
            optional_improvements,
        ]
    )

    return "\n".join(lines).strip()
