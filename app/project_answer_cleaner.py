import re


def question_requests_code(question):
    normalized = question.lower()

    code_markers = (
        "show me code",
        "write code",
        "give me code",
        "provide code",
        "rewrite",
        "fix the code",
        "example code",
        "code example",
        "patch",
    )

    return any(
        marker in normalized
        for marker in code_markers
    )


def question_requests_improvements(question):
    normalized = question.lower()

    improvement_markers = (
        "improve",
        "improvement",
        "improvements",
        "suggest",
        "suggestion",
        "recommend",
        "recommendation",
        "refactor",
        "better",
        "optimize",
    )

    return any(
        marker in normalized
        for marker in improvement_markers
    )


def remove_code_blocks(text):
    return re.sub(
        r"```.*?```",
        "",
        text,
        flags=re.DOTALL,
    )


def remove_unsolicited_improvement_sections(text):
    headings = (
        "optional improvements",
        "improvements",
        "suggestions",
        "recommendations",
    )

    lines = text.splitlines()
    cleaned_lines = []
    skipping = False

    for line in lines:
        stripped = line.strip()
        normalized = stripped.lower().strip("#*: ")

        if normalized in headings:
            skipping = True
            continue

        if skipping:
            if stripped.startswith("#"):
                skipping = False
            else:
                continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def clean_project_question_answer(
    answer,
    question,
):
    cleaned = answer

    if not question_requests_code(question):
        cleaned = remove_code_blocks(cleaned)

    if not question_requests_improvements(question):
        cleaned = remove_unsolicited_improvement_sections(
            cleaned
        )

    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    return cleaned.strip()
