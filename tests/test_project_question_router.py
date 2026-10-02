import unittest

from app.project_question_router import (
    answer_project_question_deterministically,
    build_verified_change_impact_answer,
    build_verified_problem_answer,
    classify_project_question,
)


class TestProjectQuestionRouter(unittest.TestCase):

    def setUp(self):
        self.project_files = [
            {
                "path": "projects\\dependency_project\\helper.py",
                "language": "Python",
                "content": (
                    "def greet(name):\n"
                    "    return f'Hello, {name}'"
                ),
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
            {
                "path": "projects\\dependency_project\\main.py",
                "language": "Python",
                "content": (
                    "import helper\n\n"
                    "message = helper.greet('Steve')\n"
                    "print(message)"
                ),
                "analysis": {
                    "total_lines": 4,
                    "code_lines": 3,
                    "blank_lines": 1,
                    "syntax_valid": True,
                    "imports": ["helper"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

    def test_classifies_change_impact_question(self):
        result = classify_project_question(
            "What could be affected if I change helper.py?"
        )

        self.assertEqual(
            result,
            "change_impact",
        )

    def test_classifies_problem_question(self):
        result = classify_project_question(
            "Is anything broken in this project?"
        )

        self.assertEqual(
            result,
            "problems",
        )

    def test_classifies_general_question(self):
        result = classify_project_question(
            "What does helper.py do?"
        )

        self.assertEqual(
            result,
            "general",
        )

    def test_builds_verified_change_impact_answer(self):
        result = build_verified_change_impact_answer(
            "What could be affected if I change helper.py?",
            self.project_files,
        )

        self.assertIsNotNone(result)

        self.assertIn(
            "Changing helper.py could affect:",
            result,
        )

        self.assertIn(
            "projects\\dependency_project\\main.py",
            result,
        )

        self.assertNotIn(
            "will affect",
            result.lower(),
        )

    def test_change_impact_answer_returns_none_for_unknown_file(self):
        result = build_verified_change_impact_answer(
            "What could be affected if I change missing.py?",
            self.project_files,
        )

        self.assertIsNone(result)

    def test_problem_answer_reports_no_confirmed_problems(self):
        result = build_verified_problem_answer(
            self.project_files
        )

        self.assertEqual(
            result,
            "No confirmed real problems found.",
        )

    def test_router_answers_change_impact_deterministically(self):
        result = answer_project_question_deterministically(
            "What does helper.py do, and what could be affected if I change it?",
            self.project_files,
        )

        self.assertIsNotNone(result)

        self.assertIn(
            "Changing helper.py could affect:",
            result,
        )

        self.assertIn(
            "projects\\dependency_project\\main.py",
            result,
        )

    def test_router_answers_problem_question_deterministically(self):
        result = answer_project_question_deterministically(
            "Is anything broken in this project?",
            self.project_files,
        )

        self.assertEqual(
            result,
            "No confirmed real problems found.",
        )

    def test_router_returns_none_for_general_question(self):
        result = answer_project_question_deterministically(
            "What does helper.py do?",
            self.project_files,
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
