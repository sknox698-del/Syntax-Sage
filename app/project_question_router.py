from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
    find_affected_files,
)
from app.issue_collector import (
    collect_project_issues,
    summarize_issues,
)


def classify_project_question(question):
    normalized = question.lower().strip()

    change_words = (
        "affected",
        "affect",
        "impact",
        "change",
        "depends on",
        "dependency",
        "dependencies",
        "used by",
    )

    problem_words = (
        "broken",
        "problem",
        "problems",
        "bug",
        "bugs",
        "error",
        "errors",
        "wrong",
    )

    if any(word in normalized for word in change_words):
        return "change_impact"

    if any(word in normalized for word in problem_words):
        return "problems"

    return "general"


def build_verified_change_impact_answer(
    question,
    project_files,
):
    dependency_map = build_dependency_map(project_files)
    reverse_map = build_reverse_dependency_map(
        dependency_map
    )

    normalized_question = question.lower()

    matching_paths = []

    for path in reverse_map:
        filename = path.replace("\\", "/").split("/")[-1]

        if (
            path.lower() in normalized_question
            or filename.lower() in normalized_question
        ):
            matching_paths.append(path)

    if not matching_paths:
        return None

    answer_lines = []

    for path in matching_paths:
        affected_files = find_affected_files(
            path,
            reverse_map,
        )

        filename = path.replace("\\", "/").split("/")[-1]

        if affected_files:
            answer_lines.append(
                f"Changing {filename} could affect:"
            )

            for affected_path in affected_files:
                answer_lines.append(
                    f"- {affected_path}"
                )
        else:
            answer_lines.append(
                f"No affected project files were identified "
                f"for {filename}."
            )

    return "\n".join(answer_lines)


def build_verified_problem_answer(project_files):
    issues = collect_project_issues(project_files)
    summary = summarize_issues(issues)

    errors = [
        issue
        for issue in issues
        if issue["severity"].lower() == "error"
    ]

    if not errors:
        return "No confirmed real problems found."

    lines = [
        f"Confirmed errors: {summary['error']}",
        "",
    ]

    for issue in errors:
        lines.append(
            f"- {issue['path']}: {issue['message']}"
        )

    return "\n".join(lines)


def answer_project_question_deterministically(
    question,
    project_files,
):
    question_type = classify_project_question(question)

    if question_type == "change_impact":
        answer = build_verified_change_impact_answer(
            question,
            project_files,
        )

        if answer is not None:
            return answer

    if question_type == "problems":
        return build_verified_problem_answer(
            project_files
        )

    return None
