import unittest

from app.project_pipeline_presenter import format_verified_project_pipeline
from app.project_pipeline_route import answer_verified_project_pipeline_question


class TestProjectPipelineRoute(unittest.TestCase):

    def test_original_question_returns_verified_explanation(self):
        question = (
            "Explain how project_scanner.py and project_analyzer.py work together. "
            "Do not perform a code review."
        )
        files = [
            {"path": "app\\project_scanner.py"},
            {"path": "app\\project_analyzer.py"},
        ]
        self.assertEqual(
            answer_verified_project_pipeline_question(question, files),
            format_verified_project_pipeline(),
        )

    def test_one_module_returns_none(self):
        files = [
            {"path": "app/project_scanner.py"},
            {"path": "app/project_analyzer.py"},
        ]
        self.assertIsNone(answer_verified_project_pipeline_question(
            "Explain how project_scanner.py and its callers work together.", files,
        ))

    def test_similarly_named_files_outside_app_return_none(self):
        files = [
            {"path": "other/project_scanner.py"},
            {"path": "other/project_analyzer.py"},
        ]
        self.assertIsNone(answer_verified_project_pipeline_question(
            "Explain how project_scanner.py and project_analyzer.py work together. "
            "Do not perform a code review.", files,
        ))


if __name__ == "__main__":
    unittest.main()
