MAX_PROJECT_CHARACTERS = 12000
MAX_FILE_CHARACTERS = 4000
MAX_PREFERRED_FILE_CHARACTERS = 5000


PRIORITY_FILENAMES = {
    "main.py": 1,
    "app.py": 1,
    "index.js": 1,
    "server.js": 1,
    "package.json": 2,
    "requirements.txt": 2,
    "pyproject.toml": 2,
    "pom.xml": 2,
    "build.gradle": 2,
}


def trim_content(content, max_characters=MAX_FILE_CHARACTERS):
    if len(content) <= max_characters:
        return content, False

    trimmed = content[:max_characters]

    return trimmed, True


def get_file_priority(file_info):
    path = file_info["path"].lower()

    filename = path.replace("\\", "/").split("/")[-1]

    priority = PRIORITY_FILENAMES.get(filename, 10)

    content_length = len(
        file_info.get("content", "")
    )

    return priority, content_length


def build_project_context(project_files, preferred_paths=None):
    context_files = []
    omitted_files = []
    trimmed_files = []

    total_characters = 0

    preferred = {
        str(path).replace("\\", "/").casefold()
        for path in (preferred_paths or [])
    }

    def context_priority(file_info):
        normalized = (
            file_info["path"]
            .replace("\\", "/")
            .casefold()
        )

        is_preferred = normalized in preferred

        return (
            0 if is_preferred else 1,
            *get_file_priority(file_info),
        )

    sorted_files = sorted(
        project_files,
        key=context_priority,
    )

    for file_info in sorted_files:
        if "content" not in file_info:
            omitted_files.append(file_info["path"])
            continue

        remaining = (
            MAX_PROJECT_CHARACTERS
            - total_characters
        )

        if remaining <= 0:
            omitted_files.append(file_info["path"])
            continue

        normalized_path = (
            file_info["path"]
            .replace("\\", "/")
            .casefold()
        )

        file_limit = (
            MAX_PREFERRED_FILE_CHARACTERS
            if normalized_path in preferred
            else MAX_FILE_CHARACTERS
        )

        content, was_trimmed = trim_content(
            file_info["content"],
            max_characters=file_limit,
        )

        if len(content) > remaining:
            content = content[:remaining]
            was_trimmed = True

        if was_trimmed:
            trimmed_files.append(file_info["path"])

        context_files.append(
            {
                "path": file_info["path"],
                "language": file_info["language"],
                "analysis": file_info.get(
                    "analysis",
                    {},
                ),
                "content": content,
                "trimmed": was_trimmed,
            }
        )

        total_characters += len(content)

    return {
        "files": context_files,
        "total_characters": total_characters,
        "files_included": len(context_files),
        "files_available": len(project_files),
        "trimmed_files": trimmed_files,
        "omitted_files": omitted_files,
    }


if __name__ == "__main__":
    sample = "A" * 5000

    trimmed, was_trimmed = trim_content(sample)

    print(f"Original length: {len(sample)}")
    print(f"Trimmed length: {len(trimmed)}")
    print(f"Was trimmed: {was_trimmed}")