"""Present verified static project architecture facts."""


def _format_names(values):
    if not values:
        return "None identified"

    return ", ".join(values)


def format_verified_project_architecture(facts):
    """Build an architecture overview from verified static facts."""
    lines = [
        "Verified project architecture overview",
        "",
        f"Analyzed files: {facts['file_count']}",
        (
            "Verified local dependency relationships: "
            f"{facts['local_dependency_count']}"
        ),
        "",
        (
            "The relationships below are static import/dependency "
            "relationships. They do not by themselves prove runtime "
            "execution order or function-call flow."
        ),
        "",
    ]

    for module in facts["modules"]:
        lines.extend([
            f"Module: {module['path']}",
            f"Language: {module['language']}",
            "Functions: " + _format_names(module["functions"]),
            "Classes: " + _format_names(module["classes"]),
            "Methods: " + _format_names(module["methods"]),
            "Depends on: " + _format_names(module["depends_on"]),
            "Used by: " + _format_names(module["used_by"]),
        ])

        if module["file_error"] is not None:
            lines.append(f"File error: {module['file_error']}")

        lines.append("")

    lines.extend([
        "Interpretation boundary:",
        (
            "This overview reports verified project structure. "
            "It does not infer a module's runtime role, execution "
            "sequence, or behavior beyond the supplied static facts."
        ),
    ])

    return "\n".join(lines)
