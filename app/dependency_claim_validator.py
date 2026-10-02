"""Validate structured dependency claims against verified facts."""

REQUIRED_FIELDS = {
    "found",
    "target",
    "traversal_direction",
    "pending_initialization",
    "direct_dependents",
    "affected_files",
    "target_in_affected_files",
}

_FIELD_TYPES = {
    "found": bool,
    "target": str,
    "traversal_direction": str,
    "pending_initialization": str,
    "direct_dependents": list,
    "affected_files": list,
    "target_in_affected_files": bool,
}


def _field_has_expected_type(field, value):
    # Exact types prevent integers from passing as booleans.
    if type(value) is not _FIELD_TYPES[field]:
        return False
    if _FIELD_TYPES[field] is list:
        return all(type(item) is str for item in value)
    return True


def validate_dependency_claims(claims, facts):
    """Accept only complete, accurate claims; do not validate free-form prose."""
    if not isinstance(claims, dict):
        return {
            "valid": False,
            "errors": ["Claims must be a JSON object."],
        }
    if not isinstance(facts, dict):
        return {
            "valid": False,
            "errors": ["Verified facts are unavailable."],
        }

    errors = []
    missing_facts = REQUIRED_FIELDS - facts.keys()
    for field in sorted(missing_facts):
        errors.append(f"Verified facts missing required field: {field}.")
    for field in sorted(REQUIRED_FIELDS & facts.keys()):
        if not _field_has_expected_type(field, facts[field]):
            errors.append(f"Verified facts have invalid type for field: {field}.")

    # Incomplete or malformed evidence cannot authorize any claim.
    if errors:
        return {"valid": False, "errors": errors}

    for field in sorted(REQUIRED_FIELDS - claims.keys()):
        errors.append(f"Missing required claim field: {field}.")
    for field in sorted(claims.keys() - REQUIRED_FIELDS, key=repr):
        errors.append(f"Unexpected claim field: {field}.")
    for field in sorted(REQUIRED_FIELDS & claims.keys()):
        if not _field_has_expected_type(field, claims[field]):
            errors.append(f"Invalid type for claim field: {field}.")
        elif claims[field] != facts[field]:
            errors.append(f"Claim differs from verified facts: {field}.")

    return {"valid": not errors, "errors": errors}
