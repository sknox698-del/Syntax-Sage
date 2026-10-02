"""Present verified dependency facts safely."""

from app.dependency_claim_validator import validate_dependency_claims


def format_verified_dependency_facts(facts):
    """Build an explanation from a trusted deterministic fact record."""
    evidence_check = validate_dependency_claims(facts, facts)
    if not evidence_check["valid"]:
        raise ValueError("A complete, correctly typed verified fact record is required.")
    if (
        facts["traversal_direction"] != "dependents"
        or facts["pending_initialization"] != "direct_dependents"
    ):
        raise ValueError("Unsupported verified traversal contract.")

    target = facts["target"]
    if not facts["found"]:
        return (
            f"Target: {target}\n"
            "The target was not found in the analyzed dependency map.\n"
            "get_change_impact() returns:\n"
            "- found: False\n"
            f"- target: {target}\n"
            "- affected_files: []"
        )

    direct = facts["direct_dependents"]
    affected = facts["affected_files"]
    lines = [
        f"Target: {target}",
        "",
        "Dependency traversal:",
        "- Traversal follows dependents, not dependencies.",
        "- The pending list starts with direct dependents.",
        "- Further dependents are then visited.",
        "",
        "Direct dependents:",
    ]
    lines.extend(f"- {path}" for path in direct)
    if not direct:
        lines.append("- None identified.")

    lines.extend(["", "Potentially affected files:"])
    lines.extend(f"- {path}" for path in affected)
    if not affected:
        lines.append("- No affected project files were identified.")

    lines.extend([
        "",
        (
            "The target itself is included in affected_files."
            if facts["target_in_affected_files"]
            else "The target itself is excluded from affected_files."
        ),
        "These dependency relationships could affect dependent files; "
        "those files may require review after a change. They do not prove breakage.",
        "",
        "get_change_impact() returns:",
        "- found: True",
        f"- target: {target}",
        f"- affected_files: {affected!r}",
    ])
    return "\n".join(lines)


def validate_and_present_dependency_claims(claims, facts):
    """Validate structured claims, but render only independently verified facts."""
    validation = validate_dependency_claims(claims, facts)
    answer = format_verified_dependency_facts(facts)
    if not validation["valid"]:
        answer = (
            "The AI dependency claims could not be validated. "
            "Showing verified facts instead.\n\n" + answer
        )
    return {
        "claims_valid": validation["valid"],
        "errors": list(validation["errors"]),
        "answer": answer,
    }
