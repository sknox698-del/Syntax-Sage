import unittest
from unittest.mock import call, patch

from app.project_analyzer import analyze_project


class TestProjectAnalyzerErrorContract(unittest.TestCase):

    @patch("app.project_analyzer.scan_project")
    def test_scanner_error_is_returned(self, mock_scan):
        mock_scan.return_value = (
            None,
            "Project folder not found.",
        )

        result = analyze_project("missing")

        self.assertEqual(
            result,
            (None, "Project folder not found."),
        )
        mock_scan.assert_called_once_with("missing")

    @patch("app.project_analyzer.analyze_code")
    @patch("app.project_analyzer.read_code_file")
    @patch("app.project_analyzer.scan_project")
    def test_read_error_does_not_set_project_error(
        self,
        mock_scan,
        mock_read,
        mock_analyze,
    ):
        mock_scan.return_value = (
            [
                {"path": "app/good.py", "language": "Python"},
                {"path": "app/unreadable.py", "language": "Python"},
                {"path": "app/after.py", "language": "Python"},
            ],
            None,
        )
        mock_read.side_effect = [
            ("value = 1", None),
            (None, "Permission denied."),
            ("value = 2", None),
        ]
        first_analysis = {"syntax_valid": True, "code_lines": 1}
        last_analysis = {"syntax_valid": True, "code_lines": 1}
        mock_analyze.side_effect = [first_analysis, last_analysis]

        project_files, project_error = analyze_project("app")

        self.assertIsNone(project_error)
        self.assertEqual(project_files, [
            {
                "path": "app/good.py",
                "language": "Python",
                "analysis": first_analysis,
                "content": "value = 1",
            },
            {
                "path": "app/unreadable.py",
                "language": "Python",
                "error": "Permission denied.",
            },
            {
                "path": "app/after.py",
                "language": "Python",
                "analysis": last_analysis,
                "content": "value = 2",
            },
        ])
        self.assertNotIn("analysis", project_files[1])
        self.assertNotIn("content", project_files[1])
        self.assertEqual(mock_read.call_args_list, [
            call("app/good.py"),
            call("app/unreadable.py"),
            call("app/after.py"),
        ])
        self.assertEqual(mock_analyze.call_args_list, [
            call("value = 1", "Python"),
            call("value = 2", "Python"),
        ])

    @patch("app.project_analyzer.analyze_code")
    @patch("app.project_analyzer.read_code_file")
    @patch("app.project_analyzer.scan_project")
    def test_analysis_exception_propagates(
        self,
        mock_scan,
        mock_read,
        mock_analyze,
    ):
        mock_scan.return_value = (
            [
                {"path": "app/failing.py", "language": "Python"},
                {"path": "app/after.py", "language": "Python"},
            ],
            None,
        )
        mock_read.return_value = ("value = 1", None)
        failure = RuntimeError("Analysis failed unexpectedly.")
        mock_analyze.side_effect = failure

        with self.assertRaises(RuntimeError) as raised:
            analyze_project("app")

        self.assertIs(raised.exception, failure)
        mock_read.assert_called_once_with("app/failing.py")
        mock_analyze.assert_called_once_with("value = 1", "Python")


if __name__ == "__main__":
    unittest.main()
