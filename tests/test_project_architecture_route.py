from importlib.metadata import files
import unittest

from app.project_architecture_route import answer_verified_architecture_question


class TestProjectArchitectureRoute(unittest.TestCase):

    def test_architecture_word_inside_filename_does_not_trigger_route(
        self,
    ):
        files = self.files + [
            {
                "path": "app/module_role_facts.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
            {
                "path": "app/semantic_architecture_presenter.py",
                "language": "Python",
                "analysis": {
                    "imports": [
                        "app.module_role_facts",
                    ],
                    "functions": [],
                    "classes": [],
                    "methods": [],
                },
            },
        ]
        answer = answer_verified_architecture_question(
            (
               "Explain how app\\module_role_facts.py and "
               "app\\semantic_architecture_presenter.py interact "
                "when formatting known and unknown roles. "
                "Use only the actual implementations."
         ),
           files,
        )

        self.assertIsNone(answer)

    def setUp(self):
        self.files = [
            {"path": "app/main.py", "language": "Python", "analysis": {
                "imports": ["app.helper"], "functions": [{"name": "main"}],
                "classes": [], "methods": [],
            }},
            {"path": "app/helper.py", "language": "Python", "analysis": {
                "imports": [], "functions": [{"name": "help_user"}],
                "classes": [], "methods": [],
            }},
        ]

    def test_structural_architecture_question_is_answered(self):
        for question in (
            "Give me a structural overview of this project's architecture.",
            "Give me a verified structural overview of this project's architecture. "
            "Show the modules, discovered symbols, and static dependency relationships. "
            "Do not infer runtime execution order, module responsibilities, or data flow.",
        ):
            with self.subTest(question=question):
                answer = answer_verified_architecture_question(question, self.files)
                self.assertIsNotNone(answer)
                self.assertIn("Verified project architecture overview", answer)
                self.assertIn("app/main.py", answer)
                self.assertIn("Depends on: app/helper.py", answer)

    def test_runtime_flow_question_is_not_intercepted(self):
        for question in (
            "Explain the architecture and runtime data flow of this project.",
            "Explain the architecture and runtime data flow. "
            "Do not infer runtime execution order, module responsibilities, or data flow.",
            "What files are present?",
        ):
            with self.subTest(question=question):
                self.assertIsNone(answer_verified_architecture_question(question, self.files))

    def test_responsibility_question_is_not_intercepted(self):
        answer = answer_verified_architecture_question(
            "Describe the architecture and the responsibilities of every module.",
            self.files,
        )
        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()
