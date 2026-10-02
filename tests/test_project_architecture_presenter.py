import unittest

from app.project_architecture_presenter import (
    format_verified_project_architecture,
)


class TestProjectArchitecturePresenter(unittest.TestCase):

    def setUp(self):
        self.facts = {
            "file_count": 2,
            "local_dependency_count": 1,
            "modules": [
                {
                    "path": "app/main.py",
                    "language": "Python",
                    "functions": ["main"],
                    "classes": [],
                    "methods": [],
                    "depends_on": ["app/helper.py"],
                    "used_by": [],
                    "file_error": None,
                },
                {
                    "path": "app/helper.py",
                    "language": "Python",
                    "functions": ["help_user"],
                    "classes": [],
                    "methods": [],
                    "depends_on": [],
                    "used_by": ["app/main.py"],
                    "file_error": None,
                },
            ],
        }

    def test_presents_verified_structure(self):
        answer = format_verified_project_architecture(self.facts)
        self.assertIn("Analyzed files: 2", answer)
        self.assertIn("Verified local dependency relationships: 1", answer)
        self.assertIn("Module: app/main.py", answer)
        self.assertIn("Functions: main", answer)
        self.assertIn("Depends on: app/helper.py", answer)
        self.assertIn("Used by: app/main.py", answer)
        self.assertIn("Classes: None identified", answer)
        self.assertNotIn("File error:", answer)

    def test_explicitly_limits_runtime_inference(self):
        answer = format_verified_project_architecture(self.facts)
        self.assertIn("do not by themselves prove runtime", answer)
        self.assertIn("does not infer", answer)

    def test_preserves_file_error(self):
        facts = {
            **self.facts,
            "modules": [
                {
                    **self.facts["modules"][0],
                    "file_error": "Read failed.",
                }
            ],
            "file_count": 1,
        }
        answer = format_verified_project_architecture(facts)
        self.assertIn("File error: Read failed.", answer)


if __name__ == "__main__":
    unittest.main()
