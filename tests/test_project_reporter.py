import unittest

from app.project_reporter import build_project_report


class TestProjectReporter(unittest.TestCase):

    def test_report_lists_languages(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": 'print("hello")',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "project/app.js",
                "language": "JavaScript",
                "content": 'console.log("hello");',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "2. Languages and technologies",
            report,
        )
        self.assertIn("- Python", report)
        self.assertIn("- JavaScript", report)

    def test_report_lists_python_structure(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": (
                    "def greet():\n"
                    "    pass\n\n"
                    "class Greeter:\n"
                    "    def say_hello(self):\n"
                    "        pass\n"
                ),
                "analysis": {
                    "total_lines": 6,
                    "code_lines": 5,
                    "blank_lines": 1,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [
                        {
                            "name": "greet",
                            "line": 1,
                        },
                    ],
                    "classes": [
                        {
                            "name": "Greeter",
                            "line": 4,
                        },
                    ],
                    "methods": [
                        {
                            "class": "Greeter",
                            "name": "say_hello",
                            "line": 5,
                        },
                    ],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "4. Functions, classes, and methods",
            report,
        )
        self.assertIn("Function: greet", report)
        self.assertIn("Class: Greeter", report)
        self.assertIn(
            "Method: Greeter.say_hello",
            report,
        )

    def test_report_lists_verified_issues(self):
        project_files = [
            {
                "path": "project/script.py",
                "language": "Python",
                "content": 'print("hello")',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "5. Verified issues",
            report,
        )
        self.assertIn(
            "[INFO]",
            report,
        )
        self.assertIn(
            "project/script.py",
            report,
        )

    def test_report_marks_omitted_file(self):
        project_files = [
            {
                "path": "project/main.py",
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
            },
        ]

        context = {
            "files": [],
            "trimmed_files": [],
            "omitted_files": [
                "project/main.py",
            ],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "project/main.py "
            "(Python, omitted from AI source context)",
            report,
        )

    def test_report_marks_trimmed_file(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": 'print("hello")',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [
                "project/main.py",
            ],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "project/main.py (Python, trimmed)",
            report,
        )

    def test_report_shows_issue_summary(self):
        project_files = [
            {
                "path": "project/script.py",
                "language": "Python",
                "content": 'print("hello")',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn("Issue summary", report)
        self.assertIn("- Errors: 0", report)
        self.assertIn("- Warnings: 0", report)
        self.assertIn("- Info: 1", report)

    def test_report_shows_project_health(self):
        project_files = [
            {
                "path": "project/script.py",
                "language": "Python",
                "content": 'print("hello")',
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "Project health",
            report,
        )
        self.assertIn(
            "- Status: Healthy",
            report,
        )

    def test_report_lists_project_dependencies(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import helper",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": ["helper"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "project/helper.py",
                "language": "Python",
                "content": "def help_me():\n    pass",
                "analysis": {
                    "total_lines": 2,
                    "code_lines": 2,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [
                        {
                            "name": "help_me",
                            "line": 1,
                        },
                    ],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "6. Project dependencies",
            report,
        )
        self.assertIn(
            "- project/main.py",
            report,
        )
        self.assertIn(
            "Depends on:",
            report,
        )
        self.assertIn(
            "project/helper.py",
            report,
        )
        self.assertIn(
            "Used by:",
            report,
        )

    def test_report_shows_no_dependencies_when_none_exist(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import os",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": ["os"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "6. Project dependencies",
            report,
        )

        self.assertIn(
            "No local Python dependencies detected.",
            report,
        )


    def test_report_lists_change_impact(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import helper",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": ["helper"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "project/helper.py",
                "language": "Python",
                "content": "def greet():\n    return 'Hello'",
                "analysis": {
                    "total_lines": 2,
                    "code_lines": 2,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": [],
                    "functions": [
                        {
                            "name": "greet",
                            "line": 1,
                        },
                    ],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "7. Change impact",
            report,
        )

        self.assertIn(
            "project/helper.py",
            report,
        )

        self.assertIn(
            "Potentially affects:",
            report,
        )

        self.assertIn(
            "project/main.py",
            report,
        )


    def test_report_shows_no_change_impact_when_none_exists(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import os",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": True,
                    "imports": ["os"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        context = {
            "files": project_files,
            "trimmed_files": [],
            "omitted_files": [],
        }

        report = build_project_report(
            "project",
            project_files,
            context,
        )

        self.assertIn(
            "7. Change impact",
            report,
        )

        self.assertIn(
            "No cross-file change impact detected.",
            report,
        )


if __name__ == "__main__":
    unittest.main()