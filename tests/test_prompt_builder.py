import unittest

from app.prompt_builder import build_code_review_prompt


class TestPromptBuilder(unittest.TestCase):

    def test_prompt_contains_file_information(self):
        analysis = {
            "total_lines": 3,
            "functions": [],
        }

        prompt = build_code_review_prompt(
            filepath="projects/example.py",
            language="Python",
            analysis=analysis,
            content='print("Hello")',
        )

        self.assertIn("projects/example.py", prompt)
        self.assertIn("Python", prompt)
        self.assertIn('print("Hello")', prompt)

    def test_prompt_contains_analysis_results(self):
        analysis = {
            "syntax_valid": True,
            "functions": [
                {
                    "name": "greet",
                    "line": 1,
                    "parameters": ["name"],
                }
            ],
        }

        prompt = build_code_review_prompt(
            filepath="example.py",
            language="Python",
            analysis=analysis,
            content="def greet(name): pass",
        )

        self.assertIn("greet", prompt)
        self.assertIn("syntax_valid", prompt)

    def test_prompt_contains_review_rules(self):
        prompt = build_code_review_prompt(
            filepath="example.py",
            language="Python",
            analysis={},
            content="pass",
        )

        self.assertIn("No real problems found.", prompt)
        self.assertIn("Do not rewrite", prompt)
        self.assertIn("Optional improvements", prompt)


if __name__ == "__main__":
    unittest.main()