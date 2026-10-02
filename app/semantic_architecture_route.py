"""Route verified semantic architecture questions."""

from app.project_architecture_facts import (
    build_project_architecture_facts,
)
from app.semantic_architecture_presenter import (
    format_verified_semantic_architecture,
)


def answer_verified_semantic_architecture_question(
    question,
    project_files,
):
    """Answer narrowly scoped module-responsibility questions."""

    normalized = question.casefold()

    semantic_requested = any(
        phrase in normalized
        for phrase in (
            "module responsibility",
            "module responsibilities",
            "module role",
            "module roles",
            "what does each module do",
            "what each module does",
            "purpose of each module",
            "semantic architecture",
        )
    )

    if not semantic_requested:
        return None

    # Runtime behavior is outside the verified role contracts.
    outside_scope = any(
        phrase in normalized
        for phrase in (
            "runtime flow",
            "runtime execution",
            "execution order",
            "call flow",
            "data flow",
        )
    )

    if outside_scope:
        return None

    facts = build_project_architecture_facts(
        project_files
    )

    return format_verified_semantic_architecture(
        facts
    )