import unittest
from unittest.mock import patch

from app.dependency_claim_validator import (
    REQUIRED_FIELDS,
    validate_dependency_claims,
)
from app.dependency_explanation_facts import (
    build_dependency_explanation_facts,
)


class TestDependencyExplanationFacts(unittest.TestCase):

    @patch("app.dependency_explanation_facts.get_change_impact")
    @patch("app.dependency_explanation_facts.build_reverse_dependency_map")
    @patch("app.dependency_explanation_facts.build_dependency_map")
    def test_existing_target(
        self,
        mock_dependency_map,
        mock_reverse_map,
        mock_impact,
    ):
        project_files = [{"path": "target.py", "language": "Python"}]
        mock_dependency_map.return_value = {}
        mock_reverse_map.return_value = {
            "target.py": ["direct.py"],
            "direct.py": ["indirect.py"],
            "indirect.py": [],
        }
        mock_impact.return_value = {
            "found": True,
            "target": "target.py",
            "affected_files": ["direct.py", "indirect.py"],
        }

        facts = build_dependency_explanation_facts("target.py", project_files)

        self.assertEqual(facts, {
            "found": True,
            "target": "target.py",
            "direct_dependents": ["direct.py"],
            "affected_files": ["direct.py", "indirect.py"],
            "target_in_affected_files": False,
            "traversal_direction": "dependents",
            "pending_initialization": "direct_dependents",
        })
        mock_dependency_map.assert_called_once_with(project_files)
        mock_reverse_map.assert_called_once_with(mock_dependency_map.return_value)
        mock_impact.assert_called_once_with("target.py", project_files)
        self.assertIsNot(facts["affected_files"], mock_impact.return_value["affected_files"])

    @patch("app.dependency_explanation_facts.get_change_impact")
    @patch("app.dependency_explanation_facts.build_reverse_dependency_map")
    @patch("app.dependency_explanation_facts.build_dependency_map")
    def test_missing_target(
        self,
        mock_dependency_map,
        mock_reverse_map,
        mock_impact,
    ):
        project_files = [{"path": "existing.py", "language": "Python"}]
        mock_dependency_map.return_value = {"existing.py": []}
        mock_reverse_map.return_value = {"existing.py": []}
        mock_impact.return_value = {
            "found": False,
            "target": "project/missing.py",
            "affected_files": [],
        }

        facts = build_dependency_explanation_facts("project/missing.py", project_files)

        self.assertEqual(facts, {
            "found": False,
            "target": "project/missing.py",
            "direct_dependents": [],
            "affected_files": [],
            "target_in_affected_files": False,
            "traversal_direction": "dependents",
            "pending_initialization": "direct_dependents",
        })
        mock_dependency_map.assert_called_once_with(project_files)
        mock_reverse_map.assert_called_once_with(mock_dependency_map.return_value)
        mock_impact.assert_called_once_with("project/missing.py", project_files)


    def test_fact_record_matches_validator_contract(self):
        facts = build_dependency_explanation_facts(
            "missing.py",
            [],
        )
        self.assertEqual(
            set(facts),
            REQUIRED_FIELDS,
        )
        result = validate_dependency_claims(
            dict(facts),
            facts,
        )
        self.assertTrue(
            result["valid"],
            result["errors"],
        )


if __name__ == "__main__":
    unittest.main()
