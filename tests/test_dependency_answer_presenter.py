import unittest
from copy import deepcopy

from app.dependency_answer_presenter import validate_and_present_dependency_claims


class TestDependencyAnswerPresenter(unittest.TestCase):

    def setUp(self):
        self.facts = {
            "found": True,
            "target": "target.py",
            "traversal_direction": "dependents",
            "pending_initialization": "direct_dependents",
            "direct_dependents": ["direct.py"],
            "affected_files": ["direct.py", "indirect.py"],
            "target_in_affected_files": False,
        }

    def test_accepts_correct_structured_claims(self):
        before = deepcopy(self.facts)
        result = validate_and_present_dependency_claims(dict(self.facts), self.facts)
        self.assertTrue(result["claims_valid"])
        self.assertEqual(result["errors"], [])
        for expected in (
            "pending list starts with direct dependents",
            "Traversal follows dependents, not dependencies",
            "Further dependents are then visited",
            "The target itself is excluded from affected_files.",
            "could affect",
            "may require review",
            "- found: True",
            "- target: target.py",
            "- affected_files: ['direct.py', 'indirect.py']",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, result["answer"])
        self.assertEqual(self.facts, before)

    def test_rejects_claims_and_displays_only_verified_facts(self):
        claims = dict(self.facts)
        claims.update({
            "traversal_direction": "dependencies",
            "pending_initialization": "target",
            "affected_files": ["invented.py", "target.py"],
            "target_in_affected_files": True,
            "explanation": "UNVERIFIED_PROSE_MARKER",
        })
        result = validate_and_present_dependency_claims(claims, self.facts)
        accepted = validate_and_present_dependency_claims(dict(self.facts), self.facts)
        self.assertFalse(result["claims_valid"])
        self.assertTrue(result["errors"])
        self.assertIn("Showing verified facts instead.", result["answer"])
        self.assertTrue(result["answer"].endswith(accepted["answer"]))
        self.assertNotIn("invented.py", result["answer"])
        self.assertNotIn("UNVERIFIED_PROSE_MARKER", result["answer"])
        self.assertIn("excluded from affected_files", result["answer"])

    def test_missing_target_displays_exact_return_values(self):
        facts = dict(self.facts, found=False, target="missing.py",
                     direct_dependents=[], affected_files=[])
        result = validate_and_present_dependency_claims(dict(facts), facts)
        self.assertTrue(result["claims_valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["answer"], (
            "Target: missing.py\n"
            "The target was not found in the analyzed dependency map.\n"
            "get_change_impact() returns:\n"
            "- found: False\n"
            "- target: missing.py\n"
            "- affected_files: []"
        ))


if __name__ == "__main__":
    unittest.main()
