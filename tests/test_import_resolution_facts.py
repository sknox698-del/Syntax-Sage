import unittest

from app.import_resolution_facts import build_import_resolution_facts


def python_file(path, imports=None):
    return {
        "path": path,
        "language": "Python",
        "analysis": {"imports": imports or []},
    }


class TestImportResolutionFacts(unittest.TestCase):

    def test_unique_local_self_and_external_imports(self):
        files = [
            python_file("app/main.py", ["app.helper", "main", "os"]),
            python_file("app/helper.py"),
        ]
        facts = build_import_resolution_facts("app/main.py", files)
        self.assertEqual(facts["import_results"], [
            {"import": "app.helper", "resolved_local_path": "app/helper.py"},
            {"import": "main", "resolved_local_path": None},
            {"import": "os", "resolved_local_path": None},
        ])
        self.assertEqual(facts["target"], "app/main.py")
        self.assertEqual(facts["resolution_kind"], "static_local_matching")
        self.assertEqual(facts["module_name_generation"], "dotted_path_suffixes")
        self.assertEqual(facts["prefix_order"], "longest_to_shortest")
        self.assertTrue(facts["excludes_self_matches"])
        self.assertIn("does not establish that it is external", facts["unresolved_meaning"])

    def test_unavailable_analysis_is_not_an_empty_import_list(self):
        cases = [
            [],
            [{"path": "app/main.py", "language": "JavaScript"}],
            [{"path": "app/main.py", "language": "Python"}],
            [{"path": "app/main.py", "language": "Python", "analysis": None}],
            [{"path": "app/main.py", "language": "Python", "analysis": {}}],
            [{"path": "app/main.py", "language": "Python", "analysis": {"imports": "os"}}],
        ]
        for files in cases:
            with self.subTest(files=files):
                self.assertIsNone(build_import_resolution_facts("app/main.py", files))
        facts = build_import_resolution_facts("app/main.py", [python_file("app/main.py")])
        self.assertEqual(facts["import_results"], [])

    def test_ambiguous_candidate_does_not_fall_back_to_shorter_prefix(self):
        files = [
            python_file("main.py", ["app.pkg.helper"]),
            python_file("one/app/pkg/helper.py"),
            python_file("two/app/pkg/helper.py"),
            python_file("app/pkg.py"),
        ]
        facts = build_import_resolution_facts("main.py", files)
        self.assertEqual(facts["import_results"], [
            {"import": "app.pkg.helper", "resolved_local_path": None},
        ])
        self.assertEqual(facts["ambiguity_policy"], "stop_without_shorter_prefix_fallback")
        # With the ambiguous candidates absent, the shorter match is viable.
        shorter = build_import_resolution_facts("main.py", [files[0], files[3]])
        self.assertEqual(shorter["import_results"], [
            {"import": "app.pkg.helper", "resolved_local_path": "app/pkg.py"},
        ])


if __name__ == "__main__":
    unittest.main()
