import unittest

from app.project_pipeline_presenter import format_verified_project_pipeline


class TestProjectPipelinePresenter(unittest.TestCase):

    def setUp(self):
        self.answer = format_verified_project_pipeline()

    def test_explains_scanner_analyzer_relationship(self):
        for expected in (
            "It first calls scan_project()",
            "read_code_file()",
            "analyze_code()",
            "skips symbolic-link entries, non-files",
            "detect_language()",
            "each file's path and language",
            "content and analysis",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.answer)

    def test_distinguishes_file_and_project_errors(self):
        self.assertIn("project-level error can", self.answer)
        self.assertIn("even when individual file-reading", self.answer)
        self.assertIn("(project_files, None)", self.answer)
        self.assertIn("(None, error)", self.answer)
        self.assertIn("continues to the next file", self.answer)
        self.assertIn("no analysis or content key", self.answer)
        self.assertIn("check for a per-file error before accessing its analysis", self.answer)

    def test_analysis_exceptions_propagate_without_error_record(self):
        self.assertIn("does not catch exceptions raised by analyze_code()", self.answer)
        self.assertIn("If analyze_code() raises an exception, it propagates", self.answer)
        self.assertIn("processing stops", self.answer)
        self.assertIn("not converted into a per-file error dictionary", self.answer)
        self.assertIn("No normal (project_files, None) result is returned", self.answer)
        self.assertIn("does not catch every possible filesystem exception", self.answer)


if __name__ == "__main__":
    unittest.main()
