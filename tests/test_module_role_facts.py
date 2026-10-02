import unittest

from app.module_role_facts import (
    get_verified_module_role,
)


class TestModuleRoleFacts(unittest.TestCase):

    def test_windows_and_unix_paths_match_same_module(self):
        unix_result = get_verified_module_role(
            "app/language_router.py"
        )

        windows_result = get_verified_module_role(
            r"app\language_router.py"
        )

        self.assertEqual(
            unix_result,
            windows_result,
        )

        self.assertIsNotNone(
            unix_result,
        )

    def test_known_module_returns_verified_role(self):
        result = get_verified_module_role(
            "app/language_router.py"
        )

        self.assertEqual(
            result,
            (
                "Identifies supported programming languages "
                "from filename extensions using a fixed "
                "extension map."
            ),
        )

    def test_unknown_module_returns_none(self):
        result = get_verified_module_role(
            "app/does_not_exist.py"
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()