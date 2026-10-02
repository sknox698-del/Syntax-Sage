import unittest

from app.project_answer_cleaner import (
    clean_project_question_answer,
    question_requests_code,
    question_requests_improvements,
)


class TestProjectAnswerCleaner(unittest.TestCase):

    def test_removes_unsolicited_improvement_section(self):
        answer = """
helper.py defines greet(name) and returns a greeting string.

Optional improvements:
- Add a docstring.
- Add type hints.
"""

        result = clean_project_question_answer(
            answer,
            "What does helper.py do?",
        )

        self.assertIn(
            "helper.py defines greet(name)",
            result,
        )

        self.assertNotIn(
            "Optional improvements",
            result,
        )

        self.assertNotIn(
            "Add a docstring",
            result,
        )

        self.assertNotIn(
            "Add type hints",
            result,
        )

    def test_removes_unsolicited_code_block(self):
        answer = """
helper.py defines a greeting function.
```python
def greet(name):
    return f"Hello, {name}"
```
"""

        result = clean_project_question_answer(
            answer,
            "What does helper.py do?",
        )

        self.assertIn(
            "helper.py defines a greeting function.",
            result,
        )

        self.assertNotIn(
            "def greet",
            result,
        )

        self.assertNotIn(
            "```",
            result,
        )

    def test_preserves_code_when_user_requests_code(self):
        answer = """
Here is the code:
```python
def greet(name):
    return f"Hello, {name}"
```
"""

        question = (
            "Show me code for the greet function."
        )

        result = clean_project_question_answer(
            answer,
            question,
        )

        self.assertTrue(
            question_requests_code(question)
        )

        self.assertIn(
            "def greet",
            result,
        )

        self.assertIn(
            "```python",
            result,
        )

    def test_preserves_improvements_when_user_requests_them(self):
        answer = """
Optional improvements:

- Add a docstring.
- Add type hints.
"""

        question = (
            "What improvements would you suggest?"
        )

        result = clean_project_question_answer(
            answer,
            question,
        )

        self.assertTrue(
            question_requests_improvements(question)
        )

        self.assertIn(
            "Optional improvements",
            result,
        )

        self.assertIn(
            "Add a docstring",
            result,
        )


if __name__ == "__main__":
    unittest.main()
