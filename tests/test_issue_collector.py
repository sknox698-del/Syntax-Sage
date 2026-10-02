import unittest

from app.issue_collector import (
    collect_project_issues,
    get_project_health,
    summarize_issues,
)

class TestIssueCollector(unittest.TestCase):

    def test_project_health_errors_found(self):
        summary = {
            "error": 1,
            "warning": 0,
            "info": 0,
        }

        self.assertEqual(
            get_project_health(summary),
            "Errors found",
        )

    def test_project_health_needs_review(self):
        summary = {
            "error": 0,
            "warning": 2,
            "info": 0,
        }

        self.assertEqual(
            get_project_health(summary),
            "Needs review",
        )

    def test_project_health_healthy_with_info(self):
        summary = {
            "error": 0,
            "warning": 0,
            "info": 3,
        }

        self.assertEqual(
            get_project_health(summary),
            "Healthy",
        )

    def test_collects_python_syntax_error(self):
        project_files = [
            {
                "path": "broken.py",
                "language": "Python",
                "analysis": {
                    "syntax_valid": False,
                    "syntax_error": "Line 1: expected ':'",
                },
                "content": "def greet(name)",
            }
        ]

        issues = collect_project_issues(project_files)

        self.assertEqual(len(issues), 1)
        self.assertEqual(
            issues[0]["type"],
            "syntax_error",
        )
        self.assertEqual(
            issues[0]["severity"],
            "error",
        )
        self.assertEqual(
            issues[0]["path"],
            "broken.py",
        )

    def test_collects_empty_file_warning(self):
        project_files = [
            {
                "path": "empty.py",
                "language": "Python",
                "analysis": {
                    "total_lines": 0,
                    "blank_lines": 0,
                    "code_lines": 0,
                    "syntax_valid": True,
                    "syntax_error": None,
                },
                "content": "",
            }
        ]

        issues = collect_project_issues(project_files)

        self.assertEqual(len(issues), 1)

        self.assertEqual(
            issues[0]["severity"],
            "warning",
        )

        self.assertEqual(
            issues[0]["type"],
            "empty_file",
        )

        self.assertEqual(
            issues[0]["message"],
            "The file contains no code.",
        )

    def test_collects_file_read_error(self):
        project_files = [
            {
                "path": "unreadable.py",
                "language": "Python",
                "error": "Could not read file.",
            }
        ]

        issues = collect_project_issues(project_files)

        self.assertEqual(len(issues), 1)

        self.assertEqual(
            issues[0]["type"],
            "file_read_error",
        )

    def test_valid_file_has_no_issues(self):
        project_files = [
            {
                "path": "good.py",
                "language": "Python",
                "analysis": {
                    "syntax_valid": True,
                    "syntax_error": None,
                    "functions": [
                        {
                            "name": "greet",
                            "line": 1,
                            "parameters": ["name"],
                        }
                    ],
                    "classes": [],
                    "methods": [],
                    "code_lines": 2,
                },
                "content": (
                    "def greet(name):\n"
                    "    return f'Hello, {name}!'"
                ),
            }
        ]

        issues = collect_project_issues(project_files)

        self.assertEqual(issues, [])

    def test_summarizes_issue_severity(self):
        issues = [
            {
                "severity": "error",
            },
            {
                "severity": "error",
            },
            {
                "severity": "warning",
            },
            {
                "severity": "info",
            },
        ]

        summary = summarize_issues(issues)

        self.assertEqual(summary["error"], 2)
        self.assertEqual(summary["warning"], 1)
        self.assertEqual(summary["info"], 1)

    def test_collects_script_style_info(self):
        project_files = [
            {
                "path": "script.py",
                "language": "Python",
                "analysis": {
                    "total_lines": 1,
                    "blank_lines": 0,
                    "code_lines": 1,
                    "syntax_valid": True,
                    "syntax_error": None,
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
                "content": 'print("Hello")',
            }
        ]

        issues = collect_project_issues(project_files)

        self.assertEqual(len(issues), 1)

        self.assertEqual(
            issues[0]["severity"],
            "info",
        )

        self.assertEqual(
            issues[0]["type"],
            "script_style_file",
        )

    def test_empty_init_file_is_not_a_warning(self):
        project_files = [
            {
                "path": "app/__init__.py",
                "language": "Python",
                "content": "",
                "analysis": {
                    "total_lines": 0,
                    "code_lines": 0,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            }
        ]

        issues = collect_project_issues(project_files)

        warnings = [
            issue
            for issue in issues
            if issue["severity"].lower() == "warning"
        ]

        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()