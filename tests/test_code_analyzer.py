import unittest

from app.code_analyzer import analyze_code


class TestCodeAnalyzer(unittest.TestCase):

    def test_counts_lines_correctly(self):
        code = """def greet(name):
    return f"Hello, {name}!"


print(greet("Steve"))"""

        result = analyze_code(code)

        self.assertEqual(result["total_lines"], 5)
        self.assertEqual(result["blank_lines"], 2)
        self.assertEqual(result["code_lines"], 3)

    def test_empty_file(self):
        result = analyze_code("")

        self.assertEqual(result["total_lines"], 0)
        self.assertEqual(result["blank_lines"], 0)
        self.assertEqual(result["code_lines"], 0)

    def test_file_with_only_code(self):
        code = """print("Hello")
print("World")"""

        result = analyze_code(code)

        self.assertEqual(result["total_lines"], 2)
        self.assertEqual(result["blank_lines"], 0)
        self.assertEqual(result["code_lines"], 2)

    def test_python_function_detection(self):
        code = """def greet(name):
    return f"Hello, {name}!"
"""

        result = analyze_code(code, "Python")

        self.assertTrue(result["syntax_valid"])

        self.assertEqual(
            result["functions"],
            [
                {
                    "name": "greet",
                    "line": 1,
                    "parameters": ["name"],
                }
            ],
        )

        self.assertEqual(result["classes"], [])
        self.assertEqual(result["imports"], [])

    def test_python_class_and_import_detection(self):
        code = """import os
from pathlib import Path

class FileManager:
    pass
"""

        result = analyze_code(code, "Python")

        self.assertTrue(result["syntax_valid"])

        self.assertEqual(
            result["classes"],
            [
                {
                    "name": "FileManager",
                    "line": 4,
                }
            ],
        )

        self.assertIn("os", result["imports"])
        self.assertIn("pathlib", result["imports"])

    def test_python_syntax_error_detection(self):
        code = """def greet(name)
    return f"Hello, {name}!"
"""

        result = analyze_code(code, "Python")

        self.assertFalse(result["syntax_valid"])
        self.assertIsNotNone(result["syntax_error"])
        self.assertEqual(result["functions"], [])
        self.assertEqual(result["methods"], [])

    def test_python_method_detection(self):
        code = """class Greeter:
    def greet(self, name):
        return f"Hello, {name}!"
"""

        result = analyze_code(code, "Python")

        self.assertEqual(result["functions"], [])

        self.assertEqual(
            result["methods"],
            [
                {
                    "name": "greet",
                    "line": 2,
                    "parameters": ["self", "name"],
                    "class": "Greeter",
                }
            ],
        )

        self.assertEqual(
            result["classes"],
            [
                {
                    "name": "Greeter",
                    "line": 1,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()