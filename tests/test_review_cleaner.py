import unittest

from app.review_cleaner import clean_optional_improvements


class TestReviewCleaner(unittest.TestCase):

    def test_removes_duplicate_required_fix(self):
        text = """
2. Real problems

- Syntax error: missing colon.

3. Optional improvements

- Add a colon at the end.
"""

        cleaned = clean_optional_improvements(
            text,
            force_no_optional=True,
        )

        self.assertNotIn(
            "Add a colon",
            cleaned,
        )

    def test_removes_unnecessary_docstring_suggestion(self):
        text = """
3. Optional improvements

- Consider adding a docstring.
"""

        cleaned = clean_optional_improvements(
            text,
            force_no_optional=True,
        )

        self.assertNotIn(
            "docstring",
            cleaned,
        )

    def test_force_no_optional_removes_all_extra_advice(self):
        text = """
1. What the code does
Example.

2. Real problems
- Syntax error.

3. Optional improvements
- Add type hints.

Example fix:
def greet(name):
    pass
"""

        cleaned = clean_optional_improvements(
            text,
            force_no_optional=True,
        )

        self.assertIn(
            "No optional improvements recommended.",
            cleaned,
        )

        self.assertNotIn(
            "Add type hints",
            cleaned,
        )

        self.assertNotIn(
            "Example fix",
            cleaned,
        )


if __name__ == "__main__":
    unittest.main()