from app.import_resolution_facts import build_import_resolution_facts
from app.import_resolution_presenter import format_verified_import_facts
from app.prompt_builder import find_mentioned_project_paths
from app.dependency_explanation_facts import build_dependency_explanation_facts
from app.dependency_answer_presenter import format_verified_dependency_facts


def answer_verified_dependency_question(question, project_files):
    """Answer narrowly scoped dependency explanations using verified facts."""
    normalized = question.casefold()
    explanation_requested = any(
        term in normalized
        for term in ("explain", "describe", "how does", "how do")
    )
    dependency_requested = any(
        term in normalized
        for term in (
            "get_change_impact",
            "affected files",
            "change impact",
            "dependency traversal",
        )
    )
    # These topics require evidence or explanations beyond this presenter.
    outside_scope = any(
        term in normalized
        for term in (
            "import", "what does", "purpose", "rewrite", "refactor",
            "improve", "example", "write code", "bug", "error",
        )
    )
    if not explanation_requested or not dependency_requested or outside_scope:
        return None

    matches = find_mentioned_project_paths(question, project_files)
    if len(matches) != 1:
        return None

    facts = build_dependency_explanation_facts(matches[0], project_files)
    return format_verified_dependency_facts(facts)


def answer_verified_combined_dependency_question(question, project_files):
    """Explain Syntax Sage's inspected resolver and traversal contracts."""
    normalized = question.casefold()
    asks_for_explanation = any(
        word in normalized
        for word in ("explain", "describe", "how does")
    )
    asks_about_imports = "import" in normalized
    asks_about_impact = any(
        phrase in normalized
        for phrase in ("affected files", "get_change_impact", "change impact")
    )
    if not all((asks_for_explanation, asks_about_imports, asks_about_impact)):
        return None

    matches = find_mentioned_project_paths(question, project_files)
    if len(matches) != 1:
        return None
    target = matches[0]
    # Documents the inspected implementation, not arbitrary modules.
    filename = target.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    if filename != "dependency_analyzer.py":
        return None

    import_facts = build_import_resolution_facts(target, project_files)
    if import_facts is None:
        return None
    dependency_facts = build_dependency_explanation_facts(target, project_files)
    import_answer = format_verified_import_facts(
        import_facts, include_import_results=False,
    )
    dependency_answer = format_verified_dependency_facts(dependency_facts)
    missing_target_contract = (
        "If a requested target is absent from the analyzed dependency map, "
        "get_change_impact() returns:\n"
        "- found: False\n"
        "- target: the original requested path\n"
        "- affected_files: []"
    )
    return "\n\n".join((import_answer, dependency_answer, missing_target_contract))
