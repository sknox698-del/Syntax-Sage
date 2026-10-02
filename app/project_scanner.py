from pathlib import Path

from app.language_router import detect_language


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}


def scan_project(project_path):
    root = Path(project_path)

    if not root.exists():
        return None, "Project folder not found."

    if not root.is_dir():
        return None, "The project path is not a folder."

    files = []

    for path in root.rglob("*"):
        if path.is_symlink():
            continue

        if not path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        language = detect_language(path.name)

        if language == "Unknown":
            continue

        files.append(
            {
                "path": str(path),
                "language": language,
            }
        )

    return files, None

if __name__ == "__main__":
    project_files, error = scan_project("projects/scanner_test")

    if error:
        print(f"Error: {error}")
    else:
        for file_info in project_files:
            print(
                f"{file_info['path']} -> "
                f"{file_info['language']}"
            )