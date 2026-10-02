import unittest

from app.prompt_builder import build_project_review_prompt


class TestProjectPromptDependencies(unittest.TestCase):

    def test_project_prompt_contains_verified_dependencies(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import helper\n\nhelper.greet()",
                "analysis": {
                    "total_lines": 3,
                    "code_lines": 2,
                    "blank_lines": 1,
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

        prompt = build_project_review_prompt(
            "project",
            project_files,
        )

        self.assertIn(
            "VERIFIED PROJECT DEPENDENCIES",
            prompt,
        )

        self.assertIn(
            '"depends_on"',
            prompt,
        )

        self.assertIn(
            '"used_by"',
            prompt,
        )

        self.assertIn(
            "project/main.py",
            prompt,
        )

        self.assertIn(
            "project/helper.py",
            prompt,
        )

    def test_project_prompt_does_not_treat_external_import_as_local(self):
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

        prompt = build_project_review_prompt(
            "project",
            project_files,
        )

        self.assertIn(
            '"project/main.py": []',
            prompt,
        )

        self.assertNotIn(
            '"os.py"',
            prompt,
        )


    def test_project_prompt_contains_verified_change_impact(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "content": "import helper\n\nhelper.greet()",
                "analysis": {
                    "total_lines": 3,
                    "code_lines": 2,
                    "blank_lines": 1,
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

        prompt = build_project_review_prompt(
            "project",
            project_files,
        )

        self.assertIn(
            "VERIFIED CHANGE IMPACT",
            prompt,
        )

        self.assertIn(
            "project/helper.py",
            prompt,
        )

        self.assertIn(
            "project/main.py",
            prompt,
        )


    def test_project_prompt_explains_change_impact_is_not_a_defect(self):
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
                "content": "value = 1",
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

        prompt = build_project_review_prompt(
            "project",
            project_files,
        )

        self.assertIn(
            "Verified change-impact relationships describe dependency risk, not defects.",
            prompt,
        )

        self.assertIn(
            '"project/helper.py"',
            prompt,
        )

        self.assertIn(
            '"project/main.py"',
            prompt,
        )


if __name__ == "__main__":
    unittest.main()