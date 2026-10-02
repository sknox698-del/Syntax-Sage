def collect_project_issues(project_files):
    issues = []

    for file_info in project_files:
        path = file_info["path"]

        if "error" in file_info:
            issues.append(
                {
                    "path": path,
                    "severity": "error",
                    "type": "file_read_error",
                    "message": file_info["error"],
                }
            )
            continue
        
        analysis = file_info.get("analysis", {})
        filename = file_info["path"].replace("\\", "/").rsplit("/", 1)[-1]

        is_empty_package_init = (
            file_info["language"] == "Python"
            and filename == "__init__.py"
        )

        if analysis.get("syntax_valid") is False:
            issues.append(
                {
                    "path": path,
                    "severity": "error",
                    "type": "syntax_error",
                    "message": analysis.get(
                        "syntax_error",
                        "Unknown syntax error.",
                    ),
                }
            )

        elif (
            analysis.get("code_lines") == 0
            and not is_empty_package_init
        ):
            issues.append(
                {
                    "path": path,
                    "severity": "warning",
                    "type": "empty_file",
                    "message": "The file contains no code.",
                }
            )

        elif (
            file_info.get("language") == "Python"
            and analysis.get("code_lines", 0) > 0
            and not analysis.get("functions")
            and not analysis.get("classes")
            and not analysis.get("methods")
        ):
            issues.append(
                {
                    "path": path,
                    "severity": "info",
                    "type": "script_style_file",
                    "message": (
                        "The file contains executable Python code "
                        "but no detected functions, classes, or methods."
                    ),
                }
            )

    return issues


def summarize_issues(issues):
    summary = {
        "error": 0,
        "warning": 0,
        "info": 0,
    }

    for issue in issues:
        severity = issue.get("severity")

        if severity in summary:
            summary[severity] += 1

    return summary

def get_project_health(summary):
    if summary["error"] > 0:
        return "Errors found"

    if summary["warning"] > 0:
        return "Needs review"

    return "Healthy"