import unittest

from app.project_architecture_facts import build_project_architecture_facts


class TestProjectArchitectureFacts(unittest.TestCase):

    def test_records_verified_dependency_relationships(self):
        files = [
            {
                "path": "app/main.py",
                "language": "Python",
                "analysis": {
                    "imports": ["app.helper"],
                    "functions": [], "classes": [], "methods": [],
                },
            },
            {
                "path": "app/helper.py",
                "language": "Python",
                "analysis": {
                    "imports": [],
                    "functions": [], "classes": [], "methods": [],
                },
            },
        ]
        facts = build_project_architecture_facts(files)
        modules = {item["path"]: item for item in facts["modules"]}
        self.assertEqual(modules["app/main.py"]["depends_on"], ["app/helper.py"])
        self.assertEqual(modules["app/helper.py"]["used_by"], ["app/main.py"])
        self.assertEqual(facts["local_dependency_count"], 1)
        self.assertEqual(facts["file_count"], 2)
        self.assertEqual(list(modules), ["app/helper.py", "app/main.py"])

    def test_preserves_file_error_without_inventing_analysis(self):
        files = [{
            "path": "app/broken.py",
            "language": "Python",
            "error": "Read failed.",
        }]
        facts = build_project_architecture_facts(files)
        module = facts["modules"][0]
        self.assertEqual(module["file_error"], "Read failed.")
        self.assertEqual(module["functions"], [])
        self.assertEqual(module["classes"], [])
        self.assertEqual(module["methods"], [])

    def test_normalizes_analyzer_symbol_records(self):
        files = [{
            "path": "app/example.py",
            "language": "Python",
            "analysis": {
                "imports": [],
                "functions": [{"name": "run"}, {"name": "load"}],
                "classes": [{"name": "Example"}],
                "methods": [{"name": "start"}],
            },
        }]
        facts = build_project_architecture_facts(files)
        module = facts["modules"][0]
        self.assertEqual(module["functions"], ["load", "run"])
        self.assertEqual(module["classes"], ["Example"])
        self.assertEqual(module["methods"], ["start"])


if __name__ == "__main__":
    unittest.main()
