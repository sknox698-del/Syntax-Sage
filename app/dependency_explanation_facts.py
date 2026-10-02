from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
    get_change_impact,
)


def build_dependency_explanation_facts(
    target_path,
    project_files,
):
    """Collect verified facts for a dependency explanation."""
    dependency_map = build_dependency_map(project_files)
    reverse_map = build_reverse_dependency_map(
        dependency_map
    )
    impact = get_change_impact(
        target_path,
        project_files,
    )
    resolved_target = impact["target"]
    direct_dependents = (
        sorted(reverse_map.get(resolved_target, []))
        if impact["found"]
        else []
    )
    affected_files = list(impact["affected_files"])

    return {
        "found": impact["found"],
        "target": resolved_target,
        # Source-inspected traversal contract, not inferred from result lists.
        "traversal_direction": "dependents",
        "pending_initialization": "direct_dependents",
        "direct_dependents": direct_dependents,
        "affected_files": affected_files,
        "target_in_affected_files": (
            resolved_target in affected_files
        ),
    }
