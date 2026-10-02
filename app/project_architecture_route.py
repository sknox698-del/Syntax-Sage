"""Route verified structural architecture questions."""

from app.project_architecture_facts import build_project_architecture_facts
from app.project_architecture_presenter import format_verified_project_architecture

def _question_without_project_file_mentions(
    question,
    project_files,
):
    normalized = question.casefold()

    for file_info in project_files:
        path = file_info["path"].casefold()

        variants = {
            path,
            path.replace("\\", "/"),
            path.replace("/", "\\"),
        }

        basename = (
            path.replace("\\", "/")
            .rsplit("/", 1)[-1]
        )

        variants.add(basename)

        for variant in sorted(
            variants,
            key=len,
            reverse=True,
        ):
            normalized = normalized.replace(
                variant,
                " ",
            )

    return normalized

def answer_verified_architecture_question(question, project_files):
    """Answer narrowly scoped structural architecture questions."""
    normalized = (
    _question_without_project_file_mentions(
        question,
        project_files,
        )
    )
    architecture_requested = any(
        phrase in normalized
        for phrase in (
            "architecture", "project structure", "structural overview", "module structure",
        )
    )
    if not architecture_requested:
        return None

    # This explicit exclusion asks us to stay within the static-facts boundary.
    # Only remove the complete exclusion sentence; other requests remain checked.
    scope_text = ".".join(
        sentence for sentence in normalized.split(".")
        if sentence.strip() != (
            "do not infer runtime execution order, module responsibilities, or data flow"
        )
    )
    outside_scope = any(
        phrase in scope_text
        for phrase in (
            "responsibility", "responsibilities", "purpose", "runtime",
            "execution order", "call flow", "data flow", "work together",
        )
    )
    if outside_scope:
        return None

    facts = build_project_architecture_facts(project_files)
    return format_verified_project_architecture(facts)
