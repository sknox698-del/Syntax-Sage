import unittest

from app.dependency_analyzer import (
    find_affected_files,
    get_change_impact,
)


class TestDependencyExplanationContract(unittest.TestCase):

    def test_traverses_dependents_not_dependencies(self):
        # dependency.py is used by target.py.
        # direct.py depends on target.py.
        # indirect.py depends on direct.py.
        reverse_map = {
            "dependency.py": ["target.py"],
            "target.py": ["direct.py"],
            "direct.py": ["indirect.py"],
            "indirect.py": [],
        }

        affected = find_affected_files(
            "target.py",
            reverse_map,
        )

        self.assertEqual(
            affected,
            ["direct.py", "indirect.py"],
        )
        self.assertNotIn("target.py", affected)
        self.assertNotIn("dependency.py", affected)

    def test_missing_target_has_exact_return_values(self):
        project_files = [
            {
                "path": "project/main.py",
                "language": "Python",
                "analysis": {"imports": []},
            },
        ]
        requested_path = "project/missing.py"

        result = get_change_impact(
            requested_path,
            project_files,
        )

        self.assertEqual(
            result,
            {
                "found": False,
                "target": requested_path,
                "affected_files": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
