import unittest
from copy import deepcopy

from app.dependency_claim_validator import validate_dependency_claims


class TestDependencyClaimValidator(unittest.TestCase):

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

    def test_accepts_verified_claims(self):
        claims = deepcopy(self.facts)
        before = deepcopy(self.facts)
        result = validate_dependency_claims(claims, self.facts)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(claims, before)
        self.assertEqual(self.facts, before)

    def test_rejects_incorrect_traversal_and_target(self):
        replacements = {
            "found": False,
            "target": "invented.py",
            "traversal_direction": "dependencies",
            "pending_initialization": "target",
            "direct_dependents": ["indirect.py"],
            "affected_files": ["target.py", "direct.py", "indirect.py"],
            "target_in_affected_files": True,
        }
        for field, value in replacements.items():
            with self.subTest(field=field):
                claims = dict(self.facts)
                claims[field] = value
                result = validate_dependency_claims(claims, self.facts)
                self.assertFalse(result["valid"])
                self.assertIn(
                    f"Claim differs from verified facts: {field}.",
                    result["errors"],
                )

    def test_rejects_incomplete_or_unexpected_records(self):
        for field in self.facts:
            with self.subTest(missing=field):
                incomplete = dict(self.facts)
                del incomplete[field]
                self.assertFalse(validate_dependency_claims(incomplete, self.facts)["valid"])
                self.assertFalse(validate_dependency_claims(self.facts, incomplete)["valid"])
        extra = dict(self.facts, explanation="Unsupported prose")
        self.assertFalse(validate_dependency_claims(extra, self.facts)["valid"])
        for value in (None, [], "not an object"):
            with self.subTest(value=value):
                self.assertFalse(validate_dependency_claims(value, self.facts)["valid"])
                self.assertFalse(validate_dependency_claims(self.facts, value)["valid"])

    def test_rejects_incorrect_types_including_integer_booleans(self):
        replacements = {
            "found": 1,
            "target": None,
            "traversal_direction": [],
            "pending_initialization": 1,
            "direct_dependents": "direct.py",
            "affected_files": [1],
            "target_in_affected_files": 0,
        }
        for field, value in replacements.items():
            with self.subTest(field=field):
                malformed = dict(self.facts)
                malformed[field] = value
                result = validate_dependency_claims(malformed, self.facts)
                self.assertFalse(result["valid"])
                self.assertIn(f"Invalid type for claim field: {field}.", result["errors"])
                # Matching malformed values must not validate each other.
                self.assertFalse(validate_dependency_claims(malformed, malformed)["valid"])


if __name__ == "__main__":
    unittest.main()
