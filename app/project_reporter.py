from app.issue_collector import (
    collect_project_issues,
    get_project_health,
    summarize_issues,
)
from app.dependency_analyzer import (
    build_dependency_map,
    build_reverse_dependency_map,
    find_affected_files,
)


def build_project_report(project_path, project_files, context):
    languages = sorted(
        {
            file_info["language"]
            for file_info in project_files
        }
    )

    lines = []

    lines.append("1. Project overview")
    lines.append("")
    lines.append(
        f"Project: {project_path}"
    )
    lines.append(
        f"Supported source files found: {len(project_files)}"
    )
    lines.append("")

    lines.append("2. Languages and technologies")
    lines.append("")

    for language in languages:
        lines.append(f"- {language}")

    lines.append("")
    lines.append("3. Project files")
    lines.append("")

    included_paths = {
        file_info["path"]
        for file_info in context["files"]
    }

    trimmed_paths = set(context["trimmed_files"])
    omitted_paths = set(context["omitted_files"])

    for file_info in project_files:
        path = file_info["path"]
        status = "fully included"

        if path in trimmed_paths:
            status = "trimmed"

        elif path in omitted_paths:
            status = "omitted from AI source context"

        elif path not in included_paths:
            status = "not included"

        lines.append(
            f"- {path} "
            f"({file_info['language']}, {status})"
        )

    lines.append("")
    lines.append("4. Functions, classes, and methods")
    lines.append("")

    found_structure = False

    for file_info in project_files:
        analysis = file_info.get("analysis", {})

        functions = analysis.get("functions", [])
        methods = analysis.get("methods", [])
        classes = analysis.get("classes", [])

        for function in functions:
            found_structure = True
            lines.append(
                f"- Function: {function['name']} "
                f"in {file_info['path']} "
                f"(line {function['line']})"
            )

        for class_info in classes:
            found_structure = True
            lines.append(
                f"- Class: {class_info['name']} "
                f"in {file_info['path']} "
                f"(line {class_info['line']})"
            )

        for method in methods:
            found_structure = True
            lines.append(
                f"- Method: "
                f"{method['class']}.{method['name']} "
                f"in {file_info['path']} "
                f"(line {method['line']})"
            )

    if not found_structure:
        lines.append(
            "No functions, classes, or methods were detected."
        )

    lines.append("")
    lines.append("5. Verified issues")
    lines.append("")

    issues = collect_project_issues(project_files)
    summary = summarize_issues(issues)
    health = get_project_health(summary)

    lines.append("Project health")
    lines.append("")

    lines.append(
        f"- Status: {health}"
    )

    lines.append("")

    lines.append("Issue summary")
    lines.append("")

    lines.append(
        f"- Errors: {summary['error']}"
    )

    lines.append(
        f"- Warnings: {summary['warning']}"
    )

    lines.append(
        f"- Info: {summary['info']}"
    )

    lines.append("")

    if not issues:
        lines.append("No verified issues found.")
    else:
        for issue in issues:
            lines.append(
                f"- [{issue['severity'].upper()}] "
                f"{issue['path']}: "
                f"{issue['message']}"
            )

    lines.append("")
    lines.append("6. Project dependencies")
    lines.append("")

    dependency_map = build_dependency_map(project_files)
    reverse_dependency_map = build_reverse_dependency_map(
        dependency_map
    )

    found_dependencies = False

    for path in sorted(dependency_map):
        dependencies = dependency_map[path]
        dependents = reverse_dependency_map.get(path, [])

        if not dependencies and not dependents:
            continue

        found_dependencies = True

        lines.append(f"- {path}")

        if dependencies:
            lines.append("  Depends on:")

            for dependency in dependencies:
                lines.append(
                    f"  - {dependency}"
                )

        if dependents:
            lines.append("  Used by:")

            for dependent in dependents:
                lines.append(
                    f"  - {dependent}"
                )

        lines.append("")

    if not found_dependencies:
        lines.append(
            "No local Python dependencies detected."
        )

    lines.append("")
    lines.append("7. Change impact")
    lines.append("")

    found_impact = False

    for path in sorted(reverse_dependency_map):
        affected_files = find_affected_files(
            path,
            reverse_dependency_map,
        )

        if not affected_files:
            continue

        found_impact = True

        lines.append(f"- {path}")
        lines.append("  Potentially affects:")

        for affected_path in affected_files:
            lines.append(
                f"  - {affected_path}"
            )

        lines.append("")

    if not found_impact:
        lines.append(
            "No cross-file change impact detected."
        )

    return "\n".join(lines)