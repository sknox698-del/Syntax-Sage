"""Source-inspected semantic roles for verified Syntax Sage modules."""


VERIFIED_MODULE_ROLES = {
    "app/main.py": (
        "Coordinates the command-line interface and routes "
        "user actions to analysis, project scanning, change-impact "
        "and project-question workflows."
    ),
    "app/project_scanner.py": (
        "Discovers supported source files in a project directory "
        "while excluding ignored directories, unsupported files "
        "and symbolic-link entries."
    ),
    "app/project_analyzer.py": (
        "Uses the project scanner, reads discovered files and "
        "attaches static code-analysis results or per-file read errors."
    ),
    "app/language_router.py": (
        "Identifies supported programming languages from filename "
        "extensions using a fixed extension map."
    ),
    "app/dependency_analyzer.py": (
        "Builds static local Python dependency relationships, "
        "reverse dependency relationships and change-impact results."
    ),
    "app/context_manager.py": (
        "Selects and limits source content supplied to AI prompts "
        "using project, file and preferred-file character budgets."
    ),
    "app/prompt_builder.py": (
        "Constructs code-review and project-question prompts, "
        "including focused and compact context variants."
    ),
    "app/ai_client.py": (
        "Sends prompts to the configured local Ollama model and "
        "provides normal and streaming response interfaces."
    ),
}


def get_verified_module_role(path):
    normalized = path.replace("\\", "/").casefold()

    for verified_path, role in VERIFIED_MODULE_ROLES.items():
        if verified_path.casefold() == normalized:
            return role

    return None