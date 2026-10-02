import unittest

from app.project_advice_validator import validate_test_advice


class TestProjectAdviceValidator(unittest.TestCase):
    def review(self, advice):
        return "5. Real problems\n\n- broken.py: Syntax error\n\n6. Optional improvements\n\n" + advice

    def test_removes_actual_scanner_advice_and_continuation(self):
        advice = ("- **Unit Tests for `scan_project`:**\n"
                  "  Although there are tests for ask_ai, there are no unit tests for scan_project.\n\n"
                  "  Adding tests for this function will ensure it works correctly.\n\n"
                  "- **Naming:**\n  Consider clearer names.")
        files = [{"path": r"tests\test_project_scanner.py"}]
        result = validate_test_advice(self.review(advice), files)
        self.assertNotIn("Unit Tests for", result)
        self.assertNotIn("Adding tests", result)
        self.assertIn("Consider clearer names.", result)
        self.assertIn("- broken.py: Syntax error", result)

    def test_no_discovered_tests_does_not_prove_function_untested(self):
        result = validate_test_advice(self.review("- scan_project is not tested."), [])
        self.assertNotIn("not tested", result)
        self.assertIn("No optional improvements recommended.", result)

    def test_recognizes_test_content_in_unconventional_filename(self):
        files = [{"path": "checks/checks.py", "language": "Python",
                  "content": "def test_scanner():\n    pass"}]
        result = validate_test_advice(self.review(
            "No test files were identified in the supplied project inventory."), files)
        self.assertNotIn("No test files were identified", result)

    def test_allows_only_scoped_inventory_observation_without_evidence(self):
        response = self.review("No test files were identified in the supplied project inventory.")
        self.assertEqual(validate_test_advice(response, [{"path": "app/main.py"}]), response)

    def test_removes_common_absence_phrasings(self):
        for claim in ("No tests exist.", "The module lacks tests.", "This is untested.",
                      "Tests are missing.", "There is no test coverage.",
                      "It does not have any unit tests.", "Unit tests do not exist.",
                      "There are NO\nunit tests for the scanner."):
            with self.subTest(claim=claim):
                result = validate_test_advice(self.review(claim), [])
                self.assertNotIn(claim, result)
                self.assertIn("No optional improvements recommended.", result)

    def test_preserves_positive_test_suggestion_without_absence_claim(self):
        response = self.review("- Consider an additional boundary-case test.")
        self.assertEqual(validate_test_advice(response, []), response)

    def test_preserves_verified_section_even_with_matching_words(self):
        response = "5. Real problems\n\n- no tests.py: Syntax error\n\n6. Optional improvements\n\n- No tests exist."
        result = validate_test_advice(response, [])
        self.assertEqual(result.split("6. Optional improvements")[0], response.split("6. Optional improvements")[0])

    def test_markdown_heading_and_numbered_advice(self):
        response = "## 6. Optional improvements\n\n1. **Tests:**\n   Missing unit tests.\n\n2. Consider clearer names."
        result = validate_test_advice(response, [])
        self.assertNotIn("Missing unit tests", result)
        self.assertIn("2. Consider clearer names.", result)

    def test_leaves_response_without_section_six_unchanged(self):
        response = "5. Real problems\n\nNo tests.py cannot be read."
        self.assertEqual(validate_test_advice(response, []), response)

    def test_preserves_following_section(self):
        response = self.review("- No tests exist.\n\n7. Notes\n\nKeep this.")
        result = validate_test_advice(response, [])
        self.assertIn("7. Notes\n\nKeep this.", result)
        self.assertNotIn("No tests exist.", result)


if __name__ == "__main__":
    unittest.main()
