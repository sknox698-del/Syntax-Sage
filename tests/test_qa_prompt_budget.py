import unittest

from app.qa_prompt_budget import (
    MAX_GENERAL_REQUEST_CHARACTERS,
    general_request_too_large,
)


class TestQAPromptBudget(unittest.TestCase):

    def test_accepts_request_at_limit(self):
        system = "S" * 1000
        prompt = "P" * (MAX_GENERAL_REQUEST_CHARACTERS - len(system))
        self.assertFalse(general_request_too_large(prompt, system))

    def test_rejects_request_over_limit(self):
        system = "S" * 1000
        prompt = "P" * (MAX_GENERAL_REQUEST_CHARACTERS - len(system) + 1)
        self.assertTrue(general_request_too_large(prompt, system))


if __name__ == "__main__":
    unittest.main()
