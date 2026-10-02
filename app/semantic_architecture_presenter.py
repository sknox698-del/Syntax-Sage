from app.module_role_facts import (
    get_verified_module_role,
)


def format_verified_semantic_architecture(
    architecture_facts,
):
    lines = [
        "Verified semantic architecture overview",
        "",
        (
            "Module responsibilities below are included only "
            "when a source-inspected verified role exists."
        ),
        "",
    ]

    for module in architecture_facts["modules"]:
        path = module["path"]

        lines.append(f"Module: {path}")

        role = get_verified_module_role(path)

        if role is not None:
            lines.append(
                f"Verified responsibility: {role}"
            )
        else:
            lines.append(
                "Verified responsibility: Not established."
            )

        if module["depends_on"]:
            lines.append(
                "Static dependencies: "
                + ", ".join(module["depends_on"])
            )
        else:
            lines.append(
                "Static dependencies: None identified"
            )

        if module["used_by"]:
            lines.append(
                "Statically used by: "
                + ", ".join(module["used_by"])
            )
        else:
            lines.append(
                "Statically used by: None identified"
            )

        lines.append("")

    lines.extend([
        "Interpretation boundary:",
        (
            "Verified responsibilities come from "
            "source-inspected module-role contracts."
        ),
        (
            "Static dependency relationships do not prove "
            "runtime execution order or call flow."
        ),
    ])

    return "\n".join(lines)