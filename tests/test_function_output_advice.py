import unittest

from app.project_advice_validator import (
    filter_false_direct_print_advice,
)


class TestFunctionOutputAdvice(unittest.TestCase):

    def setUp(self):
        self.project_files = [
            {
                "path": "app/project_scanner.py",
                "language": "Python",
                "content": (
                    "def scan_project(path):\n"
                    "    files = [path]\n"
                    "    return files, None\n\n"
                    "if __name__ == '__main__':\n"
                    "    print(scan_project('.'))\n"
                ),
            }
        ]

        self.false_advice = (
            "6. Optional improvements\n\n"
            "- The `scan_project` function currently prints "
            "the results directly in the "
            "`if __name__ == \"__main__\":` block. "
            "Consider refactoring it to return results."
        )

    def test_removes_false_print_attribution(self):
        result = filter_false_direct_print_advice(
            self.false_advice,
            self.project_files,
        )

        self.assertNotIn(
            "currently prints",
            result,
        )

    def test_preserves_claim_when_function_prints(self):
        files = [
            {
                "path": "app/project_scanner.py",
                "language": "Python",
                "content": (
                    "def scan_project(path):\n"
                    "    print(path)\n"
                    "    return [path], None\n"
                ),
            }
        ]

        result = filter_false_direct_print_advice(
            self.false_advice,
            files,
        )

        self.assertIn(
            "currently prints",
            result,
        )

    def test_preserves_advice_when_source_unavailable(self):
        result = filter_false_direct_print_advice(
            self.false_advice,
            [],
        )

        self.assertIn(
            "currently prints",
            result,
        )

    def test_preserves_unrelated_advice(self):
        advice = (
            "6. Optional improvements\n\n"
            "- Consider documenting the public API."
        )

        result = filter_false_direct_print_advice(
            advice,
            self.project_files,
        )

        self.assertEqual(result, advice)


if __name__ == "__main__":
    unittest.main()
