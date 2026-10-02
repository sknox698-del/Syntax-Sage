"""Verified structural facts about an analyzed project."""

from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
)


def _symbol_names(items):
    """Normalize analyzer symbol records into names."""
    names = []

    for item in items or []:
        if isinstance(item, str):
            names.append(item)
            continue

        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str):
                names.append(name)

    return sorted(set(names))


def build_project_architecture_facts(project_files):
    """Build deterministic structural project facts."""
    dependency_map = build_dependency_map(project_files)
    reverse_map = build_reverse_dependency_map(dependency_map)
    modules = []

    for file_info in sorted(
        project_files,
        key=lambda item: item["path"].casefold(),
    ):
        path = file_info["path"]
        analysis = file_info.get("analysis", {})
        if not isinstance(analysis, dict):
            analysis = {}

        modules.append(
            {
                "path": path,
                "language": file_info["language"],
                "functions": _symbol_names(analysis.get("functions", [])),
                "classes": _symbol_names(analysis.get("classes", [])),
                "methods": _symbol_names(analysis.get("methods", [])),
                "depends_on": list(dependency_map.get(path, [])),
                "used_by": list(reverse_map.get(path, [])),
                "file_error": file_info.get("error"),
            }
        )

    return {
        "file_count": len(project_files),
        "local_dependency_count": sum(
            len(paths) for paths in dependency_map.values()
        ),
        "modules": modules,
    }
