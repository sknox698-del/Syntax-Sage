"""Present verified static Python import-resolution facts."""


def format_verified_import_facts(facts, include_import_results=True):
    """Render the inspected resolver policy and actual per-import results."""
    if facts is None:
        return (
            "Import-resolution evidence is unavailable "
            "for the requested file."
        )
    if (
        not isinstance(facts, dict)
        or facts.get("resolution_kind") != "static_local_matching"
        or facts.get("module_name_generation") != "dotted_path_suffixes"
        or facts.get("prefix_order") != "longest_to_shortest"
        or facts.get("excludes_self_matches") is not True
        or facts.get("ambiguity_policy") != "stop_without_shorter_prefix_fallback"
    ):
        return "The import-resolution policy could not be verified."

    lines = [
        "Verified import-resolution explanation",
        "",
        "Syntax Sage performs static local Python "
        "import matching, not full runtime import resolution.",
        "",
        "1. It generates dotted module-name suffixes "
        "from analyzed Python file paths.",
        "2. Package __init__.py files represent their "
        "containing package.",
        "3. It strips leading dots from imported module names, "
        "then tries imported-module prefixes from longest to shortest.",
        "4. It excludes the importing file itself.",
        "5. A unique candidate match resolves to that local file.",
        "6. An ambiguous candidate stops resolution without guessing "
        "or falling back to a shorter prefix.",
        "7. If no candidate resolves, the result is None.",
    ]
    if include_import_results:
        lines.extend(["", f"Analyzed imports for: {facts['target']}"])
        results = facts["import_results"]
        if not results:
            lines.append("No imports recorded in the supplied analysis.")
        for result in results:
            resolved = result["resolved_local_path"]
            description = (
                resolved if resolved is not None else "No unique local match"
            )
            lines.append(f"- {result['import']}: {description}")

        if any(result["resolved_local_path"] is None for result in results):
            lines.extend([
                "",
                "Unresolved imports are not automatically classified as external. "
                "A missing match may reflect an absent module, ambiguity, "
                "or an excluded self-import; these results do not identify which reason applies.",
            ])
    return "\n".join(lines)
