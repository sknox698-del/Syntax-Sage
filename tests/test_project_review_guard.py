import unittest

from app.project_review_guard import (
    enforce_verified_project_errors,
)


class TestProjectReviewGuard(unittest.TestCase):

    def test_verified_error_replaces_ai_no_problems_claim(self):
        project_files = [
            {
                "path": "project/broken.py",
                "language": "Python",
                "content": "def broken(\n",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "Line 1: '(' was never closed",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        ai_response = """
5. Real problems

No real problems found.

6. Optional improvements

No optional improvements recommended.
"""

        result = enforce_verified_project_errors(
            ai_response,
            project_files,
        )

        self.assertIn(
            "5. Real problems",
            result,
        )

        self.assertIn(
            "project/broken.py",
            result,
        )

        self.assertIn(
            "never closed",
            result,
        )

        self.assertNotIn(
            "No real problems found.",
            result,
        )

    def test_all_verified_errors_are_preserved(self):
        project_files = [
            {
                "path": "project/first.py",
                "language": "Python",
                "content": "def first(\n",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "First syntax error",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "project/second.py",
                "language": "Python",
                "content": "def second(\n",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "Second syntax error",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        result = enforce_verified_project_errors(
            "5. Real problems\n\nNo real problems found.",
            project_files,
        )

        self.assertIn("project/first.py", result)
        self.assertIn("project/second.py", result)

    def test_optional_improvements_are_preserved(self):
        project_files = [
            {
                "path": "project/broken.py",
                "language": "Python",
                "content": "def broken(\n",
                "analysis": {
                    "total_lines": 1,
                    "code_lines": 1,
                    "blank_lines": 0,
                    "syntax_valid": False,
                    "syntax_error": "Syntax error",
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

        ai_response = """
5. Real problems

No real problems found.

6. Optional improvements

- Consider clearer naming.
"""

        result = enforce_verified_project_errors(
            ai_response,
            project_files,
        )

        self.assertIn(
            "Consider clearer naming.",
            result,
        )

    def test_response_is_unchanged_when_no_verified_errors_exist(self):
        project_files = [
            {
                "path": "project/good.py",
                "language": "Python",
                "content": "print('hello')",
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

        ai_response = """
5. Real problems

No real problems found.

6. Optional improvements

No optional improvements recommended.
""".strip()

        result = enforce_verified_project_errors(
            ai_response,
            project_files,
        )

        self.assertEqual(
            result,
            ai_response,
        )


if __name__ == "__main__":
    unittest.main()
