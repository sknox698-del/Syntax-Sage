import unittest

from app.import_resolution_facts import build_import_resolution_facts
from app.import_resolution_presenter import format_verified_import_facts


class TestImportResolutionPresenter(unittest.TestCase):

    def test_resolved_import_and_policy_are_presented(self):
        files = [
            {
                "path": "app/main.py",
                "language": "Python",
                "analysis": {"imports": ["app.helper"]},
            },
            {
                "path": "app/helper.py",
                "language": "Python",
                "analysis": {"imports": []},
            },
        ]
        facts = build_import_resolution_facts("app/main.py", files)
        answer = format_verified_import_facts(facts)
        self.assertIn("app.helper: app/helper.py", answer)
        self.assertIn("longest to shortest", answer)
        self.assertIn("not full runtime import resolution", answer)
        self.assertIn("without guessing or falling back to a shorter prefix", answer)
        self.assertIn("excludes the importing file itself", answer)
        # Policy drift must not silently receive the old explanation.
        for field in (
            "resolution_kind", "module_name_generation", "prefix_order",
            "excludes_self_matches", "ambiguity_policy",
        ):
            with self.subTest(field=field):
                unsupported = dict(facts)
                unsupported[field] = None
                self.assertEqual(
                    format_verified_import_facts(unsupported),
                    "The import-resolution policy could not be verified.",
                )

    def test_unresolved_import_is_not_called_external(self):
        files = [{
            "path": "app/main.py",
            "language": "Python",
            "analysis": {"imports": ["unknown_module"]},
        }]
        facts = build_import_resolution_facts("app/main.py", files)
        answer = format_verified_import_facts(facts)
        self.assertIn("unknown_module: No unique local match", answer)
        self.assertIn("not automatically classified as external", answer)
        self.assertIn("do not identify which reason applies", answer)

    def test_unavailable_analysis_is_reported(self):
        answer = format_verified_import_facts(None)
        self.assertIn("evidence is unavailable", answer)
        self.assertNotIn("No imports recorded", answer)
        files = [{"path": "app/main.py", "language": "Python", "analysis": {"imports": []}}]
        available = format_verified_import_facts(build_import_resolution_facts("app/main.py", files))
        self.assertIn("No imports recorded", available)
        self.assertNotIn("evidence is unavailable", available)


if __name__ == "__main__":
    unittest.main()
