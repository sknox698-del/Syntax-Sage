import unittest

from app.semantic_architecture_route import (
    answer_verified_semantic_architecture_question,
)


class TestSemanticArchitectureRoute(unittest.TestCase):

    def setUp(self):
        self.files = [
            {
                "path": "app/language_router.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "app/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["app.language_router"],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]

    def test_module_responsibility_question_is_answered(self):
        answer = (
            answer_verified_semantic_architecture_question(
                "What does each module do?",
                self.files,
            )
        )

        self.assertIsNotNone(answer)

        self.assertIn(
            "Verified semantic architecture overview",
            answer,
        )

        self.assertIn(
            "Module: app/language_router.py",
            answer,
        )

        self.assertIn(
            "Verified responsibility:",
            answer,
        )

    def test_runtime_flow_question_is_not_intercepted(self):
        answer = (
            answer_verified_semantic_architecture_question(
                (
                    "Explain the module responsibilities "
                    "and runtime flow."
                ),
                self.files,
            )
        )

        self.assertIsNone(answer)

    def test_unrelated_question_is_not_intercepted(self):
        answer = (
            answer_verified_semantic_architecture_question(
                "What problems are in this project?",
                self.files,
            )
        )

        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()