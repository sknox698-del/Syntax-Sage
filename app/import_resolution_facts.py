"""Verified facts about static local Python import resolution."""

from app.dependency_analyzer import (
    _module_names_for_path,
    _resolve_local_import,
)


def build_import_resolution_facts(target_path, project_files):
    """Describe imports resolved by the existing analyzer."""
    target = next(
        (
            item
            for item in project_files
            if item["path"] == target_path
            and item["language"] == "Python"
        ),
        None,
    )
    if target is None:
        return None

    analysis = target.get("analysis")
    # Don't mistake missing analysis for a file with no imports.
    if not isinstance(analysis, dict):
        return None
    imports = analysis.get("imports")
    if not isinstance(imports, list):
        return None

    module_lookup = {}
    for file_info in project_files:
        if file_info["language"] != "Python":
            continue
        for name in _module_names_for_path(file_info["path"]):
            module_lookup.setdefault(name, []).append(file_info["path"])

    import_results = []
    for imported_module in imports:
        resolved = _resolve_local_import(
            imported_module,
            module_lookup,
            target_path,
        )
        import_results.append({
            "import": imported_module,
            "resolved_local_path": resolved,
        })

    return {
        "target": target_path,
        # Policy fields describe the source-inspected resolver contract.
        # They are not conclusions inferred from unresolved imports.
        "resolution_kind": "static_local_matching",
        "module_name_generation": "dotted_path_suffixes",
        "prefix_order": "longest_to_shortest",
        "excludes_self_matches": True,
        "ambiguity_policy": "stop_without_shorter_prefix_fallback",
        "unresolved_meaning": (
            "No unique local match was resolved; the import may be absent, "
            "ambiguous, or excluded as a self-import. "
            "This does not establish that it is external."
        ),
        "import_results": import_results,
    }
