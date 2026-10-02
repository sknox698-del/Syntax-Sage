from app.code_analyzer import analyze_code
from app.file_reader import read_code_file
from app.project_scanner import scan_project


def analyze_project(project_path):
    files, error = scan_project(project_path)

    if error:
        return None, error

    project_files = []

    for file_info in files:
        filepath = file_info["path"]
        language = file_info["language"]

        content, read_error = read_code_file(filepath)

        if read_error:
            project_files.append(
                {
                    "path": filepath,
                    "language": language,
                    "error": read_error,
                }
            )
            continue

        analysis = analyze_code(content, language)

        project_files.append(
            {
                "path": filepath,
                "language": language,
                "analysis": analysis,
                "content": content,
            }
        )

    return project_files, None