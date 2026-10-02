import unittest

from app.single_file_review_guard import (
    enforce_verified_single_file_review,
)


class TestSingleFileReviewGuard(unittest.TestCase):

    def test_removes_unverified_problem_claims(self):
        ai_response = """
1. What the code does:
Detects programming languages from file extensions.
2. Real problems:
- Extensionless filenames cause AttributeError.
- Mixed-case extensions are not handled.
3. Optional improvements:
- Add exception handling.
"""
        analysis = {"syntax_valid": True, "syntax_error": None}
        result = enforce_verified_single_file_review(ai_response, analysis)
        self.assertIn(
            "Detects programming languages from file extensions.", result,
        )
        self.assertIn("2. Verified problems", result)
        self.assertIn("No verified problems found by static analysis.", result)
        self.assertNotIn("AttributeError", result)
        self.assertNotIn("Mixed-case extensions are not handled", result)
        self.assertNotIn("Optional improvements", result)
        self.assertNotIn("Add exception handling", result)

    def test_preserves_verified_syntax_error_over_ai_claim(self):
        ai_response = """
1. What the code does:
Defines a function.
2. Real problems:
No real problems found.
3. Optional improvements:
- Add a docstring.
"""
        analysis = {
            "syntax_valid": False,
            "syntax_error": "Line 1: expected ':'",
        }
        result = enforce_verified_single_file_review(ai_response, analysis)
        self.assertIn("Defines a function.", result)
        self.assertIn("Syntax error: Line 1: expected ':'", result)
        self.assertNotIn("No real problems found.", result)
        self.assertNotIn("No verified problems found", result)
        self.assertNotIn("Add a docstring", result)

    def test_missing_explanation_does_not_hide_verified_error(self):
        analysis = {
            "syntax_valid": False,
            "syntax_error": "Line 2: invalid syntax",
        }
        result = enforce_verified_single_file_review(
            "Unexpected AI output claiming everything is fine.", analysis,
        )
        self.assertIn("No AI explanation available.", result)
        self.assertIn("Syntax error: Line 2: invalid syntax", result)
        self.assertNotIn("everything is fine", result)


if __name__ == "__main__":
    unittest.main()
