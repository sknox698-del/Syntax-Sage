import tempfile
import unittest
from pathlib import Path

from app.project_analyzer import analyze_project


class TestProjectAnalyzer(unittest.TestCase):

    def test_analyzes_project_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "main.py").write_text(
                'print("Hello")',
                encoding="utf-8",
            )

            (root / "database.sql").write_text(
                "SELECT * FROM users;",
                encoding="utf-8",
            )

            project_files, error = analyze_project(root)

            self.assertIsNone(error)
            self.assertEqual(len(project_files), 2)

            languages = {
                file_info["language"]
                for file_info in project_files
            }

            self.assertEqual(
                languages,
                {"Python", "SQL"},
            )

    def test_python_file_contains_analysis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "example.py").write_text(
                """def greet(name):
    return f"Hello, {name}!"
""",
                encoding="utf-8",
            )

            project_files, error = analyze_project(root)

            self.assertIsNone(error)
            self.assertEqual(len(project_files), 1)

            analysis = project_files[0]["analysis"]

            self.assertTrue(analysis["syntax_valid"])
            self.assertEqual(
                analysis["functions"][0]["name"],
                "greet",
            )

    def test_missing_project_returns_error(self):
        project_files, error = analyze_project(
            "folder_that_does_not_exist"
        )

        self.assertIsNone(project_files)
        self.assertEqual(
            error,
            "Project folder not found.",
        )


if __name__ == "__main__":
    unittest.main()