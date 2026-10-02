import unittest

from app.dependency_explanation_route import (
    answer_verified_dependency_question,
    answer_verified_combined_dependency_question,
)


class TestDependencyExplanationRoute(unittest.TestCase):

    def setUp(self):
        self.files = [
            {"path": "project/helper.py", "language": "Python", "analysis": {"imports": []}},
            {"path": "project/main.py", "language": "Python", "analysis": {"imports": ["helper"]}},
        ]

    def test_focused_question_receives_verified_explanation(self):
        answer = answer_verified_dependency_question(
            "Explain get_change_impact() for helper.py", self.files,
        )
        self.assertIsNotNone(answer)
        self.assertIn("pending list starts with direct dependents", answer)
        self.assertIn("The target itself is excluded from affected_files.", answer)
        self.assertIn("- affected_files: ['project/main.py']", answer)
        self.assertIn("could affect", answer)

    def test_combined_import_question_is_not_intercepted(self):
        answer = answer_verified_dependency_question(
            "Explain how helper.py resolves imports and traces affected files. "
            "Describe exactly what get_change_impact() returns.",
            self.files,
        )
        self.assertIsNone(answer)

    def test_requires_a_uniquely_identified_file(self):
        ambiguous = self.files + [
            {"path": "tests/helper.py", "language": "Python", "analysis": {"imports": []}},
        ]
        cases = (
            ("Explain dependency traversal", self.files),
            ("Explain get_change_impact() for missing.py", self.files),
            ("Explain get_change_impact() for helper.py", ambiguous),
            ("Explain affected files for helper.py and main.py", self.files),
        )
        for question, files in cases:
            with self.subTest(question=question):
                self.assertIsNone(answer_verified_dependency_question(question, files))


    def _combined_files(self):
        return [
            {"path": "app/dependency_analyzer.py", "language": "Python",
             "analysis": {"imports": ["UNRELATED_IMPORT_MARKER"]}},
            {"path": "app/main.py", "language": "Python",
             "analysis": {"imports": ["app.dependency_analyzer"]}},
        ]

    def test_combined_route_explains_algorithm_without_own_imports(self):
        answer = answer_verified_combined_dependency_question(
            "Explain how dependency_analyzer.py resolves imports and traces affected files. "
            "Describe exactly what get_change_impact() returns.", self._combined_files(),
        )
        self.assertIsNotNone(answer)
        self.assertIn("longest to shortest", answer)
        self.assertIn("not full runtime import resolution", answer)
        self.assertNotIn("Analyzed imports for:", answer)
        self.assertNotIn("UNRELATED_IMPORT_MARKER", answer)
        self.assertNotIn("No imports recorded", answer)
        self.assertIn("pending list starts with direct dependents", answer)
        self.assertIn("excluded from affected_files", answer)
        self.assertIn("- affected_files: ['app/main.py']", answer)
        self.assertIn("could affect", answer)

    def test_combined_route_includes_missing_target_contract(self):
        answer = answer_verified_combined_dependency_question(
            "Describe dependency_analyzer.py import resolution and get_change_impact", self._combined_files(),
        )
        self.assertIn(
            "If a requested target is absent from the analyzed dependency map, "
            "get_change_impact() returns:\n"
            "- found: False\n"
            "- target: the original requested path\n"
            "- affected_files: []", answer,
        )

    def test_combined_route_rejects_unrelated_ambiguous_or_unavailable(self):
        files = self._combined_files()
        question = "Explain dependency_analyzer.py import resolution and affected files"
        cases = [
            ("Explain dependency_analyzer.py", files),
            ("Explain import resolution and affected files", files),
            ("Explain main.py import resolution and affected files", files),
            (question, files + [{"path": "other/dependency_analyzer.py", "language": "Python", "analysis": {"imports": []}}]),
            (question, [{"path": "app/dependency_analyzer.py", "language": "Python"}]),
        ]
        for query, project in cases:
            with self.subTest(query=query, project=project):
                self.assertIsNone(answer_verified_combined_dependency_question(query, project))


if __name__ == "__main__":
    unittest.main()
